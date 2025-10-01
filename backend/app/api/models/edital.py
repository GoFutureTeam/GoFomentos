from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class EditalBase(BaseModel):
    apelido_edital: str
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
    contrapartida_min_pct: Optional[float] = Field(None, alias="contrapartida_min_%")
    contrapartida_max_pct: Optional[float] = Field(None, alias="contrapartida_max_%")
    tipo_contrapartida: Optional[str] = None
    data_inicial_submissao: Optional[datetime] = None
    data_final_submissao: Optional[datetime] = None
    data_resultado: Optional[datetime] = None
    descricao_completa: Optional[str] = None
    origem: Optional[str] = None
    link: str
    observacoes: Optional[str] = None


class EditalCreate(EditalBase):
    pass


class EditalUpdate(BaseModel):
    apelido_edital: Optional[str] = None
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
    contrapartida_min_pct: Optional[float] = Field(None, alias="contrapartida_min_%")
    contrapartida_max_pct: Optional[float] = Field(None, alias="contrapartida_max_%")
    tipo_contrapartida: Optional[str] = None
    data_inicial_submissao: Optional[datetime] = None
    data_final_submissao: Optional[datetime] = None
    data_resultado: Optional[datetime] = None
    descricao_completa: Optional[str] = None
    origem: Optional[str] = None
    link: Optional[str] = None
    observacoes: Optional[str] = None


class EditalInDB(EditalBase):
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Edital(EditalBase):
    uuid: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class EditalChunk(BaseModel):
    edital_uuid: str
    url: str
    pagina: int
    chunk_index: int
    texto: str
