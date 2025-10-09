"""
Debug ChromaDB Endpoints - Para investigar problemas de busca
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from app.application.services.chromadb_service import ChromaDBService

router = APIRouter()


def get_chromadb_service():
    """Retorna o serviço ChromaDB"""
    from app.core.container_instance import container
    return container.chromadb_service()


@router.get("/debug/chroma/chunks/{edital_uuid}", tags=["debug"])
async def debug_chunks(
    edital_uuid: str,
    chromadb: ChromaDBService = Depends(get_chromadb_service)
) -> Dict[str, Any]:
    """
    Debug: Ver todos os chunks de um edital específico.
    """
    try:
        # Buscar todos os chunks deste edital
        result = chromadb.collection.get(
            where={"edital_uuid": edital_uuid}
        )

        chunks_info = []
        for i, (doc_id, document, metadata) in enumerate(zip(
            result.get('ids', []),
            result.get('documents', []),
            result.get('metadatas', [])
        )):
            chunks_info.append({
                "id": doc_id,
                "chunk_index": metadata.get("chunk_index"),
                "total_chunks": metadata.get("total_chunks"),
                "edital_name": metadata.get("edital_name"),
                "text_preview": document[:200] + "..." if len(document) > 200 else document,
                "text_length": len(document),
                "has_cronograma": "CRONOGRAMA" in document.upper() or "cronograma" in document.lower(),
                "has_data": "data" in document.lower(),
                "has_submissao": "submissão" in document.lower() or "submissao" in document.lower()
            })

        return {
            "edital_uuid": edital_uuid,
            "total_chunks": len(chunks_info),
            "chunks": sorted(chunks_info, key=lambda x: x["chunk_index"])
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar chunks: {str(e)}"
        )


@router.get("/debug/chroma/all-chunks", tags=["debug"])
async def debug_all_chunks(
    chromadb: ChromaDBService = Depends(get_chromadb_service)
) -> Dict[str, Any]:
    """
    Debug: Ver TODOS os chunks no ChromaDB (sem filtro).
    """
    try:
        # Buscar TODOS os chunks
        result = chromadb.collection.get()

        chunks_by_edital = {}
        for i, (doc_id, document, metadata) in enumerate(zip(
            result.get('ids', []),
            result.get('documents', []),
            result.get('metadatas', [])
        )):
            edital_uuid = metadata.get("edital_uuid", "unknown")
            if edital_uuid not in chunks_by_edital:
                chunks_by_edital[edital_uuid] = {
                    "edital_name": metadata.get("edital_name", "Unknown"),
                    "chunks": []
                }

            chunks_by_edital[edital_uuid]["chunks"].append({
                "id": doc_id,
                "chunk_index": metadata.get("chunk_index"),
                "text_preview": document[:100] + "..." if len(document) > 100 else document
            })

        return {
            "total_chunks": len(result.get('ids', [])),
            "total_editais": len(chunks_by_edital),
            "editais": chunks_by_edital
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar chunks: {str(e)}"
        )


@router.post("/debug/chroma/test-search", tags=["debug"])
async def test_search(
    query: str,
    edital_uuid: str,
    n_results: int = 10,
    chromadb: ChromaDBService = Depends(get_chromadb_service)
) -> Dict[str, Any]:
    """
    Debug: Testar busca vetorial com query específica.
    """
    try:
        results = await chromadb.search_similar(
            query=query,
            n_results=n_results,
            filter_metadata={"edital_uuid": edital_uuid}
        )

        formatted_results = []
        for chunk in results:
            formatted_results.append({
                "id": chunk["id"],
                "chunk_index": chunk.get("metadata", {}).get("chunk_index"),
                "distance": chunk.get("distance"),
                "text_preview": chunk["text"][:300] + "..." if len(chunk["text"]) > 300 else chunk["text"],
                "has_cronograma": "CRONOGRAMA" in chunk["text"].upper(),
                "has_data": "data" in chunk["text"].lower(),
                "has_submissao": "submissão" in chunk["text"].lower() or "submissao" in chunk["text"].lower()
            })

        return {
            "query": query,
            "edital_uuid": edital_uuid,
            "total_results": len(formatted_results),
            "results": formatted_results
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na busca: {str(e)}"
        )
