"""
Chat Message Entity - Domain Layer
"""
from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ChatMessage:
    """
    Entidade de mensagem de chat.
    Representa uma mensagem individual na conversa (usuário ou assistente).
    """
    role: str  # "user" ou "assistant"
    content: str
    timestamp: datetime
    sources: Optional[List[str]] = None  # IDs dos chunks usados (rastreabilidade)

    def __post_init__(self):
        """Validações de domínio"""
        if self.role not in ["user", "assistant"]:
            raise ValueError("Role deve ser 'user' ou 'assistant'")

        if not self.content or not self.content.strip():
            raise ValueError("Conteúdo da mensagem não pode estar vazio")

        if self.sources is None:
            self.sources = []

    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "sources": self.sources or []
        }

    @staticmethod
    def from_dict(data: dict) -> 'ChatMessage':
        """Cria instância a partir de dicionário"""
        return ChatMessage(
            role=data["role"],
            content=data["content"],
            timestamp=data["timestamp"],
            sources=data.get("sources", [])
        )
