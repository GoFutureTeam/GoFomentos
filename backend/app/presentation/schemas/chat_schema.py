"""
Chat Schemas - Presentation Layer
DTOs (Data Transfer Objects) para API de chat
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============= REQUEST SCHEMAS =============

class CreateConversationRequest(BaseModel):
    """Request para criar nova conversa"""
    edital_uuid: Optional[str] = Field(
        None,
        description="UUID do edital para filtrar contexto (opcional)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "edital_uuid": "abc123-def456"
            }
        }


class SendMessageRequest(BaseModel):
    """Request para enviar mensagem"""
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Mensagem do usuário"
    )
    edital_uuid: Optional[str] = Field(
        None,
        description="Filtrar contexto por edital específico (opcional)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Qual é o prazo de submissão do edital?",
                "edital_uuid": "abc123-def456"
            }
        }


# ============= RESPONSE SCHEMAS =============

class ChatMessageResponse(BaseModel):
    """Representa uma mensagem no histórico"""
    role: str = Field(..., description="'user' ou 'assistant'")
    content: str = Field(..., description="Conteúdo da mensagem")
    timestamp: datetime = Field(..., description="Data/hora da mensagem")
    sources: List[str] = Field(
        default_factory=list,
        description="IDs dos chunks usados (apenas para assistant)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "role": "assistant",
                "content": "O prazo de submissão é 30/12/2025.",
                "timestamp": "2025-01-15T10:30:00",
                "sources": ["edital123_chunk_1", "edital123_chunk_5"]
            }
        }


class ConversationResponse(BaseModel):
    """Resposta com dados da conversa"""
    id: str = Field(..., description="ID da conversa")
    user_id: str = Field(..., description="ID do usuário")
    title: str = Field(..., description="Título da conversa")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")
    edital_uuid: Optional[str] = Field(None, description="UUID do edital filtrado")
    messages: List[ChatMessageResponse] = Field(
        default_factory=list,
        description="Histórico de mensagens"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "user_id": "user123",
                "title": "Qual é o prazo de submissão?",
                "created_at": "2025-01-15T10:00:00",
                "updated_at": "2025-01-15T10:30:00",
                "edital_uuid": None,
                "messages": [
                    {
                        "role": "user",
                        "content": "Qual é o prazo de submissão?",
                        "timestamp": "2025-01-15T10:00:00",
                        "sources": []
                    },
                    {
                        "role": "assistant",
                        "content": "O prazo de submissão é 30/12/2025.",
                        "timestamp": "2025-01-15T10:00:05",
                        "sources": ["edital123_chunk_1"]
                    }
                ]
            }
        }


class SendMessageResponse(BaseModel):
    """Resposta ao enviar mensagem"""
    conversation_id: str = Field(..., description="ID da conversa")
    message: str = Field(..., description="Resposta do assistente")
    sources: List[str] = Field(..., description="Chunks usados na resposta")
    chunks_used: int = Field(..., description="Quantidade de chunks usados")
    timestamp: datetime = Field(..., description="Timestamp da resposta")

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "507f1f77bcf86cd799439011",
                "message": "O prazo de submissão do Edital CNPq 01/2025 é 30/12/2025.",
                "sources": ["edital123_chunk_1", "edital123_chunk_5"],
                "chunks_used": 2,
                "timestamp": "2025-01-15T10:30:00"
            }
        }


class ConversationListResponse(BaseModel):
    """Lista de conversas (paginada)"""
    total: int = Field(..., description="Total de conversas")
    conversations: List[ConversationResponse] = Field(
        ...,
        description="Lista de conversas"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total": 5,
                "conversations": [
                    {
                        "id": "507f1f77bcf86cd799439011",
                        "user_id": "user123",
                        "title": "Qual é o prazo de submissão?",
                        "created_at": "2025-01-15T10:00:00",
                        "updated_at": "2025-01-15T10:30:00",
                        "edital_uuid": None,
                        "messages": []
                    }
                ]
            }
        }


class DeleteConversationResponse(BaseModel):
    """Resposta ao deletar conversa"""
    success: bool = Field(..., description="Se a operação foi bem-sucedida")
    message: str = Field(..., description="Mensagem descritiva")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Conversa deletada com sucesso"
            }
        }
