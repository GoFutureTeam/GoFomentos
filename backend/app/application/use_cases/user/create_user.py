"""
Create User Use Case
"""
from ....domain.entities.user import User
from ....domain.repositories.user_repository import UserRepository
from ....infrastructure.security.password_service import PasswordService
from ....domain.exceptions.domain_exceptions import UserAlreadyExistsError


class CreateUserUseCase:
    """
    Caso de uso para criar um novo usuário.
    """

    def __init__(self, user_repository: UserRepository, password_service: PasswordService):
        """
        Inicializa o caso de uso.

        Args:
            user_repository: Repositório de usuários
            password_service: Serviço de hash de senhas
        """
        self.user_repository = user_repository
        self.password_service = password_service

    async def execute(self, email: str, password: str, name: str) -> User:
        """
        Executa o caso de uso de criação de usuário.

        Args:
            email: Email do usuário
            password: Senha do usuário (em texto plano)
            name: Nome do usuário

        Returns:
            User: Usuário criado

        Raises:
            UserAlreadyExistsError: Se o email já está em uso
        """
        # Verificar se o usuário já existe
        if await self.user_repository.exists_by_email(email):
            raise UserAlreadyExistsError(email)

        # Hashear a senha
        hashed_password = self.password_service.hash(password)

        # Criar entidade de domínio
        user = User.create(
            email=email,
            name=name,
            hashed_password=hashed_password
        )

        # Persistir
        created_user = await self.user_repository.create(user)

        return created_user
