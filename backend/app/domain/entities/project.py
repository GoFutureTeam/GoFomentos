"""
Project Domain Entity - Entidade pura de domínio sem dependências externas
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Project:
    """
    Entidade de domínio Project.
    Representa um projeto de uma empresa submetido para um edital.
    """
    titulo_projeto: str
    objetivo_principal: str
    nome_empresa: str
    resumo_atividades: str
    cnae: str
    user_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    documento_url: Optional[str] = None
    edital_uuid: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        titulo_projeto: str,
        objetivo_principal: str,
        nome_empresa: str,
        resumo_atividades: str,
        cnae: str,
        user_id: str,
        documento_url: Optional[str] = None,
        edital_uuid: Optional[str] = None
    ) -> "Project":
        """
        Factory method para criar um novo projeto.

        Args:
            titulo_projeto: Título do projeto
            objetivo_principal: Objetivo principal do projeto
            nome_empresa: Nome da empresa
            resumo_atividades: Resumo das atividades
            cnae: CNAE da empresa
            user_id: ID do usuário proprietário
            documento_url: URL do documento (opcional)
            edital_uuid: UUID do edital relacionado (opcional)

        Returns:
            Project: Nova instância de projeto
        """
        return cls(
            titulo_projeto=titulo_projeto,
            objetivo_principal=objetivo_principal,
            nome_empresa=nome_empresa,
            resumo_atividades=resumo_atividades,
            cnae=cnae,
            user_id=user_id,
            documento_url=documento_url,
            edital_uuid=edital_uuid
        )

    def belongs_to_user(self, user_id: str) -> bool:
        """
        Verifica se o projeto pertence ao usuário.

        Args:
            user_id: ID do usuário

        Returns:
            bool: True se o projeto pertence ao usuário
        """
        return self.user_id == user_id

    def associate_with_edital(self, edital_uuid: str) -> None:
        """
        Associa o projeto a um edital.

        Args:
            edital_uuid: UUID do edital
        """
        self.edital_uuid = edital_uuid
        self.updated_at = datetime.utcnow()

    def update_info(
        self,
        titulo_projeto: Optional[str] = None,
        objetivo_principal: Optional[str] = None,
        nome_empresa: Optional[str] = None,
        resumo_atividades: Optional[str] = None,
        cnae: Optional[str] = None,
        documento_url: Optional[str] = None
    ) -> None:
        """
        Atualiza informações do projeto.

        Args:
            titulo_projeto: Novo título (opcional)
            objetivo_principal: Novo objetivo (opcional)
            nome_empresa: Novo nome da empresa (opcional)
            resumo_atividades: Novo resumo (opcional)
            cnae: Novo CNAE (opcional)
            documento_url: Nova URL do documento (opcional)
        """
        if titulo_projeto:
            self.titulo_projeto = titulo_projeto
        if objetivo_principal:
            self.objetivo_principal = objetivo_principal
        if nome_empresa:
            self.nome_empresa = nome_empresa
        if resumo_atividades:
            self.resumo_atividades = resumo_atividades
        if cnae:
            self.cnae = cnae
        if documento_url is not None:
            self.documento_url = documento_url

        self.updated_at = datetime.utcnow()

    def attach_document(self, documento_url: str) -> None:
        """
        Anexa um documento ao projeto.

        Args:
            documento_url: URL do documento
        """
        self.documento_url = documento_url
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Converte a entidade para dicionário"""
        return {
            "id": self.id,
            "titulo_projeto": self.titulo_projeto,
            "objetivo_principal": self.objetivo_principal,
            "nome_empresa": self.nome_empresa,
            "resumo_atividades": self.resumo_atividades,
            "cnae": self.cnae,
            "user_id": self.user_id,
            "documento_url": self.documento_url,
            "edital_uuid": self.edital_uuid,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        """Cria uma entidade a partir de um dicionário"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            titulo_projeto=data["titulo_projeto"],
            objetivo_principal=data["objetivo_principal"],
            nome_empresa=data["nome_empresa"],
            resumo_atividades=data["resumo_atividades"],
            cnae=data["cnae"],
            user_id=data["user_id"],
            documento_url=data.get("documento_url"),
            edital_uuid=data.get("edital_uuid"),
            created_at=data.get("created_at", datetime.utcnow()),
            updated_at=data.get("updated_at", datetime.utcnow())
        )
