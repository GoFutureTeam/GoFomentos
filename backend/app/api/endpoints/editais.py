from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from ..models.user import User
from ..models.edital import Edital, EditalCreate, EditalUpdate
from ..services.mongo_service import MongoService
from ..services.chroma_service import ChromaService
from ..services.auth_service import get_current_user
# TODO: Reimplementar processors
# from ...processors.pdf_downloader import PDFDownloader
# from ...processors.pdf_extractor import PDFExtractor
# from ...processors.data_extractor import DataExtractor
# from ...processors.embedding_generator import EmbeddingGenerator
# from ...processors.edital_pipeline import process_url
import asyncio
import os

router = APIRouter()

class FetchEditaisRequest(BaseModel):
    url: str

class QueryRequest(BaseModel):
    query: str
    edital_uuid: Optional[str] = None
    n_results: int = 5

# TODO: Reimplementar após recriar processors
async def process_edital(url: str):
    """
    Processa um edital: baixa, extrai texto, extrai dados e gera embeddings
    DESABILITADO - Aguardando reimplementação dos processors
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Funcionalidade temporariamente desabilitada. Processors em reimplementação."
    )
# TODO: Reimplementar após recriar processors
@router.post("/post/editais/fetch")
async def post_editais_fetch(request: FetchEditaisRequest, current_user: User = Depends(get_current_user)):
    """
    DESABILITADO - Aguardando reimplementação dos processors
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Funcionalidade temporariamente desabilitada. Processors em reimplementação."
    )

# TODO: Reimplementar após recriar processors
@router.post("/editais/fetch")
async def fetch_editais(request: FetchEditaisRequest, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)):
    """
    DESABILITADO - Aguardando reimplementação dos processors
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Funcionalidade temporariamente desabilitada. Processors em reimplementação."
    )

@router.post("/editais", response_model=Edital, status_code=status.HTTP_201_CREATED)
async def create_edital(edital: EditalCreate, current_user: User = Depends(get_current_user)):
    """
    Cria um novo edital manualmente
    
    Campos obrigatórios:
    - apelido_edital: Nome/título do edital
    - link: URL do edital
    
    Campos opcionais (todos os demais):
    - financiador_1, financiador_2: Órgãos financiadores
    - area_foco: Área de foco do edital
    - tipo_proponente: Tipo de proponente aceito
    - empresas_que_podem_submeter: Descrição das empresas elegíveis
    - duracao_min_meses, duracao_max_meses: Duração do projeto
    - valor_min_R$, valor_max_R$: Faixa de valores
    - tipo_recurso: Tipo de recurso (reembolsável, não reembolsável, etc)
    - recepcao_recursos: Forma de recepção dos recursos
    - custeio, capital: Tipos de despesas permitidas
    - contrapartida_min_%, contrapartida_max_%: Percentual de contrapartida
    - tipo_contrapartida: Tipo de contrapartida exigida
    - data_inicial_submissao: Data de abertura (YYYY-MM-DD)
    - data_final_submissao: Data de encerramento (YYYY-MM-DD)
    - data_resultado: Data prevista para resultado (YYYY-MM-DD)
    - descricao_completa: Descrição detalhada do edital
    - origem: Origem/fonte do edital
    - observacoes: Observações adicionais
    - status: Status do edital ('aberto', 'fechado', 'em_breve')
    """
    return await MongoService.create_edital(edital)

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
