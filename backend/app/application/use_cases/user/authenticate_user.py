"""
Authenticate User Use Case
"""
from datetime import timedelta
from typing import Dict, Any
from ....domain.entities.user import User
from ....domain.repositories.user_repository import UserRepository
from ....infrastructure.security.password_service import PasswordService
from ....infrastructure.security.jwt_service import JWTService
from ....domain.exceptions.domain_exceptions import (
    InvalidCredentialsError,
    UserInactiveError
)


class AuthenticateUserUseCase:
    """
    Caso de uso para autenticar um usuário e gerar token JWT.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
        jwt_service: JWTService
    ):
        """
        Inicializa o caso de uso.

        Args:
            user_repository: Repositório de usuários
            password_service: Serviço de verificação de senhas
            jwt_service: Serviço de geração de tokens JWT
        """
        self.user_repository = user_repository
        self.password_service = password_service
        self.jwt_service = jwt_service

    async def execute(self, email: str, password: str) -> Dict[str, Any]:
        """
        Executa o caso de uso de autenticação.

        Args:
            email: Email do usuário
            password: Senha do usuário (em texto plano)

        Returns:
            Dict[str, Any]: Dicionário contendo token e informações do usuário

        Raises:
            InvalidCredentialsError: Se as credenciais estiverem incorretas
            UserInactiveError: Se o usuário estiver inativo
        """
        # Buscar usuário por email
        user = await self.user_repository.find_by_email(email)
        if not user:
            raise InvalidCredentialsError()

        # Verificar senha
        if not self.password_service.verify(password, user.hashed_password):
            raise InvalidCredentialsError()

        # Verificar se o usuário está ativo
        if not user.is_active:
            raise UserInactiveError()

        # Gerar token JWT
        access_token = self.jwt_service.create_access_token(
            data={"sub": user.email}
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name
            }
        }
