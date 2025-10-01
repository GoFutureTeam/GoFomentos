from typing import List, Dict, Any
from openai import OpenAI
from ..core.config import settings
from ..api.services.chroma_service import ChromaService


class EmbeddingGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.chroma_service = ChromaService()
    
    def generate_and_store_embeddings(self, chunks: List[str], edital_uuid: str, pdf_url: str, page_numbers: List[int]) -> None:
        """
        Gera embeddings para chunks de texto e armazena no ChromaDB
        
        Args:
            chunks: Lista de chunks de texto
            edital_uuid: UUID do edital
            pdf_url: URL do PDF
            page_numbers: Lista de números de página correspondentes aos chunks
        """
        # Armazenar diretamente no ChromaDB (que gerará embeddings internamente)
        self.chroma_service.add_chunks(
            chunks=chunks,
            edital_uuid=edital_uuid,
            pdf_url=pdf_url,
            page_numbers=page_numbers
        )
