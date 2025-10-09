"""
Conversation Repository Interface - Domain Layer
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.conversation import Conversation


class ConversationRepository(ABC):
    """
    Interface do repositório de conversas.
    Define o contrato para persistência de conversas de chat.
    """

    @abstractmethod
    async def create(self, conversation: Conversation) -> str:
        """
        Cria uma nova conversa.

        Args:
            conversation: Entidade de conversa

        Returns:
            str: ID da conversa criada
        """
        pass

    @abstractmethod
    async def get_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """
        Busca conversa por ID.

        Args:
            conversation_id: ID da conversa

        Returns:
            Conversation ou None se não encontrada
        """
        pass

    @abstractmethod
    async def get_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Conversation]:
        """
        Busca conversas de um usuário.

        Args:
            user_id: ID do usuário
            skip: Quantidade de registros a pular (paginação)
            limit: Limite de resultados

        Returns:
            Lista de conversas
        """
        pass

    @abstractmethod
    async def update(self, conversation: Conversation) -> bool:
        """
        Atualiza uma conversa existente.

        Args:
            conversation: Entidade de conversa com dados atualizados

        Returns:
            bool: True se atualizado com sucesso
        """
        pass

    @abstractmethod
    async def delete(self, conversation_id: str) -> bool:
        """
        Deleta uma conversa.

        Args:
            conversation_id: ID da conversa

        Returns:
            bool: True se deletado com sucesso
        """
        pass

    @abstractmethod
    async def count_by_user(self, user_id: str) -> int:
        """
        Conta total de conversas de um usuário.

        Args:
            user_id: ID do usuário

        Returns:
            int: Número de conversas
        """
        pass
