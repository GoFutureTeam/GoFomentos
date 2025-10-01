from typing import List, Dict, Any, Optional
from ...db.chromadb import chromadb_client
from ..models.edital import EditalChunk
import uuid


class ChromaService:
    @staticmethod
    def add_chunks(chunks: List[str], edital_uuid: str, pdf_url: str, page_numbers: List[int]) -> None:
        """
        Adiciona chunks de texto ao ChromaDB
        
        Args:
            chunks: Lista de chunks de texto
            edital_uuid: UUID do edital
            pdf_url: URL do PDF
            page_numbers: Lista de números de página correspondentes aos chunks
        """
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            # Determinar a página com base no índice do chunk
            page_idx = min(i // 5, len(page_numbers) - 1)  # Assumindo ~5 chunks por página
            page = page_numbers[page_idx]
            
            metadatas.append({
                "edital_uuid": edital_uuid,
                "url": pdf_url,
                "pagina": page,
                "chunk_index": i
            })
            
            ids.append(f"{edital_uuid}_{i}")
        
        chromadb_client.add_texts(
            texts=chunks,
            metadatas=metadatas,
            ids=ids
        )
    
    @staticmethod
    def query_chunks(query_text: str, edital_uuid: Optional[str] = None, n_results: int = 5) -> Dict[str, Any]:
        """
        Consulta chunks no ChromaDB
        
        Args:
            query_text: Texto da consulta
            edital_uuid: UUID do edital (opcional)
            n_results: Número de resultados a retornar
            
        Returns:
            Resultados da consulta
        """
        where_filter = None
        if edital_uuid:
            where_filter = {"edital_uuid": edital_uuid}
        
        return chromadb_client.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where_filter
        )
