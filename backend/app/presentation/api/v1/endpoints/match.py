"""
Match Endpoints - Presentation Layer
API para match entre projetos e editais usando busca vetorial + GPT-4o
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any

from app.domain.entities.user import User
from app.presentation.api.v1.dependencies import get_current_user
from app.application.use_cases.match.match_project_to_editais import MatchProjectToEditaisUseCase
from app.presentation.schemas.match_schema import (
    MatchProjectRequest,
    MatchResponse
)

router = APIRouter()


def get_match_use_case() -> MatchProjectToEditaisUseCase:
    """Dependency para obter o MatchProjectToEditaisUseCase"""
    from app.core.container_instance import container
    return container.match_project_use_case()


@router.post(
    "/match/project",
    response_model=MatchResponse,
    status_code=status.HTTP_200_OK,
    tags=["match"],
    summary="Match de projeto com editais compatíveis",
    description="""
    **Algoritmo de Match Inteligente usando ChromaDB + GPT-4o**
    
    Este endpoint realiza um match avançado entre um projeto e editais de fomento disponíveis.
    
    ## 🔍 Como Funciona (Algoritmo em 6 Etapas):
    
    ### 1️⃣ Recebimento dos Dados
    - Recebe informações do projeto (título, objetivo, empresa, CNAE, etc.)
    
    ### 2️⃣ Geração de Palavras-Chave (GPT-4o)
    - GPT-4o analisa o projeto e gera **3 frases-chave** otimizadas para busca vetorial
    - Foco em: área temática, público-alvo, tecnologias, impacto social
    
    ### 3️⃣ Busca Vetorial no ChromaDB
    - Para cada frase-chave, busca os **top 10 chunks** mais similares
    - Total: até 30 chunks recuperados do banco vetorial
    
    ### 4️⃣ Agrupamento e Deduplicação
    - Agrupa chunks por edital
    - Remove duplicatas
    - Identifica editais candidatos
    
    ### 5️⃣ Análise de Compatibilidade (GPT-4o)
    - Para cada edital candidato:
      - GPT-4o analisa compatibilidade detalhada
      - Gera score de 0-100
      - Identifica fatores de compatibilidade
      - Justifica o match
    
    ### 6️⃣ Ranqueamento e Retorno
    - Ordena editais por score (maior → menor)
    - Retorna **top 10 editais** mais compatíveis
    
    ## 📊 Resposta Inclui:
    - ✅ Score de compatibilidade (0-100)
    - ✅ Justificativa do match
    - ✅ Fatores de compatibilidade
    - ✅ Detalhes do edital (financiador, valores, prazos)
    - ✅ Palavras-chave usadas na busca
    - ✅ Tempo de execução
    
    ## 🎯 Exemplo de Uso:
    ```json
    {
      "titulo_projeto": "Projeto Raízes Digitais",
      "objetivo_principal": "Criar uma plataforma gamificada para educar crianças sobre biomas brasileiros",
      "nome_empresa": "InovaEdu Soluções Tecnológicas Ltda.",
      "resumo_atividades": "Empresa de tecnologia com foco em soluções educacionais (EdTech)",
      "cnae": "6201-5/01 - Desenvolvimento de programas de computador sob encomenda",
      "user_id": "0c3a6ed1-cff8-4530-a686-d5a328558093"
    }
    ```
    
    ## ⚡ Performance:
    - Tempo médio: 5-10 segundos
    - Depende do número de editais no banco vetorial
    
    ## 🔐 Autenticação:
    - Requer token JWT válido
    """
)
async def match_project_to_editais(
    request: MatchProjectRequest,
    current_user: User = Depends(get_current_user),
    match_use_case: MatchProjectToEditaisUseCase = Depends(get_match_use_case)
):
    """
    Realiza match entre projeto e editais compatíveis.
    
    **Fluxo:**
    1. Valida autenticação do usuário
    2. Extrai dados do projeto
    3. Executa algoritmo de match (ChromaDB + GPT-4o)
    4. Retorna editais ranqueados por compatibilidade
    
    **Args:**
    - request: Dados do projeto (MatchProjectRequest)
    - current_user: Usuário autenticado (injetado)
    - match_use_case: Use case de match (injetado)
    
    **Returns:**
    - MatchResponse: Lista de editais compatíveis com scores
    
    **Raises:**
    - HTTPException 401: Token inválido ou expirado
    - HTTPException 500: Erro interno no processamento
    """
    try:
        # Executar algoritmo de match
        result = await match_use_case.execute(
            titulo_projeto=request.titulo_projeto,
            objetivo_principal=request.objetivo_principal,
            nome_empresa=request.nome_empresa,
            resumo_atividades=request.resumo_atividades,
            cnae=request.cnae,
            user_id=request.user_id
        )
        
        return MatchResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dados inválidos: {str(e)}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar match: {str(e)}"
        )


@router.get(
    "/match/health",
    tags=["match"],
    summary="Health check do serviço de match"
)
async def match_health_check():
    """
    Verifica se o serviço de match está operacional.
    
    **Returns:**
    - Status do serviço
    - Componentes verificados (ChromaDB, OpenAI)
    """
    from app.core.container_instance import container
    
    try:
        # Verificar ChromaDB
        chromadb_service = container.chromadb_service()
        stats = await chromadb_service.get_stats()
        
        return {
            "status": "healthy",
            "service": "match",
            "chromadb": {
                "status": "connected",
                "total_chunks": stats.get("total_chunks", 0),
                "total_editais": stats.get("total_editais", 0)
            },
            "openai": {
                "status": "configured",
                "model": "gpt-4o"
            }
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "match",
            "error": str(e)
        }
