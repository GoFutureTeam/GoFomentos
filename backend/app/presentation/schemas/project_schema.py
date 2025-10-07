"""
Project Schemas - Modelos Pydantic para request/response de projetos
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# Request Schemas
class ProjectCreateRequest(BaseModel):
    """Schema para criação de projeto"""
    titulo_projeto: str = Field(..., description="Título do projeto")
    objetivo_principal: str = Field(..., description="Objetivo principal do projeto")
    nome_empresa: str = Field(..., description="Nome da empresa")
    resumo_atividades: str = Field(..., description="Resumo das atividades da empresa")
    cnae: str = Field(..., description="CNAE da empresa")
    documento_url: Optional[str] = Field(None, description="URL do documento PDF")
    edital_uuid: Optional[str] = Field(None, description="UUID do edital relacionado")


class ProjectUpdateRequest(BaseModel):
    """Schema para atualização de projeto"""
    titulo_projeto: Optional[str] = None
    objetivo_principal: Optional[str] = None
    nome_empresa: Optional[str] = None
    resumo_atividades: Optional[str] = None
    cnae: Optional[str] = None
    documento_url: Optional[str] = None
    edital_uuid: Optional[str] = None


# Response Schemas
class ProjectResponse(BaseModel):
    """Schema de resposta para projeto"""
    id: str
    titulo_projeto: str
    objetivo_principal: str
    nome_empresa: str
    resumo_atividades: str
    cnae: str
    user_id: str
    documento_url: Optional[str] = None
    edital_uuid: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
