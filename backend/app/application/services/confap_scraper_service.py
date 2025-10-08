"""
CONFAP Scraper Service - Serviço de raspagem do CONFAP
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


class ConfapScraperService:
    """
    Serviço para raspagem de editais do CONFAP.
    """

    def __init__(self, max_workers: int = 2):
        self.base_url = "https://confap.org.br/pt/editais/status=em-andamento"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.executor = ProcessPoolExecutor(max_workers=max_workers)

    def _parse_date(self, date_str: str) -> Optional[date]:
        """
        Converte string de data DD/MM/YYYY para objeto date.

        Args:
            date_str: String da data (ex: "17/11/2025")

        Returns:
            Optional[date]: Objeto date ou None se falhar
        """
        try:
            return datetime.strptime(date_str, "%d/%m/%Y").date()
        except:
            return None

    def _extract_deadline_from_text(self, text: str) -> Optional[date]:
        """
        Extrai data de deadline do texto do edital.

        Args:
            text: Texto do título/descrição

        Returns:
            Optional[date]: Data encontrada ou None
        """
        # Padrões de data comuns em editais CONFAP
        patterns = [
            r'Data de Encerramento[:\s]+(\d{2}/\d{2}/\d{4})',  # Data de Encerramento: 17/11/2025
            r'Prazo.*?(\d{2}/\d{2}/\d{4})',  # Prazo para envio: 17/11/2025
            r'até\s+(\d{2}/\d{2}/\d{4})',  # até 17/11/2025
            r'(\d{2}/\d{2}/\d{4})',  # 17/11/2025 (genérico)
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                parsed = self._parse_date(date_str)
                if parsed:
                    return parsed

        return None

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

    async def scrape_confap_editais(self, filter_by_date: bool = True) -> List[Dict[str, Any]]:
        """
        Raspa o site do CONFAP e retorna lista de editais com filtro de data opcional.

        Args:
            filter_by_date: Se True, filtra apenas editais com ano >= ano atual. Se False, retorna todos.

        Returns:
            List[Dict]: Lista de dicionários com informações dos editais
                {
                    'titulo': str,
                    'url': str,  (URL da página de detalhes)
                    'status': str,
                    'ano': int (extraído do título)
                }
        """
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando raspagem do CONFAP...")

        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(self.base_url, headers=self.headers)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Encontrar todos os editais (links "Ver detalhes")
            editais = []
            current_year = date.today().year
            processed_urls = set()  # Evitar duplicatas

            # Buscar todos os links "Ver detalhes"
            detail_links = soup.find_all('a', href=True, string=re.compile(r'Ver detalhes', re.IGNORECASE))

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Encontrados {len(detail_links)} editais")

            for link in detail_links:
                try:
                    href = link.get('href', '')
                    
                    # Garantir URL absoluta
                    if href.startswith('http'):
                        detail_url = href
                    elif href.startswith('/'):
                        detail_url = f"https://confap.org.br{href}"
                    else:
                        detail_url = f"https://confap.org.br/{href}"
                    
                    # Evitar duplicatas
                    if detail_url in processed_urls:
                        continue
                    processed_urls.add(detail_url)
                    
                    # Buscar título (geralmente está em um h2 ou h3 próximo)
                    titulo = None
                    parent = link.find_parent(['div', 'article', 'section'])
                    if parent:
                        titulo_tag = parent.find(['h2', 'h3', 'h4'])
                        if titulo_tag:
                            titulo = titulo_tag.get_text(strip=True)
                    
                    # Se não encontrou título, usar texto do link
                    if not titulo:
                        titulo = link.get_text(strip=True)
                    
                    # Buscar status (geralmente está próximo ao título)
                    status = "Em andamento"  # Padrão, já que estamos na página de editais em andamento
                    if parent:
                        status_tag = parent.find(string=re.compile(r'Em andamento|Encerrado|Aberto', re.IGNORECASE))
                        if status_tag:
                            status = status_tag.strip()
                    
                    # Extrair ano do título
                    ano = self._extract_year_from_text(titulo) if titulo else None
                    
                    # Criar objeto do edital
                    edital_info = {
                        'titulo': titulo or "Sem título",
                        'url': detail_url,
                        'status': status,
                        'ano': ano
                    }

                    # Filtrar por data se habilitado
                    if filter_by_date:
                        if ano and ano >= current_year:
                            editais.append(edital_info)
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Edital válido: {titulo[:80]}... (ano: {ano})")
                        elif not ano:
                            # Se não conseguiu extrair ano, incluir mesmo assim
                            editais.append(edital_info)
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Edital sem ano identificado (incluído): {titulo[:80]}...")
                        else:
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏭️ Edital de ano anterior: {titulo[:80]}... (ano: {ano})")
                    else:
                        # Sem filtro: adiciona todos
                        editais.append(edital_info)
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Edital adicionado (sem filtro de data): {titulo[:80]}...")

                except Exception as e:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Erro ao processar link: {e}")
                    continue

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Total de editais válidos: {len(editais)}")
            return editais

        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ ERRO na raspagem: {e}")
            raise

    async def extract_download_links(self, detail_url: str) -> List[str]:
        """
        Acessa a página de detalhes do edital e extrai todos os links de download.

        Args:
            detail_url: URL da página de detalhes do edital

        Returns:
            List[str]: Lista de URLs de download encontradas
        """
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Extraindo links de download de: {detail_url}")

        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(detail_url, headers=self.headers)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Buscar todos os links que contenham "download" no href
            download_links = []
            all_links = soup.find_all('a', href=True)

            for link in all_links:
                href = link.get('href', '')
                
                # Verificar se "download" está no href
                if 'download' in href.lower():
                    # Garantir URL absoluta
                    if href.startswith('http'):
                        download_url = href
                    elif href.startswith('/'):
                        download_url = f"https://confap.org.br{href}"
                    else:
                        download_url = f"https://confap.org.br/{href}"
                    
                    download_links.append(download_url)
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📎 Link de download encontrado: {download_url}")

            # Se não encontrou links com "download" no href, buscar links para PDFs
            if not download_links:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Nenhum link com 'download' encontrado. Buscando PDFs...")
                
                for link in all_links:
                    href = link.get('href', '')
                    if href.lower().endswith('.pdf'):
                        # Garantir URL absoluta
                        if href.startswith('http'):
                            download_url = href
                        elif href.startswith('/'):
                            download_url = f"https://confap.org.br{href}"
                        else:
                            download_url = f"https://confap.org.br/{href}"
                        
                        download_links.append(download_url)
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📎 PDF encontrado: {download_url}")

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Total de links de download: {len(download_links)}")
            return download_links

        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro ao extrair links de download: {e}")
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

                # CONFAP: links com "download" retornam PDFs mesmo sem Content-Type correto
                # Validar se é PDF pelo conteúdo ou pela URL
                is_pdf_url = 'download' in url.lower() or url.lower().endswith('.pdf')
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
