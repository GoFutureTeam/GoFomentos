"""
Password Service - Serviço para hash e verificação de senhas
"""
from abc import ABC, abstractmethod
from passlib.context import CryptContext


class PasswordService(ABC):
    """Interface para serviço de senhas"""

    @abstractmethod
    def hash(self, password: str) -> str:
        """Cria hash de uma senha"""
        pass

    @abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica se a senha corresponde ao hash"""
        pass


class Argon2PasswordService(PasswordService):
    """
    Implementação do serviço de senhas usando Argon2.
    Argon2 é mais seguro e moderno que bcrypt, sem limitações de tamanho.
    """

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

    def hash(self, password: str) -> str:
        """
        Cria hash de uma senha usando Argon2.

        Args:
            password: Senha em texto plano

        Returns:
            str: Hash da senha
        """
        return self.pwd_context.hash(password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifica se a senha corresponde ao hash.

        Args:
            plain_password: Senha em texto plano
            hashed_password: Hash da senha

        Returns:
            bool: True se a senha está correta
        """
        return self.pwd_context.verify(plain_password, hashed_password)
