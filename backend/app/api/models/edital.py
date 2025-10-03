from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime, date
import uuid


class EditalBase(BaseModel):
    """
    Modelo base para editais com todos os campos necessários
    """
    # Campo obrigatório
    apelido_edital: str = Field(..., description="Nome/título do edital")
    link: str = Field(..., description="URL do edital")
    
    # Financiadores
    financiador_1: Optional[str] = Field(None, description="Órgão financiador principal")
    financiador_2: Optional[str] = Field(None, description="Órgão financiador secundário")
    
    # Classificação
    area_foco: Optional[str] = Field(None, description="Área de foco do edital")
    tipo_proponente: Optional[str] = Field(None, description="Tipo de proponente aceito")
    empresas_que_podem_submeter: Optional[str] = Field(None, description="Descrição das empresas elegíveis")
    
    # Duração do projeto
    duracao_min_meses: Optional[int] = Field(None, description="Duração mínima em meses")
    duracao_max_meses: Optional[int] = Field(None, description="Duração máxima em meses")
    
    # Valores financeiros
    valor_min_R: Optional[float] = Field(None, alias="valor_min_R$", description="Valor mínimo em R$")
    valor_max_R: Optional[float] = Field(None, alias="valor_max_R$", description="Valor máximo em R$")
    
    # Recursos
    tipo_recurso: Optional[str] = Field(None, description="Tipo de recurso (reembolsável, não reembolsável, etc)")
    recepcao_recursos: Optional[str] = Field(None, description="Forma de recepção dos recursos")
    custeio: Optional[bool] = Field(None, description="Permite despesas de custeio")
    capital: Optional[bool] = Field(None, description="Permite despesas de capital")
    
    # Contrapartida
    contrapartida_min_pct: Optional[float] = Field(None, alias="contrapartida_min_%", description="Percentual mínimo de contrapartida")
    contrapartida_max_pct: Optional[float] = Field(None, alias="contrapartida_max_%", description="Percentual máximo de contrapartida")
    tipo_contrapartida: Optional[str] = Field(None, description="Tipo de contrapartida exigida")
    
    # Datas (aceita string YYYY-MM-DD ou datetime)
    data_inicial_submissao: Optional[Union[str, datetime, date]] = Field(None, description="Data de abertura (YYYY-MM-DD)")
    data_final_submissao: Optional[Union[str, datetime, date]] = Field(None, description="Data de encerramento (YYYY-MM-DD)")
    data_resultado: Optional[Union[str, datetime, date]] = Field(None, description="Data prevista para resultado (YYYY-MM-DD)")
    
    # Descrições
    descricao_completa: Optional[str] = Field(None, description="Descrição detalhada do edital")
    origem: Optional[str] = Field(None, description="Origem/fonte do edital")
    observacoes: Optional[str] = Field(None, description="Observações adicionais")
    
    # Status para filtro do frontend
    status: Optional[str] = Field(
        None, 
        description="Status do edital: 'aberto', 'fechado', 'em_breve'"
    )
    
    class Config:
        populate_by_name = True  # Permite usar tanto o nome quanto o alias


class EditalCreate(EditalBase):
    pass


class EditalUpdate(BaseModel):
    """Modelo para atualização de edital - todos os campos são opcionais"""
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
    data_inicial_submissao: Optional[Union[str, datetime, date]] = None
    data_final_submissao: Optional[Union[str, datetime, date]] = None
    data_resultado: Optional[Union[str, datetime, date]] = None
    descricao_completa: Optional[str] = None
    origem: Optional[str] = None
    observacoes: Optional[str] = None
    status: Optional[str] = None
    
    class Config:
        populate_by_name = True


class EditalInDB(EditalBase):
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Edital(EditalBase):
    uuid: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EditalChunk(BaseModel):
    edital_uuid: str
    url: str
    pagina: int
    chunk_index: int
    texto: str
