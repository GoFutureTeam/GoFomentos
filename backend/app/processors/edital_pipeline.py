import re
import io
import os
import hashlib
import uuid
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse, parse_qsl, urlencode

from dateutil import parser as dateparser
import pytz

import pdfplumber
from pdf2image import convert_from_bytes
import pytesseract

from ..core.config import settings
from ..db.chromadb import chromadb_client
from ..api.services.mongo_service import MongoService  # fallback access if needed
from ..api.services.mongo_canon_service import MongoCanonService

from openai import OpenAI

TIMEZONE = pytz.timezone("America/Fortaleza")
CHROMA_COLLECTION_NAME = "editais"  # as per spec
UUID_NAMESPACE_EDITAIS = uuid.UUID(settings.UUID_NAMESPACE_EDITAIS)
USER_AGENT = "GoFomentosBot/1.0 (+https://localhost)"
RATE_LIMIT_SLEEP = 0.6  # ~1-2 req/s

# Helper: now strings

def now_iso() -> str:
    return datetime.now(TIMEZONE).isoformat()


def today_date() -> str:
    return datetime.now(TIMEZONE).date().isoformat()


# URL normalization

def _strip_tracking(u: str) -> str:
    parsed = urlparse(u)
    # remove utm_* and anchors
    query = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True) if not k.lower().startswith("utm_")]
    new_query = urlencode(query, doseq=True)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, ""))


def render_html(url: str) -> str:
    headers = {"User-Agent": USER_AGENT}
    # Try best-effort JS rendering if requests_html is available
    try:
        from requests_html import HTMLSession  # type: ignore
        session = HTMLSession()
        r = session.get(url, headers=headers, timeout=30)
        time.sleep(RATE_LIMIT_SLEEP)
        try:
            r.html.render(timeout=30, sleep=1)
            return r.html.html or r.text
        except Exception:
            return r.text
    except Exception:
        # Fallback: plain requests
        r = requests.get(url, headers=headers, timeout=30)
        time.sleep(RATE_LIMIT_SLEEP)
        return r.text


def extract_candidate_links(source_url: str, html: str) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "lxml")
    candidates = []

    def score(text: str) -> int:
        t = text.lower()
        pos = ["edital", "chamada", "seleção pública", "chamadas públicas", "portaria"]
        neg = ["resultado", "homologação", "errata", "retificação", "encerrado"]
        s = 0
        if any(p in t for p in pos):
            s += 2
        if any(n in t for n in neg):
            s -= 2
        return s

    # anchors
    for a in soup.find_all("a"):
        href = a.get("href")
        if not href:
            continue
        abs_url = _strip_tracking(urljoin(source_url, href))
        text = (a.get_text(strip=True) or "")
        s = score(text + " " + abs_url)
        candidates.append({
            "url": abs_url,
            "text": text,
            "score": s
        })

    # buttons with onclick
    for btn in soup.find_all(["button", "input"]):
        onclick = btn.get("onclick")
        if onclick and "http" in onclick:
            m = re.search(r"https?://[^'\"]+", onclick)
            if m:
                abs_url = _strip_tracking(urljoin(source_url, m.group(0)))
                text = (btn.get_text(strip=True) or btn.get("value", ""))
                s = score(text + " " + abs_url)
                candidates.append({"url": abs_url, "text": text, "score": s})

    # deduplicate by url keeping max score
    dedup: Dict[str, Dict[str, Any]] = {}
    for c in candidates:
        u = c["url"]
        if u not in dedup or c["score"] > dedup[u]["score"]:
            dedup[u] = c

    # type detection by extension
    def detect_type(u: str) -> str:
        path = urlparse(u).path.lower()
        if path.endswith(".pdf"):
            return "pdf"
        if path.endswith(".html") or path.endswith(".htm"):
            return "html"
        if path.endswith(".doc") or path.endswith(".docx"):
            return "docx"
        if path.endswith(".zip"):
            return "zip"
        return "html"

    out = []
    for u, c in dedup.items():
        out.append({"download_url": u, "source_url": source_url, "type": detect_type(u), "score": c["score"]})
    # prioritize pdf and high score
    out.sort(key=lambda x: (x["type"] != "pdf", -x["score"]))
    return out


