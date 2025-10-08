"""
Paraíba Gov Scraper Service - Serviço de raspagem do Governo da Paraíba
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


class ParaibaGovScraperService:
    """
    Serviço para raspagem de editais do Governo da Paraíba - SECTIES.
    """

    def __init__(self, max_workers: int = 2):
        self.base_url = "https://paraiba.pb.gov.br/diretas/secretaria-da-ciencia-tecnologia-inovacao-e-ensino-superior/edital"
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
        Converte string de data DD/MM/YYYY ou DD.MM.YYYY para objeto date.

        Args:
            date_str: String da data (ex: "13/03/2025" ou "13.03.2025")

        Returns:
            Optional[date]: Objeto date ou None se falhar
        """
        try:
            # Tentar formato DD/MM/YYYY
            return datetime.strptime(date_str, "%d/%m/%Y").date()
        except:
            try:
                # Tentar formato DD.MM.YYYY
                return datetime.strptime(date_str, "%d.%m.%Y").date()
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
        # Padrões de data comuns em editais
        patterns = [
            r'até\s+(\d{2}[/\.]\d{2}[/\.]\d{4})',  # até 31/03/2025 ou até 31.03.2025
            r'prazo[:\s]+(\d{2}[/\.]\d{2}[/\.]\d{4})',  # prazo: 31/03/2025
            r'(\d{2}[/\.]\d{2}[/\.]\d{4})\s+a\s+(\d{2}[/\.]\d{2}[/\.]\d{4})',  # 12/03/2025 a 31/03/2025
            r'de\s+\d{1,2}\s+a\s+(\d{2}[/\.]\d{2}[/\.]\d{4})',  # de 12 a 31/03/2025
            r'em\s+(\d{2}[/\.]\d{2}[/\.]\d{2,4})',  # em 09/06/25 ou em 09/06/2025
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Pega o último grupo (data final)
                date_str = match.group(match.lastindex) if match.lastindex else match.group(1)
                
                # Normalizar separadores para /
                date_str = date_str.replace('.', '/')
                
                # Se ano com 2 dígitos, converter para 4
                parts = date_str.split('/')
                if len(parts) == 3 and len(parts[2]) == 2:
                    year = int(parts[2])
                    # Assumir 20XX se >= 00
                    parts[2] = f"20{parts[2]}"
                    date_str = '/'.join(parts)
                
                parsed = self._parse_date(date_str)
                if parsed:
                    return parsed

        return None

    async def scrape_paraiba_gov_editais(self, filter_by_date: bool = True) -> List[Dict[str, Any]]:
        """
        Raspa o site do Governo da Paraíba e retorna lista de editais com filtro de data opcional.

        Args:
            filter_by_date: Se True, filtra apenas editais com prazo >= hoje. Se False, retorna todos.

        Returns:
            List[Dict]: Lista de dicionários com informações dos editais
                {
                    'titulo': str,
                    'url': str,  (URL do PDF)
                    'pdf_url': str,  (URL do PDF - mesmo que url)
                    'descricao': str,
                    'data_limite': date (extraída do texto)
                }
        """
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando raspagem do Governo da Paraíba...")

        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(self.base_url, headers=self.headers)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Encontrar todos os links que apontam para PDFs
            all_links = soup.find_all('a', href=True)
            
            editais = []
            today = date.today()
            processed_urls = set()  # Evitar duplicatas

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Encontrados {len(all_links)} links no total")

            for link in all_links:
                try:
                    href = link.get('href', '')
                    
                    # Filtrar apenas links que terminam com .pdf
                    if not href.lower().endswith('.pdf'):
                        continue
                    
                    # Evitar duplicatas
                    if href in processed_urls:
                        continue
                    processed_urls.add(href)
                    
                    # Garantir URL absoluta
                    if href.startswith('http'):
                        pdf_url = href
                    elif href.startswith('/'):
                        pdf_url = f"https://paraiba.pb.gov.br{href}"
                    else:
                        pdf_url = f"https://paraiba.pb.gov.br/{href}"
                    
                    # Extrair título (texto do link ou texto do pai)
                    titulo = link.get_text(strip=True)
                    if not titulo or len(titulo) < 10:
                        # Tentar pegar texto do elemento pai (h3, p, etc.)
                        parent = link.find_parent(['h3', 'h2', 'p', 'div'])
                        if parent:
                            titulo = parent.get_text(strip=True)
                    
                    # Se ainda não tem título, usar nome do arquivo
                    if not titulo or len(titulo) < 10:
                        titulo = href.split('/')[-1].replace('.pdf', '').replace('-', ' ').replace('_', ' ').title()
                    
                    # Extrair data limite do título
                    data_limite = self._extract_deadline_from_text(titulo)
                    
                    # Criar objeto do edital
                    edital_info = {
                        'titulo': titulo,
                        'url': pdf_url,
                        'pdf_url': pdf_url,
                        'descricao': titulo,  # Usar título como descrição
                        'data_limite': data_limite
                    }

                    # Filtrar por data se habilitado
                    if filter_by_date:
                        if data_limite and data_limite >= today:
                            editais.append(edital_info)
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Edital válido: {titulo[:80]}... (prazo: {data_limite})")
                        elif not data_limite:
                            # Se não conseguiu extrair data, incluir mesmo assim (pode ser edital sem prazo definido)
                            editais.append(edital_info)
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Edital sem data identificada (incluído): {titulo[:80]}...")
                        else:
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏭️ Edital expirado: {titulo[:80]}... (prazo: {data_limite})")
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

                if 'application/pdf' not in content_type and not url.lower().endswith('.pdf'):
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
