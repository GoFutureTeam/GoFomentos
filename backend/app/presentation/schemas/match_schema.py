"""
Match Schemas - Modelos Pydantic para request/response de match entre projetos e editais
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


# Request Schema
class MatchProjectRequest(BaseModel):
    """Schema para requisição de match de projeto com editais"""
    titulo_projeto: str = Field(..., description="Título do projeto")
    objetivo_principal: str = Field(..., description="Objetivo principal do projeto")
    nome_empresa: str = Field(..., description="Nome da empresa")
    resumo_atividades: str = Field(..., description="Resumo das atividades da empresa")
    cnae: str = Field(..., description="CNAE da empresa")
    user_id: str = Field(..., description="ID do usuário")

    class Config:
        json_schema_extra = {
            "example": {
                "titulo_projeto": "Projeto Raízes Digitais",
                "objetivo_principal": "Criar uma plataforma gamificada para educar crianças do ensino fundamental sobre a importância dos biomas brasileiros",
                "nome_empresa": "InovaEdu Soluções Tecnológicas Ltda.",
                "resumo_atividades": "Empresa de tecnologia com foco no desenvolvimento de soluções educacionais (EdTech)",
                "cnae": "6201-5/01 - Desenvolvimento de programas de computador sob encomenda",
                "user_id": "0c3a6ed1-cff8-4530-a686-d5a328558093"
            }
        }


# Response Schemas
class EditalMatchResult(BaseModel):
    """Resultado de match de um edital específico"""
    edital_uuid: str = Field(..., description="UUID do edital")
    edital_name: str = Field(..., description="Nome/apelido do edital")
    match_score: float = Field(..., description="Score de compatibilidade (0-100)")
    match_percentage: str = Field(..., description="Porcentagem formatada (ex: 85%)")
    reasoning: str = Field(..., description="Justificativa do match")
    compatibility_factors: Dict[str, Any] = Field(..., description="Fatores de compatibilidade detalhados")
    edital_details: Optional[Dict[str, Any]] = Field(None, description="Detalhes do edital")
    chunks_found: int = Field(..., description="Número de chunks relevantes encontrados")


class MatchResponse(BaseModel):
    """Schema de resposta para match de projeto"""
    success: bool = Field(..., description="Indica se o match foi bem-sucedido")
    total_matches: int = Field(..., description="Total de editais encontrados")
    keywords_used: List[str] = Field(..., description="Palavras-chave geradas para busca")
    matches: List[EditalMatchResult] = Field(..., description="Lista de editais compatíveis ranqueados")
    execution_time_seconds: float = Field(..., description="Tempo de execução em segundos")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "total_matches": 5,
                "keywords_used": [
                    "plataforma educacional gamificada biomas brasileiros",
                    "tecnologia educação infantil consciência ambiental",
                    "EdTech desenvolvimento aplicativos ensino fundamental"
                ],
                "matches": [
                    {
                        "edital_uuid": "abc-123",
                        "edital_name": "Edital CNPq Educação e Tecnologia 2025",
                        "match_score": 92.5,
                        "match_percentage": "92.5%",
                        "reasoning": "Alta compatibilidade com foco em educação, tecnologia e meio ambiente",
                        "compatibility_factors": {
                            "area_match": "Educação e Tecnologia",
                            "target_audience": "Ensino Fundamental",
                            "theme_alignment": "Meio Ambiente e Sustentabilidade"
                        },
                        "chunks_found": 8
                    }
                ],
                "execution_time_seconds": 3.45
            }
        }
