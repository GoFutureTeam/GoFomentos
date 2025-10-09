"""
Conversation Entity - Domain Layer
"""
from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass, field

from .chat_message import ChatMessage


@dataclass
class Conversation:
    """
    Entidade de conversa.
    Agregado que contém múltiplas mensagens de chat.
    """
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessage] = field(default_factory=list)
    edital_uuid: Optional[str] = None  # Filtrar contexto por edital específico
    id: Optional[str] = None  # MongoDB ObjectId como string

    def add_message(self, message: ChatMessage) -> None:
        """
        Adiciona uma mensagem à conversa.
        Atualiza o timestamp de modificação.
        """
        self.messages.append(message)
        self.updated_at = datetime.utcnow()

    def get_messages_history(self, limit: Optional[int] = None) -> List[ChatMessage]:
        """
        Retorna o histórico de mensagens.

        Args:
            limit: Número máximo de mensagens recentes (None = todas)

        Returns:
            Lista de mensagens ordenadas cronologicamente
        """
        if limit:
            return self.messages[-limit:]
        return self.messages

    def generate_title(self) -> str:
        """
        Gera um título baseado na primeira mensagem do usuário.
        Trunca em 50 caracteres.
        """
        if not self.messages:
            return "Nova Conversa"

        first_user_msg = next(
            (msg for msg in self.messages if msg.role == "user"),
            None
        )

        if first_user_msg:
            content = first_user_msg.content.strip()
            return content[:50] + "..." if len(content) > 50 else content

        return "Nova Conversa"

    def to_dict(self) -> dict:
        """Converte para dicionário (persistência)"""
        return {
            "user_id": self.user_id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages": [msg.to_dict() for msg in self.messages],
            "edital_uuid": self.edital_uuid
        }

    @staticmethod
    def from_dict(data: dict) -> 'Conversation':
        """Cria instância a partir de dicionário"""
        messages = [
            ChatMessage.from_dict(msg) for msg in data.get("messages", [])
        ]

        return Conversation(
            id=str(data.get("_id", "")),
            user_id=data["user_id"],
            title=data["title"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            messages=messages,
            edital_uuid=data.get("edital_uuid")
        )
