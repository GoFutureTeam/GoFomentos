from fastapi import APIRouter, Depends, HTTPException, status
from ...db.mongodb import mongodb
from ...db.chromadb import chromadb_client

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Verifica o status da API e conexões com bancos de dados
    """
    mongo_status = "OK"
    chroma_status = "OK"
    
    try:
        # Verificar conexão com MongoDB
        await mongodb.connect_to_database()
        info = await mongodb.client.server_info()
    except Exception as e:
        mongo_status = f"Error: {str(e)}"
    
    try:
        # Verificar conexão com ChromaDB
        chromadb_client.connect_to_database()
    except Exception as e:
        chroma_status = f"Error: {str(e)}"
    
    return {
        "status": "API is running",
        "mongodb_status": mongo_status,
        "chromadb_status": chroma_status
    }
