import requests
import json
import os
import tempfile
import uuid
from typing import List, Dict, Any, Optional, Tuple
from ..core.config import settings


class PDFDownloader:
    @staticmethod
    async def get_edital_links(url: str) -> List[str]:
        """
        Obtém links de editais a partir de uma URL usando a API Jina
        
        Args:
            url: URL da página com links de editais
            
        Returns:
            Lista de URLs de editais
        """
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {settings.JINA_API_KEY}",
            "X-Return-Format": "html",
            "X-Target-Selector": "a.btn[alt='Chamada'][target='_blank']",
            "X-With-Links-Summary": "all"
        }
        
        try:
            response = requests.get(f"https://r.jina.ai/{url}", headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("code") == 200 and data.get("status") == 20000:
                links_data = data.get("data", {}).get("links", [])
                return [link[1] for link in links_data if len(link) > 1]
            else:
                raise Exception(f"Erro ao obter links: {data}")
                
        except Exception as e:
            print(f"Erro ao obter links de editais: {e}")
            raise e
    
    @staticmethod
    async def download_pdf(url: str) -> Tuple[str, str]:
        """
        Baixa um PDF a partir de uma URL
        
        Args:
            url: URL do PDF
            
        Returns:
            Tuple contendo o caminho temporário do arquivo e o UUID gerado
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Gerar UUID para o edital
            edital_uuid = str(uuid.uuid4())
            
            # Criar arquivo temporário
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, f"{edital_uuid}.pdf")
            
            # Salvar PDF
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return file_path, edital_uuid
            
        except Exception as e:
            print(f"Erro ao baixar PDF: {e}")
            raise e
