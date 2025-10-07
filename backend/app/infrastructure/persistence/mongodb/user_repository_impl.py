"""
MongoDB User Repository Implementation
"""
from typing import Optional, List
from ....domain.entities.user import User
from ....domain.repositories.user_repository import UserRepository
from ....domain.exceptions.domain_exceptions import UserNotFoundError, UserAlreadyExistsError
from .connection import MongoDBConnection


class MongoUserRepository(UserRepository):
    """
    Implementação concreta do UserRepository usando MongoDB.
    """

    def __init__(self, db_connection: MongoDBConnection):
        """
        Inicializa o repositório.

        Args:
            db_connection: Conexão com MongoDB
        """
        self.db_connection = db_connection
        self.collection_name = "users"

    def _get_collection(self):
        """Retorna a coleção de usuários"""
        return self.db_connection.get_collection(self.collection_name)

    async def create(self, user: User) -> User:
        """Cria um novo usuário"""
        collection = self._get_collection()

        # Verificar se email já existe
        if await self.exists_by_email(user.email):
            raise UserAlreadyExistsError(user.email)

        # Inserir usuário
        await collection.insert_one(user.to_dict())
        return user

    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Busca usuário por ID"""
        collection = self._get_collection()
        data = await collection.find_one({"id": user_id})

        if data:
            return User.from_dict(data)
        return None

    async def find_by_email(self, email: str) -> Optional[User]:
        """Busca usuário por email"""
        collection = self._get_collection()
        data = await collection.find_one({"email": email})

        if data:
            return User.from_dict(data)
        return None

    async def find_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Busca todos os usuários com paginação"""
        collection = self._get_collection()
        cursor = collection.find().skip(skip).limit(limit)
        users_data = await cursor.to_list(length=limit)

        return [User.from_dict(data) for data in users_data]

    async def update(self, user: User) -> User:
        """Atualiza um usuário existente"""
        collection = self._get_collection()

        # Verificar se o usuário existe
        existing = await collection.find_one({"id": user.id})
        if not existing:
            raise UserNotFoundError(user_id=user.id)

        # Atualizar usuário
        await collection.update_one(
            {"id": user.id},
            {"$set": user.to_dict()}
        )

        return user

    async def delete(self, user_id: str) -> bool:
        """Deleta um usuário"""
        collection = self._get_collection()
        result = await collection.delete_one({"id": user_id})
        return result.deleted_count > 0

    async def exists_by_email(self, email: str) -> bool:
        """Verifica se um usuário com o email existe"""
        collection = self._get_collection()
        count = await collection.count_documents({"email": email})
        return count > 0
