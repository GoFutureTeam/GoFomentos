"""
Edital Schemas - Modelos Pydantic para request/response de editais
"""
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, Union


# Request Schemas
class EditalCreateRequest(BaseModel):
    """Schema para criação de edital"""
    apelido_edital: str = Field(..., description="Nome/título do edital")
    link: str = Field(..., description="URL do edital")

    # Financiadores
    financiador_1: Optional[str] = None
    financiador_2: Optional[str] = None

    # Classificação
    area_foco: Optional[str] = None
    tipo_proponente: Optional[str] = None
    empresas_que_podem_submeter: Optional[str] = None

    # Duração
    duracao_min_meses: Optional[int] = None
    duracao_max_meses: Optional[int] = None

    # Valores
    valor_min_R: Optional[float] = Field(None, alias="valor_min_R$")
    valor_max_R: Optional[float] = Field(None, alias="valor_max_R$")

    # Recursos
    tipo_recurso: Optional[str] = None
    recepcao_recursos: Optional[str] = None
    custeio: Optional[bool] = None
    capital: Optional[bool] = None

    # Contrapartida
    contrapartida_min_pct: Optional[float] = Field(None, alias="contrapartida_min_%")
    contrapartida_max_pct: Optional[float] = Field(None, alias="contrapartida_max_%")
    tipo_contrapartida: Optional[str] = None

    # Datas (aceita string YYYY-MM-DD ou date)
    data_inicial_submissao: Optional[Union[str, date]] = None
    data_final_submissao: Optional[Union[str, date]] = None
    data_resultado: Optional[Union[str, date]] = None

    # Descrições
    descricao_completa: Optional[str] = None
    origem: Optional[str] = None
    observacoes: Optional[str] = None

    # Status
    status: Optional[str] = Field(None, description="'aberto', 'fechado', 'em_breve'")

    class Config:
        populate_by_name = True


class EditalUpdateRequest(BaseModel):
    """Schema para atualização de edital"""
    apelido_edital: Optional[str] = None
    link: Optional[str] = None
    financiador_1: Optional[str] = None
    financiador_2: Optional[str] = None
    area_foco: Optional[str] = None
    tipo_proponente: Optional[str] = None
    empresas_que_podem_submeter: Optional[str] = None
    duracao_min_meses: Optional[int] = None
    duracao_max_meses: Optional[int] = None
    valor_min_R: Optional[float] = Field(None, alias="valor_min_R$")
    valor_max_R: Optional[float] = Field(None, alias="valor_max_R$")
    tipo_recurso: Optional[str] = None
    recepcao_recursos: Optional[str] = None
    custeio: Optional[bool] = None
    capital: Optional[bool] = None
    contrapartida_min_pct: Optional[float] = Field(None, alias="contrapartida_min_%")
    contrapartida_max_pct: Optional[float] = Field(None, alias="contrapartida_max_%")
    tipo_contrapartida: Optional[str] = None
    data_inicial_submissao: Optional[Union[str, date]] = None
    data_final_submissao: Optional[Union[str, date]] = None
    data_resultado: Optional[Union[str, date]] = None
    descricao_completa: Optional[str] = None
    origem: Optional[str] = None
    observacoes: Optional[str] = None
    status: Optional[str] = None

    class Config:
        populate_by_name = True


# Response Schemas
class EditalResponse(BaseModel):
    """Schema de resposta para edital"""
    uuid: str
    apelido_edital: str
    link: str
    financiador_1: Optional[str] = None
    financiador_2: Optional[str] = None
    area_foco: Optional[str] = None
    tipo_proponente: Optional[str] = None
    empresas_que_podem_submeter: Optional[str] = None
    duracao_min_meses: Optional[int] = None
    duracao_max_meses: Optional[int] = None
    valor_min_R: Optional[float] = None
    valor_max_R: Optional[float] = None
    tipo_recurso: Optional[str] = None
    recepcao_recursos: Optional[str] = None
    custeio: Optional[bool] = None
    capital: Optional[bool] = None
    contrapartida_min_pct: Optional[float] = None
    contrapartida_max_pct: Optional[float] = None
    tipo_contrapartida: Optional[str] = None
    data_inicial_submissao: Optional[date] = None
    data_final_submissao: Optional[date] = None
    data_resultado: Optional[date] = None
    descricao_completa: Optional[str] = None
    origem: Optional[str] = None
    observacoes: Optional[str] = None
    status: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
