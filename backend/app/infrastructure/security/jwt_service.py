"""
JWT Service - Serviço para criação e validação de tokens JWT
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from ...domain.exceptions.domain_exceptions import InvalidTokenError


class JWTService:
    """
    Serviço para gerenciamento de tokens JWT.
    """

    def __init__(self, secret_key: str, algorithm: str = "HS256", expiration_minutes: int = 30):
        """
        Inicializa o serviço JWT.

        Args:
            secret_key: Chave secreta para assinar tokens
            algorithm: Algoritmo de criptografia (padrão: HS256)
            expiration_minutes: Tempo de expiração do token em minutos
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expiration_minutes = expiration_minutes

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Cria um token JWT.

        Args:
            data: Dados a serem codificados no token
            expires_delta: Tempo customizado de expiração (opcional)

        Returns:
            str: Token JWT codificado
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.expiration_minutes)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

        return encoded_jwt

    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decodifica e valida um token JWT.

        Args:
            token: Token JWT a ser decodificado

        Returns:
            Dict[str, Any]: Dados contidos no token

        Raises:
            InvalidTokenError: Se o token for inválido ou expirado
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            raise InvalidTokenError() from e

    def extract_subject(self, token: str) -> str:
        """
        Extrai o subject (sub) de um token JWT.

        Args:
            token: Token JWT

        Returns:
            str: Subject do token (geralmente email ou user_id)

        Raises:
            InvalidTokenError: Se o token for inválido ou não contiver subject
        """
        payload = self.decode_token(token)
        subject = payload.get("sub")

        if subject is None:
            raise InvalidTokenError()

        return subject
