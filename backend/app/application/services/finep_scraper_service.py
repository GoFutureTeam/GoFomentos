"""
FINEP Scraper Service - Serviço de raspagem da FINEP
"""
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import pdfplumber
from io import BytesIO
import asyncio
from concurrent.futures import ProcessPoolExecutor
import re


def _extract_pdf_text_sync(pdf_content: bytes) -> str:
    """
    Função auxiliar síncrona para extrair texto de PDF (executada em ProcessPool).

    Args:
        pdf_content: Conteúdo binário do PDF

    Returns:
        str: Texto extraído
    """
    pdf_bytes = BytesIO(pdf_content)
    texto_completo = ''

    with pdfplumber.open(pdf_bytes) as pdf:
        total_paginas = len(pdf.pages)

        for pagina_num, pagina in enumerate(pdf.pages, 1):
            texto_pagina = pagina.extract_text()
            if texto_pagina:
                texto_completo += f"\n--- Página {pagina_num} ---\n{texto_pagina}\n"

    return texto_completo


class FinepScraperService:
    """
    Serviço para raspagem de chamadas públicas da FINEP.
    """

    def __init__(self, max_workers: int = 2):
        self.base_url = "http://www.finep.gov.br/chamadas-publicas?situacao=aberta"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.executor = ProcessPoolExecutor(max_workers=max_workers)

    def _parse_date(self, date_str: str) -> Optional[date]:
        """
        Converte string de data DD/MM/YYYY para objeto date.

        Args:
            date_str: String da data (ex: "31/12/2025")

        Returns:
            Optional[date]: Objeto date ou None se falhar
        """
        try:
            return datetime.strptime(date_str, "%d/%m/%Y").date()
        except:
            return None

    def _extract_date_from_text(self, text: str) -> Optional[date]:
        """
        Extrai data do texto usando regex.

        Args:
            text: Texto para buscar data

        Returns:
            Optional[date]: Data encontrada ou None
        """
        # Padrões de data comuns
        patterns = [
            r'(\d{2}/\d{2}/\d{4})',  # DD/MM/YYYY
            r'(\d{2}\.\d{2}\.\d{4})',  # DD.MM.YYYY
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Pegar a última data encontrada (geralmente é a data limite)
                date_str = matches[-1].replace('.', '/')
                parsed = self._parse_date(date_str)
                if parsed:
                    return parsed

        return None

    async def scrape_finep_chamadas(self, filter_by_date: bool = True) -> List[Dict[str, Any]]:
        """
        Raspa o site da FINEP e retorna lista de chamadas abertas com filtro de data opcional.

        Args:
            filter_by_date: Se True, filtra apenas chamadas com data >= hoje. Se False, retorna todos.

        Returns:
            List[Dict]: Lista de dicionários com informações das chamadas
                {
                    'titulo': str,
                    'url': str,  (URL da página de detalhes)
                    'data_limite': date (extraída do conteúdo)
                }
        """
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando raspagem da FINEP...")

        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(self.base_url, headers=self.headers)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            chamadas = []
            today = date.today()
            processed_urls = set()  # Evitar duplicatas

            # Buscar todos os links de chamadas (geralmente em h3 ou links específicos)
            # Padrão FINEP: links para /chamadas-publicas/chamadapublica/XXX
            all_links = soup.find_all('a', href=re.compile(r'/chamadas-publicas/chamadapublica/\d+'))

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Encontrados {len(all_links)} links de chamadas")

            for link in all_links:
                try:
                    href = link.get('href', '')
                    
                    # Garantir URL absoluta
                    if href.startswith('http'):
                        detail_url = href
                    elif href.startswith('/'):
                        detail_url = f"http://www.finep.gov.br{href}"
                    else:
                        detail_url = f"http://www.finep.gov.br/{href}"
                    
                    # Evitar duplicatas
                    if detail_url in processed_urls:
                        continue
                    processed_urls.add(detail_url)
                    
                    # Extrair título
                    titulo = link.get_text(strip=True)
                    
                    if not titulo or len(titulo) < 5:
                        continue
                    
                    # Buscar data limite no texto próximo (se disponível na listagem)
                    data_limite = None
                    parent = link.find_parent(['div', 'article', 'section'])
                    if parent:
                        parent_text = parent.get_text()
                        data_limite = self._extract_date_from_text(parent_text)
                    
                    # Criar objeto da chamada
                    chamada_info = {
                        'titulo': titulo,
                        'url': detail_url,
                        'data_limite': data_limite
                    }

                    # Filtrar por data se habilitado
                    if filter_by_date:
                        if data_limite and data_limite >= today:
                            chamadas.append(chamada_info)
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Chamada válida: {titulo[:80]}... (prazo: {data_limite})")
                        elif not data_limite:
                            # Se não conseguiu extrair data na listagem, incluir para verificar na página de detalhes
                            chamadas.append(chamada_info)
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Chamada sem data na listagem (incluída): {titulo[:80]}...")
                        else:
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏭️ Chamada expirada: {titulo[:80]}... (prazo: {data_limite})")
                    else:
                        # Sem filtro: adiciona todos
                        chamadas.append(chamada_info)
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Chamada adicionada (sem filtro de data): {titulo[:80]}...")

                except Exception as e:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Erro ao processar link: {e}")
                    continue

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Total de chamadas válidas: {len(chamadas)}")
            return chamadas

        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ ERRO na raspagem: {e}")
            raise

    async def extract_pdf_links(self, detail_url: str) -> List[str]:
        """
        Acessa a página de detalhes da chamada e extrai todos os links de PDFs.

        Args:
            detail_url: URL da página de detalhes da chamada

        Returns:
            List[str]: Lista de URLs de PDFs encontradas
        """
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Extraindo links de PDFs de: {detail_url}")

        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(detail_url, headers=self.headers)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Buscar todos os links que contenham ".pdf" no href
            pdf_links = []
            all_links = soup.find_all('a', href=True)

            for link in all_links:
                href = link.get('href', '')
                
                # Verificar se ".pdf" está no href
                if '.pdf' in href.lower():
                    # Garantir URL absoluta
                    if href.startswith('http'):
                        pdf_url = href
                    elif href.startswith('/'):
                        pdf_url = f"http://www.finep.gov.br{href}"
                    else:
                        # Concatenar com URL base conforme especificado
                        pdf_url = f"http://www.finep.gov.br/{href}"
                    
                    pdf_links.append(pdf_url)
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📎 PDF encontrado: {pdf_url}")

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Total de PDFs: {len(pdf_links)}")
            return pdf_links

        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro ao extrair links de PDFs: {e}")
            return []

    async def download_and_extract_pdf(self, url: str, max_retries: int = 3) -> Optional[str]:
        """
        Baixa um PDF e extrai o texto com retry automático.

        Args:
            url: URL do PDF
            max_retries: Número máximo de tentativas

        Returns:
            Optional[str]: Texto extraído ou None se falhar
        """
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Baixando PDF: {url}")

        for attempt in range(max_retries):
            try:
                # Timeout mais alto e configurações de retry
                timeout = httpx.Timeout(120.0, connect=30.0)

                async with httpx.AsyncClient(
                    timeout=timeout,
                    follow_redirects=True,
                    limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
                ) as client:
                    response = await client.get(url, headers=self.headers)
                    response.raise_for_status()

                content_type = response.headers.get('Content-Type', '')

                # FINEP: validar se é PDF pelo conteúdo ou pela URL
                is_pdf_url = '.pdf' in url.lower()
                is_pdf_content = 'application/pdf' in content_type
                
                # Verificar se o conteúdo começa com assinatura PDF (%PDF)
                is_pdf_signature = response.content[:4] == b'%PDF'

                if not (is_pdf_content or is_pdf_url or is_pdf_signature):
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Não é um PDF: {content_type}")
                    return None

                # Extrair texto do PDF em processo separado (não bloqueia a API)
                loop = asyncio.get_event_loop()
                texto_completo = await loop.run_in_executor(
                    self.executor,
                    _extract_pdf_text_sync,
                    response.content
                )

                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Texto extraído: {len(texto_completo)} caracteres")
                return texto_completo

            except (httpx.ReadTimeout, httpx.ConnectTimeout) as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # Backoff exponencial: 2s, 4s, 6s
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏳ Timeout (tentativa {attempt + 1}/{max_retries}). Aguardando {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Timeout após {max_retries} tentativas: {e}")
                    return None

            except httpx.RemoteProtocolError as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3  # Backoff maior para erros de protocolo
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏳ Servidor desconectou (tentativa {attempt + 1}/{max_retries}). Aguardando {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Servidor desconectou após {max_retries} tentativas: {e}")
                    return None

            except Exception as e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro ao baixar/processar PDF: {e}")
                return None

        return None

    def shutdown(self):
        """Encerra o executor de processos"""
        self.executor.shutdown(wait=True)
