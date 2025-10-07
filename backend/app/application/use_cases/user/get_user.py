"""
Get User Use Case
"""
from typing import Optional
from ....domain.entities.user import User
from ....domain.repositories.user_repository import UserRepository
from ....domain.exceptions.domain_exceptions import UserNotFoundError


class GetUserUseCase:
    """
    Caso de uso para obter informações de um usuário.
    """

    def __init__(self, user_repository: UserRepository):
        """
        Inicializa o caso de uso.

        Args:
            user_repository: Repositório de usuários
        """
        self.user_repository = user_repository

    async def execute_by_id(self, user_id: str) -> User:
        """
        Obtém um usuário por ID.

        Args:
            user_id: ID do usuário

        Returns:
            User: Usuário encontrado

        Raises:
            UserNotFoundError: Se o usuário não existir
        """
        user = await self.user_repository.find_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id=user_id)
        return user

    async def execute_by_email(self, email: str) -> User:
        """
        Obtém um usuário por email.

        Args:
            email: Email do usuário

        Returns:
            User: Usuário encontrado

        Raises:
            UserNotFoundError: Se o usuário não existir
        """
        user = await self.user_repository.find_by_email(email)
        if not user:
            raise UserNotFoundError(email=email)
        return user
