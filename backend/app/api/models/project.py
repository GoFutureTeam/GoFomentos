from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class ProjectBase(BaseModel):
    """
    Modelo base para projetos.
    Representa a proposta de projeto de uma empresa.
    """
    # Dados do Projeto
    titulo_projeto: str = Field(..., description="Título do projeto")
    objetivo_principal: str = Field(..., description="Objetivo principal do projeto")
    
    # Dados da Empresa
    nome_empresa: str = Field(..., description="Nome da empresa (razão social ou fantasia)")
    resumo_atividades: str = Field(..., description="Resumo das atividades da empresa")
    cnae: str = Field(..., description="CNAE da empresa")
    
    # Documento opcional
    documento_url: Optional[str] = Field(None, description="URL do documento PDF (até 10MB)")
    
    # Relacionamentos
    user_id: str = Field(..., description="ID do usuário proprietário")
    edital_uuid: Optional[str] = Field(None, description="UUID do edital relacionado")


class ProjectCreate(ProjectBase):
    """Modelo para criação de projeto"""
    pass


class ProjectUpdate(BaseModel):
    """Modelo para atualização de projeto"""
    titulo_projeto: Optional[str] = None
    objetivo_principal: Optional[str] = None
    nome_empresa: Optional[str] = None
    resumo_atividades: Optional[str] = None
    cnae: Optional[str] = None
    documento_url: Optional[str] = None
    edital_uuid: Optional[str] = None


class ProjectInDB(ProjectBase):
    """Modelo para projeto no banco de dados"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Project(ProjectBase):
    """Modelo de resposta para projeto"""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
