"""
Conversation Repository MongoDB Implementation - Infrastructure Layer
"""
from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from ....domain.entities.conversation import Conversation
from ....domain.repositories.conversation_repository import ConversationRepository


class ConversationRepositoryImpl(ConversationRepository):
    """
    Implementação concreta do repositório de conversas usando MongoDB.
    """

    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Inicializa o repositório.

        Args:
            database: Instância do banco MongoDB
        """
        self.collection = database["conversations"]

    async def create(self, conversation: Conversation) -> str:
        """
        Cria uma nova conversa no MongoDB.

        Args:
            conversation: Entidade de conversa

        Returns:
            str: ID da conversa criada
        """
        doc = conversation.to_dict()

        # Remover ID se existir (MongoDB vai gerar)
        doc.pop("_id", None)

        result = await self.collection.insert_one(doc)
        return str(result.inserted_id)

    async def get_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """
        Busca conversa por ID.

        Args:
            conversation_id: ID da conversa

        Returns:
            Conversation ou None se não encontrada
        """
        try:
            doc = await self.collection.find_one({"_id": ObjectId(conversation_id)})

            if doc:
                return Conversation.from_dict(doc)

            return None

        except Exception as e:
            print(f"Erro ao buscar conversa: {e}")
            return None

    async def get_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Conversation]:
        """
        Busca conversas de um usuário com paginação.

        Args:
            user_id: ID do usuário
            skip: Quantidade de registros a pular
            limit: Limite de resultados

        Returns:
            Lista de conversas ordenadas por data (mais recentes primeiro)
        """
        cursor = self.collection.find({"user_id": user_id}) \
            .sort("updated_at", -1) \
            .skip(skip) \
            .limit(limit)

        conversations = []
        async for doc in cursor:
            conversations.append(Conversation.from_dict(doc))

        return conversations

    async def update(self, conversation: Conversation) -> bool:
        """
        Atualiza uma conversa existente.

        Args:
            conversation: Entidade de conversa com dados atualizados

        Returns:
            bool: True se atualizado com sucesso
        """
        if not conversation.id:
            return False

        doc = conversation.to_dict()
        doc.pop("_id", None)  # Remover ID do update

        result = await self.collection.update_one(
            {"_id": ObjectId(conversation.id)},
            {"$set": doc}
        )

        return result.modified_count > 0

    async def delete(self, conversation_id: str) -> bool:
        """
        Deleta uma conversa.

        Args:
            conversation_id: ID da conversa

        Returns:
            bool: True se deletado com sucesso
        """
        try:
            result = await self.collection.delete_one(
                {"_id": ObjectId(conversation_id)}
            )
            return result.deleted_count > 0

        except Exception as e:
            print(f"Erro ao deletar conversa: {e}")
            return False

    async def count_by_user(self, user_id: str) -> int:
        """
        Conta total de conversas de um usuário.

        Args:
            user_id: ID do usuário

        Returns:
            int: Número de conversas
        """
        return await self.collection.count_documents({"user_id": user_id})
