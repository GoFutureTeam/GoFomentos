"""
User Domain Entity - Entidade pura de domínio sem dependências externas
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class User:
    """
    Entidade de domínio User.
    Representa um usuário do sistema com suas regras de negócio.
    """
    email: str
    name: str
    hashed_password: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(cls, email: str, name: str, hashed_password: str) -> "User":
        """
        Factory method para criar um novo usuário.

        Args:
            email: Email do usuário
            name: Nome completo do usuário
            hashed_password: Senha já hasheada

        Returns:
            User: Nova instância de usuário
        """
        return cls(
            email=email,
            name=name,
            hashed_password=hashed_password
        )

    def deactivate(self) -> None:
        """Desativa o usuário"""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Ativa o usuário"""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def update_profile(self, name: Optional[str] = None, email: Optional[str] = None) -> None:
        """
        Atualiza informações do perfil do usuário.

        Args:
            name: Novo nome (opcional)
            email: Novo email (opcional)
        """
        if name:
            self.name = name
        if email:
            self.email = email
        self.updated_at = datetime.utcnow()

    def change_password(self, new_hashed_password: str) -> None:
        """
        Altera a senha do usuário.

        Args:
            new_hashed_password: Nova senha hasheada
        """
        self.hashed_password = new_hashed_password
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Converte a entidade para dicionário"""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "hashed_password": self.hashed_password,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Cria uma entidade a partir de um dicionário"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            email=data["email"],
            name=data["name"],
            hashed_password=data["hashed_password"],
            is_active=data.get("is_active", True),
            created_at=data.get("created_at", datetime.utcnow()),
            updated_at=data.get("updated_at", datetime.utcnow())
        )