DATE_PATTERNS = [
    # dd/mm/yyyy or dd-mm-yyyy
    r"\b(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})\b",
    # yyyy-mm-dd
    r"\b(\d{4})-(\d{2})-(\d{2})\b",
]


def _extract_dates(text: str) -> List[datetime]:
    dates: List[datetime] = []
    for pat in DATE_PATTERNS:
        for m in re.finditer(pat, text):
            try:
                dt = dateparser.parse(m.group(0), dayfirst=True)
                if dt:
                    dates.append(dt)
            except Exception:
                pass
    return dates


def quick_deadline_filter(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    today = datetime.now(TIMEZONE).date()
    headers = {"User-Agent": USER_AGENT}
    approved: List[Dict[str, Any]] = []
    for c in candidates:
        u = c["download_url"]
        try:
            if c["type"] == "html":
                r = requests.get(u, headers=headers, timeout=20)
                time.sleep(RATE_LIMIT_SLEEP)
                text = r.text
            elif c["type"] == "pdf":
                r = requests.get(u, headers=headers, timeout=30)
                time.sleep(RATE_LIMIT_SLEEP)
                # light pass: first page text
                with pdfplumber.open(io.BytesIO(r.content)) as pdf:
                    first = pdf.pages[0] if pdf.pages else None
                    text = first.extract_text() if first else ""
            else:
                # skip heavy types in quick pass
                continue
            dts = _extract_dates(text)
            max_date = None
            for dt in dts:
                try:
                    d = dt.date()
                    if (max_date is None) or (d > max_date):
                        max_date = d
                except Exception:
                    continue
            if max_date and max_date >= today:
                approved.append(c)
        except Exception:
            # ignore failures here; they can be validated later
            pass
    return approved


def llm_validate_links_html(html_snippet: str, current_iso: str, current_date: str, client: OpenAI) -> List[str]:
    prompt = (
        "Você receberá um conteúdo HTML entre <conteudo>…</conteudo>.\n"
        f"Considere a data/hora de referência (timezone America/Fortaleza) como: {current_iso}\n"
        f"Objetivo: retornar apenas as URLs de editais cujo prazo final de submissão seja >= {current_date}.\n\n"
        "Regras:\n"
        "- Saída: uma URL válida por linha. \n"
        "- Se nenhuma for válida, responda exatamente: Nenhum edital aberto encontrado.\n"
        "- Não invente URLs. Use apenas as URLs presentes no conteúdo.\n"
        "- Se não houver datas explícitas sobre prazo de submissão, responda: Nenhum edital aberto encontrado.\n\n"
        "<conteudo>\n" + html_snippet + "\n</conteudo>\n"
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.0,
        messages=[
            {"role": "system", "content": "Papel: filtro de links de editais abertos."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=512,
    )
    content = (resp.choices[0].message.content or "").strip()
    if content == "Nenhum edital aberto encontrado.":
        return []
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    # return only valid URLs
    return [l for l in lines if l.startswith("http://") or l.startswith("https://")]


def download_bytes(url: str) -> Tuple[bytes, str, str]:
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(url, headers=headers, timeout=60)
    time.sleep(RATE_LIMIT_SLEEP)
    r.raise_for_status()
    data = r.content
    sha = hashlib.sha256(data).hexdigest()
    mime = r.headers.get("Content-Type", "application/octet-stream").split(";")[0]
    return data, sha, mime


def extract_pdf_text_pages(data: bytes) -> List[Tuple[int, str]]:
    pages: List[Tuple[int, str]] = []
    try:
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for i, p in enumerate(pdf.pages):
                txt = p.extract_text() or ""
                pages.append((i + 1, txt))
    except Exception:
        pages = []
    if not pages or all(not t.strip() for _, t in pages):
        # OCR fallback
        images = convert_from_bytes(data)
        pages = []
        for i, img in enumerate(images):
            txt = pytesseract.image_to_string(img, lang="por+eng")
            pages.append((i + 1, txt))
    return pages


def extract_html_text(data: bytes) -> str:
    html = data.decode(errors="ignore")
    soup = BeautifulSoup(html, "lxml")
    # remove script/style
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()
    text = soup.get_text("\n")
    return text


def chunk_text_with_overlap(page_texts: List[Tuple[int, str]], target_size: int = 1000, overlap: int = 120) -> Tuple[List[str], List[str]]:
    chunks: List[str] = []
    page_spans: List[str] = []
    buf = ""
    span_pages: List[int] = []
    for page_num, text in page_texts:
        cursor = 0
        while cursor < len(text):
            remaining = text[cursor:cursor + target_size]
            if not remaining:
                break
            if not buf:
                span_pages = [page_num]
            buf += remaining
            cursor += target_size - overlap
            if len(buf) >= target_size:
                chunks.append(buf[:target_size])
                page_spans.append(f"{span_pages[0]}-{page_num}")
                buf = buf[target_size - overlap:]
        # if page ended and buffer has content, continue to next page (span continues)
        if span_pages and span_pages[-1] != page_num:
            span_pages.append(page_num)
    if buf:
        chunks.append(buf)
        if span_pages:
            page_spans.append(f"{span_pages[0]}-{span_pages[-1]}")
        else:
            page_spans.append("")
    return chunks, page_spans


def index_chunks_in_chroma(edital_id: str, download_url: str, source_url: str, content_sha256: str, mime_type: str, language: str, chunks: List[str], page_spans: List[str]) -> List[str]:
    created_at = now_iso()
    ids: List[str] = []
    metadatas: List[Dict[str, Any]] = []
    for i, (chunk, span) in enumerate(zip(chunks, page_spans), start=1):
        chunk_id = f"{edital_id}#{i}"
        ids.append(chunk_id)
        metadatas.append({
            "edital_id": edital_id,
            "chunk_id": chunk_id,
            "seq": i,
            "source_url": source_url,
            "download_url": download_url,
            "content_sha256": content_sha256,
            "page_spans": span or "",
            "mime_type": mime_type if mime_type in ("application/pdf", "text/html") else ("application/pdf" if mime_type.endswith("pdf") else "text/html"),
            "language": language,
            "created_at": created_at,
        })
    chromadb_client.add_texts(texts=chunks, metadatas=metadatas, ids=ids)
    return ids


SCHEMA_FIELDS = [
    "apelido_edital",
    "financiador_1",
    "financiador_2",
    "area_foco",
    "tipo_proponente",
    "empresas_que_podem_submeter",
    "duracao_min_meses",
    "duracao_max_meses",
    "valor_min_R$",
    "valor_max_R$",
    "tipo_recurso",
    "recepcao_recursos",
    "custeio",
    "capital",
    "contrapartida_min_%",
    "contrapartida_max_%",
    "tipo_contrapartida",
    "data_inicial_submissao",
    "data_final_submissao",
    "data_resultado",
    "descricao_completa",
    "origem",
    "link",
    "observacoes",
]


def map_extract_chunk(client: OpenAI, edital_id: str, chunk_id: str, seq: int, page_spans: str, texto: str) -> Dict[str, Any]:
    schema_obj = {
        "apelido_edital": None,
        "financiador_1": None,
        "financiador_2": None,
        "area_foco": None,
        "tipo_proponente": None,
        "empresas_que_podem_submeter": None,
        "duracao_min_meses": None,
        "duracao_max_meses": None,
        "valor_min_R$": None,
        "valor_max_R$": None,
        "tipo_recurso": None,
        "recepcao_recursos": None,
        "custeio": None,
        "capital": None,
        "contrapartida_min_%": None,
        "contrapartida_max_%": None,
        "tipo_contrapartida": None,
        "data_inicial_submissao": None,
        "data_final_submissao": None,
        "data_resultado": None,
        "descricao_completa": None,
        "origem": None,
        "link": None,
        "observacoes": None,
        "confidence": {},
        "provenance": {"chunk_id": chunk_id, "page_spans": page_spans},
    }

    prompt = (
        "Papel: extrator estrito de informações.\n\n"
        "Instruções:\n"
        "- Você receberá o texto de um chunk de um edital, com metadados { \"edital_id\": ..., \"chunk_id\": ..., \"seq\": ..., \"page_spans\": ... }.\n"
        "- Retorne SOMENTE um objeto JSON válido conforme o schema abaixo.\n"
        "- Para qualquer campo sem evidência explícita neste chunk, retorne null.\n"
        "- Não use conhecimento externo.\n"
        "- Para datas, normalize para \"YYYY-MM-DD\" se a data for completa; caso contrário, retorne null.\n"
        "- Para moeda (R$) e percentuais, normalize para números (ex.: \"R$ 1.234,56\" → 1234.56; \"10%\" → 10.0).\n"
        "- Para booleans (custeio/capital), retorne true/false ou null se não houver evidência.\n"
        "- Inclua um objeto \"confidence\" com valores 0.0–1.0 por campo.\n"
        "- Inclua \"provenance\": { \"chunk_id\": \"...\", \"page_spans\": \"...\" }.\n\n"
        "Schema dos dados:\n"
        "{\n"
        "  \"apelido_edital\": \"STRING\",\n  \"financiador_1\": \"STRING\",\n  \"financiador_2\": \"STRING\",\n  \"area_foco\": \"STRING\",\n  \"tipo_proponente\": \"STRING\",\n  \"empresas_que_podem_submeter\": \"STRING\",\n  \"duracao_min_meses\": \"NUMBER\",\n  \"duracao_max_meses\": \"NUMBER\",\n  \"valor_min_R$\": \"NUMBER\",\n  \"valor_max_R$\": \"NUMBER\",\n  \"tipo_recurso\": \"STRING\",\n  \"recepcao_recursos\": \"STRING\",\n  \"custeio\": \"BOOLEAN\",\n  \"capital\": \"BOOLEAN\",\n  \"contrapartida_min_%\": \"NUMBER\",\n  \"contrapartida_max_%\": \"NUMBER\",\n  \"tipo_contrapartida\": \"STRING\",\n  \"data_inicial_submissao\": \"YYYY-MM-DD\",\n  \"data_final_submissao\": \"YYYY-MM-DD\",\n  \"data_resultado\": \"YYYY-MM-DD\",\n  \"descricao_completa\": \"STRING\",\n  \"origem\": \"STRING\",\n  \"link\": \"STRING\",\n  \"observacoes\": \"STRING\"\n"
        "}\n\n"
        "Entrada:\n"
        f"{{\n  \"edital_id\": \"{edital_id}\",\n  \"chunk_id\": \"{chunk_id}\",\n  \"seq\": {seq},\n  \"page_spans\": \"{page_spans}\",\n  \"texto\": \"" + texto.replace("\n", " ").replace("\"", "\\\"")[:6000] + "\"\n}"
    )

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.0,
        messages=[
            {"role": "system", "content": "Você é um assistente que retorna somente JSON válido."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1200,
    )
    content = (resp.choices[0].message.content or "").strip()
    try:
        obj = json.loads(content)
        # ensure required keys exist
        for k in SCHEMA_FIELDS:
            obj.setdefault(k, None)
        obj.setdefault("confidence", {})
        obj.setdefault("provenance", {"chunk_id": chunk_id, "page_spans": page_spans})
        return obj
    except Exception:
        return schema_obj


def reduce_merge(acc: Dict[str, Any], incoming: Dict[str, Any], today_str: str) -> Dict[str, Any]:
    # initialize
    if not acc:
        acc = {k: None for k in SCHEMA_FIELDS}
        acc["confidence"] = {}
        acc["provenance_map"] = {}
    for k in SCHEMA_FIELDS:
        v_new = incoming.get(k)
        conf_new = (incoming.get("confidence") or {}).get(k, 0.0)
        if acc.get(k) is None and v_new not in (None, ""):
            acc[k] = v_new
            acc["confidence"][k] = conf_new
            acc["provenance_map"][k] = incoming.get("provenance")
        elif v_new not in (None, ""):
            # conflict -> choose higher confidence
            conf_old = acc.get("confidence", {}).get(k, 0.0)
            if conf_new > conf_old:
                acc[k] = v_new
                acc["confidence"][k] = conf_new
                acc["provenance_map"][k] = incoming.get("provenance")
    # validity constraints for dates and numbers could be post-validated
    return acc


def gap_fill(client: OpenAI, edital_id: str, missing_fields: List[str]) -> Dict[str, Any]:
    if not missing_fields:
        return {}
    # retrieve
    res = chromadb_client.query(query_texts=["Preencher campos faltantes"], n_results=5, where={"edital_id": edital_id})
    documents = res.get("documents", [[]])[0]
    metadatas = res.get("metadatas", [[]])[0]
    # Build snippets with references
    snippets = []
    for doc, meta in zip(documents, metadatas):
        ref = f"[{meta.get('chunk_id','')}]({meta.get('page_spans','')})"
        snippets.append(ref + "\n" + (doc or ""))
    schema_incomplete = {f: None for f in missing_fields}
    prompt = (
        "Papel: completador de campos faltantes com base em evidências.\n"
        "Você receberá:\n- O schema dos campos que AINDA estão nulos.\n- Um conjunto de trechos recuperados via retriever, todos do MESMO edital (mesmo edital_id).\n"
        "Regras:\n- Retorne SOMENTE um objeto JSON com os campos faltantes do schema e seus valores normalizados.\n- Se continuar sem evidência suficiente, retorne null no campo.\n- Não use conhecimento externo; apenas os trechos fornecidos.\n- Normalize datas para \"YYYY-MM-DD\"; BRL em número; % em número; booleans true/false.\n\n"
        "Schema-incompleto:\n" + json.dumps(schema_incomplete, ensure_ascii=False) + "\n\n"
        "Trechos:\n" + "\n\n".join(snippets) + "\n"
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.0,
        messages=[
            {"role": "system", "content": "Você retorna somente JSON válido."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=800,
    )
    content = (resp.choices[0].message.content or "").strip()
    try:
        obj = json.loads(content)
        return obj
    except Exception:
        return {f: None for f in missing_fields}


def compute_status(final_date: Optional[str], start_date: Optional[str], today_str: str) -> str:
    if final_date:
        try:
            d_end = dateparser.parse(final_date).date()
            today = dateparser.parse(today_str).date()
            if start_date:
                d_start = dateparser.parse(start_date).date()
                if d_start <= today <= d_end:
                    return "aberto"
            if d_end >= today:
                return "aberto"
            else:
                return "encerrado"
        except Exception:
            return "incerto"
    return "incerto"


def make_apelido_if_empty(download_url: str) -> str:
    parsed = urlparse(download_url)
    domain = parsed.netloc.split(":")[0]
    yr = datetime.now(TIMEZONE).year
    short = hashlib.sha1(download_url.encode()).hexdigest()[:6]
    return f"{domain}-{yr}-{short}"


def process_url(input_url: str) -> Dict[str, Any]:
    report = {
        "source_url": input_url,
        "candidatos_total": 0,
        "candidatos_aprovados_pre": 0,
        "candidatos_aprovados_llm": 0,
        "editais_processados": {"novos": 0, "atualizados": 0, "pulados": 0},
        "chunks_total": 0,
        "por_edital": [],
        "erros": [],
    }
    CURRENT_ISO = now_iso()
    CURRENT_ISO_DATE = today_date()

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    # 1) Render HTML
    html = render_html(input_url)

    # 2) Extract candidate links
    candidates = extract_candidate_links(input_url, html)
    report["candidatos_total"] = len(candidates)

    # 3) Deterministic pre-filter by deadline
    pre = quick_deadline_filter(candidates)
    report["candidatos_aprovados_pre"] = len(pre)

    # 4) LLM validation per candidate (batch by concatenating normalized HTML snippets)
    approved_urls: List[str] = []
    for c in pre:
        try:
            # fetch content for LLM context (html only)
            if c["type"] == "html":
                r = requests.get(c["download_url"], headers={"User-Agent": USER_AGENT}, timeout=30)
                time.sleep(RATE_LIMIT_SLEEP)
                snippet = r.text[:20000]
            else:
                snippet = f"<a href=\"{c['download_url']}\">PDF do edital</a>"
            urls = llm_validate_links_html(snippet, CURRENT_ISO, CURRENT_ISO_DATE, client)
            for u in urls:
                if u == c["download_url"]:
                    approved_urls.append(u)
        except Exception as e:
            report["erros"].append(f"LLM validação falhou para {c['download_url']}: {e}")
    approved_urls = list(dict.fromkeys(approved_urls))
    report["candidatos_aprovados_llm"] = len(approved_urls)

    # 5..10) For each approved download_url, process
    for download_url in approved_urls:
        try:
            edital_id = str(uuid.uuid5(UUID_NAMESPACE_EDITAIS, download_url))
            data, content_sha256, mime = download_bytes(download_url)

            # Load existing canonical record
            existing = MongoCanonService.get_by_edital_id(edital_id)
            if existing and existing.get("content_sha256") == content_sha256:
                # idempotent skip heavy work
                report["editais_processados"]["pulados"] += 1
                report["por_edital"].append({"edital_id": edital_id, "status": existing.get("status"), "skipped": True})
                # update last_seen_at
                MongoCanonService.touch_last_seen(edital_id)
                continue

            # 6) Extract content
            page_texts: List[Tuple[int, str]] = []
            language = "pt-BR"
            if mime == "application/pdf" or download_url.lower().endswith(".pdf"):
                page_texts = extract_pdf_text_pages(data)
            else:
                text = extract_html_text(data)
                page_texts = [(1, text)]
                mime = "text/html"

            # 7) Chunking
            chunks, spans = chunk_text_with_overlap(page_texts, target_size=1000, overlap=120)
            chunk_ids = index_chunks_in_chroma(
                edital_id=edital_id,
                download_url=download_url,
                source_url=input_url,
                content_sha256=content_sha256,
                mime_type=mime,
                language=language,
                chunks=chunks,
                page_spans=spans,
            )
            report["chunks_total"] += len(chunk_ids)

            # 8) Map extraction per chunk
            acc: Dict[str, Any] = {}
            for seq, (chunk_text, span, chunk_id) in enumerate(zip(chunks, spans, chunk_ids), start=1):
                m = map_extract_chunk(client, edital_id, chunk_id, seq, span, chunk_text)
                acc = reduce_merge(acc, m, CURRENT_ISO_DATE)

            # 9) Gap-filling
            missing = [k for k in SCHEMA_FIELDS if acc.get(k) in (None, "")]
            if missing:
                filled = gap_fill(client, edital_id, missing)
                for k, v in filled.items():
                    if acc.get(k) in (None, "") and v not in (None, ""):
                        acc[k] = v
                        acc.setdefault("provenance_map", {})[k] = {"chunk_id": "retriever", "page_spans": ""}

            # Normalize fields and compute status
            final_date = acc.get("data_final_submissao")
            start_date = acc.get("data_inicial_submissao")
            status = compute_status(final_date, start_date, CURRENT_ISO_DATE)
            if not acc.get("apelido_edital"):
                acc["apelido_edital"] = make_apelido_if_empty(download_url)
            acc["origem"] = acc.get("origem") or input_url
            acc["link"] = download_url

            # 10) Persist canonical record (upsert)
            is_update = existing is not None
            MongoCanonService.upsert_canonical(
                edital_id=edital_id,
                json_final=acc,
                status=status,
                source_url=input_url,
                download_url=download_url,
                content_sha256=content_sha256,
                chunk_ids=chunk_ids,
                provenance=acc.get("provenance_map", {}),
                is_update=is_update,
            )
            if is_update:
                report["editais_processados"]["atualizados"] += 1
            else:
                report["editais_processados"]["novos"] += 1
            report["por_edital"].append({
                "edital_id": edital_id,
                "status": status,
                "chunks": len(chunk_ids),
                "faltantes": [k for k in SCHEMA_FIELDS if acc.get(k) in (None, "")],
            })
        except Exception as e:
            report["erros"].append(f"Erro ao processar {download_url}: {e}")

    return {
        "CURRENT_ISO": CURRENT_ISO,
        "CURRENT_ISO_DATE": CURRENT_ISO_DATE,
        "relatorio": report,
    }
