"""
ChromaDB Visualization Endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any, List

from app.domain.entities.user import User
from app.presentation.api.v1.dependencies import get_current_user
from app.application.services.chromadb_service import ChromaDBService

router = APIRouter()


def get_chromadb_service():
    """Retorna o serviço ChromaDB"""
    from app.core.container_instance import container
    return container.chromadb_service()


@router.get("/chroma/documents", tags=["chroma"])
async def get_chroma_documents(
    chromadb: ChromaDBService = Depends(get_chromadb_service)
) -> Dict[str, Any]:
    """
    Retorna todos os documentos armazenados no ChromaDB.
    Endpoint para o visualizador (sem autenticação para facilitar uso).
    """
    try:
        result = await chromadb.get_all_documents()
        return {
            "status": "success",
            "documents": result.get('documents', []),
            "metadatas": result.get('metadatas', []),
            "ids": result.get('ids', []),
            "total": result.get('total', 0)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar documentos do ChromaDB: {str(e)}"
        )


@router.post("/chroma/clear", tags=["chroma"])
async def clear_chroma_collection(
    current_user: User = Depends(get_current_user),
    chromadb: ChromaDBService = Depends(get_chromadb_service)
) -> Dict[str, Any]:
    """
    Limpa a coleção do ChromaDB.
    """
    try:
        success = await chromadb.clear_collection()
        if success:
            return {"status": "success", "message": "Coleção ChromaDB limpa com sucesso"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao limpar coleção"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao limpar ChromaDB: {str(e)}"
        )


@router.get("/chroma/stats", tags=["chroma"])
async def get_chroma_stats(
    chromadb: ChromaDBService = Depends(get_chromadb_service)
) -> Dict[str, Any]:
    """
    Retorna estatísticas do ChromaDB (sem autenticação para visualizador).
    """
    try:
        stats = await chromadb.get_stats()
        return {
            "status": "success",
            **stats
        }
    except Exception as e:
        return {
            "status": "error",
            "total_documents": 0,
            "total_chunks": 0,
            "collections": [],
            "error": str(e)
        }


@router.get("/chroma/editais", tags=["chroma"])
async def list_editais(
    chromadb: ChromaDBService = Depends(get_chromadb_service)
) -> Dict[str, Any]:
    """
    Lista todos os editais únicos armazenados no ChromaDB.
    Retorna informações agregadas por edital.
    """
    try:
        result = await chromadb.get_all_documents()

        # Agrupar por edital_uuid
        editais_map = {}
        for i, metadata in enumerate(result.get('metadatas', [])):
            edital_uuid = metadata.get('edital_uuid')
            if not edital_uuid:
                continue

            if edital_uuid not in editais_map:
                editais_map[edital_uuid] = {
                    'uuid': edital_uuid,
                    'name': metadata.get('edital_name', 'Sem nome'),
                    'total_chunks': metadata.get('total_chunks', 0),
                    'link': metadata.get('link', ''),
                    'financiador': metadata.get('financiador'),
                    'area_foco': metadata.get('area_foco'),
                    'created_at': metadata.get('created_at'),
                    'chunks_stored': 0
                }

            editais_map[edital_uuid]['chunks_stored'] += 1

        editais_list = list(editais_map.values())

        return {
            "status": "success",
            "total_editais": len(editais_list),
            "editais": editais_list
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar editais: {str(e)}"
        )


@router.post("/chroma/search", tags=["chroma"])
async def semantic_search(
    query: str,
    n_results: int = 10,
    edital_uuid: str = None,
    chromadb: ChromaDBService = Depends(get_chromadb_service)
) -> Dict[str, Any]:
    """
    Busca semântica no ChromaDB.

    Args:
        query: Texto da consulta
        n_results: Número de resultados (padrão: 10)
        edital_uuid: Filtrar por UUID do edital (opcional)
    """
    try:
        filter_metadata = {"edital_uuid": edital_uuid} if edital_uuid else None

        results = await chromadb.search_similar(
            query=query,
            n_results=n_results,
            filter_metadata=filter_metadata
        )

        return {
            "status": "success",
            "query": query,
            "total_results": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na busca semântica: {str(e)}"
        )
