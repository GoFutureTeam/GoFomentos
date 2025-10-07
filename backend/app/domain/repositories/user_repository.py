"""
User Repository Interface - Contrato para implementações de persistência de usuários
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from ..entities.user import User


class UserRepository(ABC):
    """
    Interface para repositório de usuários.
    Define operações de persistência sem especificar a implementação.
    """

    @abstractmethod
    async def create(self, user: User) -> User:
        """
        Cria um novo usuário.

        Args:
            user: Entidade User a ser persistida

        Returns:
            User: Usuário criado

        Raises:
            UserAlreadyExistsError: Se o email já está em uso
        """
        pass

    @abstractmethod
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """
        Busca um usuário por ID.

        Args:
            user_id: ID do usuário

        Returns:
            Optional[User]: Usuário encontrado ou None
        """
        pass

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        """
        Busca um usuário por email.

        Args:
            email: Email do usuário

        Returns:
            Optional[User]: Usuário encontrado ou None
        """
        pass

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Busca todos os usuários com paginação.

        Args:
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar

        Returns:
            List[User]: Lista de usuários
        """
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """
        Atualiza um usuário existente.

        Args:
            user: Entidade User com dados atualizados

        Returns:
            User: Usuário atualizado

        Raises:
            UserNotFoundError: Se o usuário não existe
        """
        pass

    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """
        Deleta um usuário.

        Args:
            user_id: ID do usuário

        Returns:
            bool: True se deletado com sucesso, False caso contrário
        """
        pass

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """
        Verifica se um usuário com o email existe.

        Args:
            email: Email a verificar

        Returns:
            bool: True se existe, False caso contrário
        """
        pass
