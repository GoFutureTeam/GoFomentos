"""
Edital Domain Entity - Entidade pura de domínio sem dependências externas
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional
import uuid


@dataclass
class Edital:
    """
    Entidade de domínio Edital.
    Representa um edital de fomento com suas regras de negócio.
    """
    apelido_edital: str
    link: str
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

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
    valor_min_R: Optional[float] = None
    valor_max_R: Optional[float] = None

    # Recursos
    tipo_recurso: Optional[str] = None
    recepcao_recursos: Optional[str] = None
    custeio: Optional[bool] = None
    capital: Optional[bool] = None

    # Contrapartida
    contrapartida_min_pct: Optional[float] = None
    contrapartida_max_pct: Optional[float] = None
    tipo_contrapartida: Optional[str] = None

    # Datas
    data_inicial_submissao: Optional[date] = None
    data_final_submissao: Optional[date] = None
    data_resultado: Optional[date] = None

    # Descrições
    descricao_completa: Optional[str] = None
    origem: Optional[str] = None
    observacoes: Optional[str] = None

    # Status
    status: Optional[str] = None  # 'aberto', 'fechado', 'em_breve'

    # Metadados
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(cls, apelido_edital: str, link: str, **kwargs) -> "Edital":
        """
        Factory method para criar um novo edital.

        Args:
            apelido_edital: Nome/título do edital
            link: URL do edital
            **kwargs: Outros campos opcionais

        Returns:
            Edital: Nova instância de edital
        """
        return cls(
            apelido_edital=apelido_edital,
            link=link,
            **kwargs
        )

    def is_open(self) -> bool:
        """Verifica se o edital está aberto para submissões"""
        if not self.data_final_submissao:
            return self.status == "aberto"

        today = datetime.now().date()
        return (
            self.status == "aberto" and
            (not self.data_inicial_submissao or self.data_inicial_submissao <= today) and
            self.data_final_submissao >= today
        )

    def is_closed(self) -> bool:
        """Verifica se o edital está fechado"""
        if not self.data_final_submissao:
            return self.status == "fechado"

        today = datetime.now().date()
        return (
            self.status == "fechado" or
            self.data_final_submissao < today
        )

    def close(self) -> None:
        """Fecha o edital"""
        self.status = "fechado"
        self.updated_at = datetime.utcnow()

    def open(self) -> None:
        """Abre o edital"""
        self.status = "aberto"
        self.updated_at = datetime.utcnow()

    def update_info(self, **kwargs) -> None:
        """
        Atualiza informações do edital.

        Args:
            **kwargs: Campos a serem atualizados
        """
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Converte a entidade para dicionário"""
        return {
            "uuid": self.uuid,
            "apelido_edital": self.apelido_edital,
            "link": self.link,
            "financiador_1": self.financiador_1,
            "financiador_2": self.financiador_2,
            "area_foco": self.area_foco,
            "tipo_proponente": self.tipo_proponente,
            "empresas_que_podem_submeter": self.empresas_que_podem_submeter,
            "duracao_min_meses": self.duracao_min_meses,
            "duracao_max_meses": self.duracao_max_meses,
            "valor_min_R": self.valor_min_R,
            "valor_max_R": self.valor_max_R,
            "tipo_recurso": self.tipo_recurso,
            "recepcao_recursos": self.recepcao_recursos,
            "custeio": self.custeio,
            "capital": self.capital,
            "contrapartida_min_pct": self.contrapartida_min_pct,
            "contrapartida_max_pct": self.contrapartida_max_pct,
            "tipo_contrapartida": self.tipo_contrapartida,
            "data_inicial_submissao": self.data_inicial_submissao.isoformat() if self.data_inicial_submissao else None,
            "data_final_submissao": self.data_final_submissao.isoformat() if self.data_final_submissao else None,
            "data_resultado": self.data_resultado.isoformat() if self.data_resultado else None,
            "descricao_completa": self.descricao_completa,
            "origem": self.origem,
            "observacoes": self.observacoes,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Edital":
        """Cria uma entidade a partir de um dicionário"""
        # Campos válidos da entidade
        valid_fields = {
            'uuid', 'apelido_edital', 'link', 'financiador_1', 'financiador_2',
            'area_foco', 'tipo_proponente', 'empresas_que_podem_submeter',
            'duracao_min_meses', 'duracao_max_meses', 'valor_min_R', 'valor_max_R',
            'tipo_recurso', 'recepcao_recursos', 'custeio', 'capital',
            'contrapartida_min_pct', 'contrapartida_max_pct', 'tipo_contrapartida',
            'data_inicial_submissao', 'data_final_submissao', 'data_resultado',
            'descricao_completa', 'origem', 'observacoes', 'status',
            'created_at', 'updated_at'
        }

        # Filtrar apenas campos válidos
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}

        # Garantir campos obrigatórios com valores padrão
        if 'apelido_edital' not in filtered_data:
            filtered_data['apelido_edital'] = 'Sem título'
        if 'link' not in filtered_data:
            filtered_data['link'] = ''

        # Converter strings de data para objetos date
        if isinstance(filtered_data.get("data_inicial_submissao"), str):
            filtered_data["data_inicial_submissao"] = datetime.fromisoformat(filtered_data["data_inicial_submissao"]).date()
        if isinstance(filtered_data.get("data_final_submissao"), str):
            filtered_data["data_final_submissao"] = datetime.fromisoformat(filtered_data["data_final_submissao"]).date()
        if isinstance(filtered_data.get("data_resultado"), str):
            filtered_data["data_resultado"] = datetime.fromisoformat(filtered_data["data_resultado"]).date()

        return cls(**filtered_data)
