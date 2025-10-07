"""
Health Check Endpoint
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint para verificar se a API está funcionando.
    """
    return {
        "status": "healthy",
        "message": "API is running"
    }
