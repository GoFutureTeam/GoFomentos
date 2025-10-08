"""
CAPES Scraper Service - Serviço de raspagem da CAPES
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


class CapesScraperService:
    """
    Serviço para raspagem de chamadas públicas da CAPES.
    """

    def __init__(self, max_workers: int = 2):
        self.base_url = "https://www.gov.br/capes/pt-br/acesso-a-informacao/licitacoes-e-contratos/chamadas-publicas/chamadas"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.executor = ProcessPoolExecutor(max_workers=max_workers)

    def _extract_year_from_text(self, text: str) -> Optional[int]:
        """
        Extrai ano do texto (título ou descrição).

        Args:
            text: Texto para buscar o ano

        Returns:
            Optional[int]: Ano encontrado ou None
        """
        # Buscar padrões de ano (2024, 2025, etc.)
        match = re.search(r'\b(20\d{2})\b', text)
        if match:
            return int(match.group(1))
        return None

    async def scrape_capes_chamadas(self, filter_by_date: bool = True) -> List[Dict[str, Any]]:
        """
        Raspa o site da CAPES e retorna lista de chamadas públicas com filtro de data opcional.

        Args:
            filter_by_date: Se True, filtra apenas chamadas com ano >= ano atual. Se False, retorna todos.

        Returns:
            List[Dict]: Lista de dicionários com informações das chamadas
                {
                    'titulo': str,
                    'ano': int,
                    'pdf_urls': List[str]  (URLs dos PDFs encontrados)
                }
        """
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando raspagem da CAPES...")

        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(self.base_url, headers=self.headers)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            chamadas = []
            current_year = date.today().year
            processed_sections = set()  # Evitar duplicatas

            # Buscar todas as seções de chamadas (geralmente h3 com "Chamadas públicas XXXX")
            sections = soup.find_all(['h3', 'h2'], string=re.compile(r'Chamadas públicas \d{4}', re.IGNORECASE))

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Encontradas {len(sections)} seções de chamadas")

            for section in sections:
                try:
                    # Extrair ano do título da seção
                    section_text = section.get_text(strip=True)
                    ano = self._extract_year_from_text(section_text)

                    if not ano:
                        continue

                    # Filtrar por ano se habilitado
                    if filter_by_date and ano < current_year:
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏭️ Seção de ano anterior: {section_text}")
                        continue

                    # Evitar processar a mesma seção duas vezes
                    if section_text in processed_sections:
                        continue
                    processed_sections.add(section_text)

                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📋 Processando seção: {section_text}")

                    # Buscar o próximo elemento que contém os links (geralmente um div ou p)
                    content_container = section.find_next_sibling()
                    
                    if not content_container:
                        # Tentar buscar o parent e depois o próximo sibling
                        parent = section.find_parent(['div', 'section'])
                        if parent:
                            content_container = parent

                    if not content_container:
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Não encontrou container de conteúdo")
                        continue

                    # Buscar todos os links que contêm "-pdf" no href dentro desta seção
                    pdf_links = []
                    all_links = content_container.find_all('a', href=True)

                    for link in all_links:
                        href = link.get('href', '')
                        
                        # Verificar se "-pdf" está no href
                        if '-pdf' in href.lower() or href.lower().endswith('.pdf'):
                            # Garantir URL absoluta
                            if href.startswith('http'):
                                pdf_url = href
                            elif href.startswith('/'):
                                pdf_url = f"https://www.gov.br{href}"
                            else:
                                pdf_url = f"https://www.gov.br/capes/pt-br/acesso-a-informacao/licitacoes-e-contratos/chamadas-publicas/{href}"
                            
                            pdf_links.append(pdf_url)
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📎 PDF encontrado: {pdf_url}")

                    if pdf_links:
                        chamada_info = {
                            'titulo': section_text,
                            'ano': ano,
                            'pdf_urls': pdf_links
                        }
                        chamadas.append(chamada_info)
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Chamada válida: {section_text} ({len(pdf_links)} PDFs)")
                    else:
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Nenhum PDF encontrado nesta seção")

                except Exception as e:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Erro ao processar seção: {e}")
                    continue

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Total de chamadas válidas: {len(chamadas)}")
            return chamadas

        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ ERRO na raspagem: {e}")
            raise

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

                # CAPES: links com "-pdf" retornam PDFs mesmo sem Content-Type correto
                # Validar se é PDF pelo conteúdo ou pela URL
                is_pdf_url = '-pdf' in url.lower() or url.lower().endswith('.pdf')
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
