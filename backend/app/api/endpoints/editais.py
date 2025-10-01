from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from ..models.user import User
from ..models.edital import Edital, EditalCreate, EditalUpdate
from ..services.mongo_service import MongoService
from ..services.chroma_service import ChromaService
from ..services.auth_service import get_current_user
from ...processors.pdf_downloader import PDFDownloader
from ...processors.pdf_extractor import PDFExtractor
from ...processors.data_extractor import DataExtractor
from ...processors.embedding_generator import EmbeddingGenerator
from ...processors.edital_pipeline import process_url
import asyncio
import os

router = APIRouter()

class FetchEditaisRequest(BaseModel):
    url: str

class QueryRequest(BaseModel):
    query: str
    edital_uuid: Optional[str] = None
    n_results: int = 5

async def process_edital(url: str):
    """
    Processa um edital: baixa, extrai texto, extrai dados e gera embeddings
    """
    try:
        # Baixar PDF
        pdf_downloader = PDFDownloader()
        file_path, edital_uuid = await pdf_downloader.download_pdf(url)
        
        try:
            # Extrair texto
            pdf_extractor = PDFExtractor()
            page_texts = pdf_extractor.extract_text_with_pymupdf(file_path)
            
            # Criar chunks
            all_chunks = []
            page_numbers = []
            
            for text, page_num in page_texts:
                chunks = pdf_extractor.chunk_text(text)
                all_chunks.extend(chunks)
                page_numbers.extend([page_num] * len(chunks))
            
            # Extrair dados estruturados
            data_extractor = DataExtractor()
            extracted_data_list = []
            
            for chunk in all_chunks:
                extracted_data = data_extractor.extract_data_from_chunk(chunk, edital_uuid, url)
                extracted_data_list.append(extracted_data)
            
            # Consolidar dados
            consolidated_data = data_extractor.consolidate_data(extracted_data_list)
            
            # Criar edital no MongoDB
            edital_create = EditalCreate(**consolidated_data)
            await MongoService.create_edital(edital_create)
            
            # Gerar embeddings e armazenar no ChromaDB
            embedding_generator = EmbeddingGenerator()
            embedding_generator.generate_and_store_embeddings(
                chunks=all_chunks,
                edital_uuid=edital_uuid,
                pdf_url=url,
                page_numbers=page_numbers
            )
        finally:
            # Limpar arquivo temporário
            if os.path.exists(file_path):
                os.remove(file_path)
        
    except Exception as e:
        print(f"Erro ao processar edital {url}: {e}")
        raise e
@router.post("/post/editais/fetch")
async def post_editais_fetch(request: FetchEditaisRequest, current_user: User = Depends(get_current_user)):
    """
    Executa o pipeline completo solicitado para uma URL de origem e retorna o relatório.
    - Renderiza HTML
    - Extrai candidatos
    - Pré-filtra por prazo
    - Valida via LLM
    - Baixa, extrai texto, chunking e indexa no Chroma
    - Extrai JSON final com map/reduce + gap-filling
    - Upsert no store canônico (Mongo)
    - Gera relatório
    """
    try:
        report = process_url(request.url)
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no pipeline de editais: {str(e)}"
        )

@router.post("/editais/fetch")
async def fetch_editais(request: FetchEditaisRequest, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)):
    """
    Busca e processa editais de uma URL
    """
    try:
        # Obter links de editais
        pdf_downloader = PDFDownloader()
        links = await pdf_downloader.get_edital_links(request.url)
        
        # Processar cada edital em background
        for link in links:
            background_tasks.add_task(process_edital, link)
        
        return {
            "status": "Processing started",
            "links_found": len(links),
            "links": links
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching editais: {str(e)}"
        )

@router.get("/editais", response_model=List[Edital])
async def read_editais(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user)):
    """
    Retorna lista de editais
    """
    return await MongoService.get_editais(skip, limit)

@router.get("/editais/{edital_uuid}", response_model=Edital)
async def read_edital(edital_uuid: str, current_user: User = Depends(get_current_user)):
    """
    Retorna um edital específico
    """
    edital = await MongoService.get_edital(edital_uuid)
    if edital is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Edital not found"
        )
    return edital

@router.put("/editais/{edital_uuid}", response_model=Edital)
async def update_edital(edital_uuid: str, edital_update: EditalUpdate, current_user: User = Depends(get_current_user)):
    """
    Atualiza um edital
    """
    updated_edital = await MongoService.update_edital(edital_uuid, edital_update)
    if updated_edital is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Edital not found"
        )
    return updated_edital

@router.delete("/editais/{edital_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_edital(edital_uuid: str, current_user: User = Depends(get_current_user)):
    """
    Deleta um edital
    """
    result = await MongoService.delete_edital(edital_uuid)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Edital not found"
        )

@router.post("/editais/query")
async def query_editais(request: QueryRequest, current_user: User = Depends(get_current_user)):
    """
    Realiza uma consulta semântica nos editais
    """
    chroma_service = ChromaService()
    results = chroma_service.query_chunks(
        query_text=request.query,
        edital_uuid=request.edital_uuid,
        n_results=request.n_results
    )
    
    return results
