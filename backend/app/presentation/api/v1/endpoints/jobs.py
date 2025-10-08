"""
Jobs Endpoints - Gerenciamento de jobs agendados
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List

from app.domain.entities.user import User
from app.domain.entities.job_execution import JobExecution
from app.presentation.schemas.job_schema import (
    JobExecutionResponse,
    JobExecuteResponse,
    JobListResponse
)
from app.application.services.job_scheduler_service import JobSchedulerService
from app.domain.repositories.job_repository import JobRepository
from app.presentation.api.v1.dependencies import get_current_user, get_job_scheduler, get_job_repository


router = APIRouter()


def job_to_response(job: JobExecution) -> JobExecutionResponse:
    """Converte entidade JobExecution para JobExecutionResponse"""
    return JobExecutionResponse(
        id=job.id,
        job_name=job.job_name,
        status=job.status,
        started_at=job.started_at,
        finished_at=job.finished_at,
        progress=job.progress,
        total_editais=job.total_editais,
        processed_editais=job.processed_editais,
        failed_editais=job.failed_editais,
        errors=job.errors,
        result_summary=job.result_summary,
        created_at=job.created_at,
        updated_at=job.updated_at
    )


@router.post("/jobs/cnpq/execute", response_model=JobExecuteResponse, tags=["jobs"])
async def execute_cnpq_job_now(
    current_user: User = Depends(get_current_user),
    scheduler: JobSchedulerService = Depends(get_job_scheduler)
):
    """
    Executa o job de raspagem CNPq AGORA (manualmente).

    Inicia a raspagem do site CNPq, download de PDFs e extração de variáveis.
    O job roda em background e você pode monitorar o progresso via GET /jobs/{job_id}
    """

    job_id = await scheduler.execute_cnpq_job_now()

    return JobExecuteResponse(
        job_id=job_id,
        message="Job CNPq iniciado com sucesso",
        status_url=f"/api/v1/jobs/{job_id}"
    )


@router.post("/jobs/fapesq/execute", response_model=JobExecuteResponse, tags=["jobs"])
async def execute_fapesq_job_now(
    filter_by_date: bool = True,
    current_user: User = Depends(get_current_user),
    scheduler: JobSchedulerService = Depends(get_job_scheduler)
):
    """
    Executa o job de raspagem FAPESQ AGORA (manualmente).

    Inicia a raspagem do site FAPESQ-PB, download de PDFs e extração de variáveis.
    O job roda em background e você pode monitorar o progresso via GET /jobs/{job_id}

    Parâmetros:
    - **filter_by_date**: Se True (padrão), filtra apenas editais com prazo >= data atual.
                          Se False, processa TODOS os editais encontrados (útil para testes).

    Filtro de data:
    - Extrai data limite da descrição do edital
    - Compara com data atual
    """

    job_id = await scheduler.execute_fapesq_job_now(filter_by_date=filter_by_date)

    return JobExecuteResponse(
        job_id=job_id,
        message=f"Job FAPESQ iniciado com sucesso (filter_by_date={filter_by_date})",
        status_url=f"/api/v1/jobs/{job_id}"
    )


@router.post("/jobs/paraiba_gov/execute", response_model=JobExecuteResponse, tags=["jobs"])
async def execute_paraiba_gov_job_now(
    filter_by_date: bool = True,
    current_user: User = Depends(get_current_user),
    scheduler: JobSchedulerService = Depends(get_job_scheduler)
):
    """
    Executa o job de raspagem Paraíba Gov AGORA (manualmente).

    Inicia a raspagem do site do Governo da Paraíba (SECTIES), download de PDFs e extração de variáveis.
    O job roda em background e você pode monitorar o progresso via GET /jobs/{job_id}

    Parâmetros:
    - **filter_by_date**: Se True (padrão), filtra apenas editais com prazo >= data atual.
                          Se False, processa TODOS os editais encontrados (útil para testes).

    Filtro de data:
    - Extrai data limite do título/descrição do edital usando regex
    - Compara com data atual
    - Inclui editais sem data identificada (podem ser editais sem prazo definido)
    """

    job_id = await scheduler.execute_paraiba_gov_job_now(filter_by_date=filter_by_date)

    return JobExecuteResponse(
        job_id=job_id,
        message=f"Job Paraíba Gov iniciado com sucesso (filter_by_date={filter_by_date})",
        status_url=f"/api/v1/jobs/{job_id}"
    )


@router.post("/jobs/confap/execute", response_model=JobExecuteResponse, tags=["jobs"])
async def execute_confap_job_now(
    filter_by_date: bool = True,
    current_user: User = Depends(get_current_user),
    scheduler: JobSchedulerService = Depends(get_job_scheduler)
):
    """
    Executa o job de raspagem CONFAP AGORA (manualmente).

    Inicia a raspagem do site do CONFAP (Conselho Nacional das Fundações Estaduais de Amparo à Pesquisa),
    extrai links de download de cada edital, baixa PDFs e extrai variáveis.
    O job roda em background e você pode monitorar o progresso via GET /jobs/{job_id}

    Parâmetros:
    - **filter_by_date**: Se True (padrão), filtra apenas editais com ano >= ano atual.
                          Se False, processa TODOS os editais encontrados (útil para testes).

    Fluxo do scraper:
    1. Acessa página de editais em andamento
    2. Extrai lista de editais com filtro de ano
    3. Para cada edital, acessa página de detalhes
    4. Busca links com "download" no href
    5. Baixa e processa cada PDF encontrado
    6. Extrai variáveis com OpenAI e salva no MongoDB + ChromaDB
    """

    job_id = await scheduler.execute_confap_job_now(filter_by_date=filter_by_date)

    return JobExecuteResponse(
        job_id=job_id,
        message=f"Job CONFAP iniciado com sucesso (filter_by_date={filter_by_date})",
        status_url=f"/api/v1/jobs/{job_id}"
    )


@router.post("/jobs/capes/execute", response_model=JobExecuteResponse, tags=["jobs"])
async def execute_capes_job_now(
    filter_by_date: bool = True,
    current_user: User = Depends(get_current_user),
    scheduler: JobSchedulerService = Depends(get_job_scheduler)
):
    """
    Executa o job de raspagem CAPES AGORA (manualmente).

    Inicia a raspagem do site da CAPES (Coordenação de Aperfeiçoamento de Pessoal de Nível Superior),
    busca chamadas públicas, extrai links de PDFs com "-pdf" no href, baixa e processa.
    O job roda em background e você pode monitorar o progresso via GET /jobs/{job_id}

    Parâmetros:
    - **filter_by_date**: Se True (padrão), filtra apenas chamadas com ano >= ano atual.
                          Se False, processa TODAS as chamadas encontradas (útil para testes).

    Fluxo do scraper:
    1. Acessa página de chamadas públicas
    2. Identifica seções por ano (h3: "Chamadas públicas XXXX")
    3. Filtra por ano se habilitado
    4. Busca links com "-pdf" no href em cada seção
    5. Baixa e processa cada PDF encontrado
    6. Extrai variáveis com OpenAI e salva no MongoDB + ChromaDB
    """

    job_id = await scheduler.execute_capes_job_now(filter_by_date=filter_by_date)

    return JobExecuteResponse(
        job_id=job_id,
        message=f"Job CAPES iniciado com sucesso (filter_by_date={filter_by_date})",
        status_url=f"/api/v1/jobs/{job_id}"
    )


@router.post("/jobs/finep/execute", response_model=JobExecuteResponse, tags=["jobs"])
async def execute_finep_job_now(
    filter_by_date: bool = True,
    current_user: User = Depends(get_current_user),
    scheduler: JobSchedulerService = Depends(get_job_scheduler)
):
    """
    Executa o job de raspagem FINEP AGORA (manualmente).

    Inicia a raspagem do site da FINEP (Financiadora de Estudos e Projetos),
    busca chamadas públicas abertas, extrai links de PDFs (.pdf no href), baixa e processa.
    O job roda em background e você pode monitorar o progresso via GET /jobs/{job_id}

    Parâmetros:
    - **filter_by_date**: Se True (padrão), filtra apenas chamadas com data >= hoje.
                          Se False, processa TODAS as chamadas encontradas (útil para testes).

    Fluxo do scraper:
    1. Acessa página de chamadas públicas abertas
    2. Extrai lista de chamadas com filtro de data
    3. Para cada chamada, acessa página de detalhes
    4. Busca links com ".pdf" no href
    5. Concatena URL base: http://www.finep.gov.br/ + link
    6. Baixa e processa cada PDF encontrado
    7. Extrai variáveis com OpenAI e salva no MongoDB + ChromaDB
    """

    job_id = await scheduler.execute_finep_job_now(filter_by_date=filter_by_date)

    return JobExecuteResponse(
        job_id=job_id,
        message=f"Job FINEP iniciado com sucesso (filter_by_date={filter_by_date})",
        status_url=f"/api/v1/jobs/{job_id}"
    )


@router.get("/jobs/{job_id}", response_model=JobExecutionResponse, tags=["jobs"])
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    job_repo: JobRepository = Depends(get_job_repository)
):
    """
    Retorna o status de um job em execução.

    Use este endpoint para monitorar o progresso de um job em tempo real.
    """

    job = await job_repo.find_by_id(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    return job_to_response(job)


@router.get("/jobs", response_model=JobListResponse, tags=["jobs"])
async def list_jobs(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    job_repo: JobRepository = Depends(get_job_repository)
):
    """
    Lista todos os jobs executados (histórico).

    Retorna jobs ordenados por data de criação (mais recentes primeiro).
    """

    jobs = await job_repo.find_all(skip, limit)

    return JobListResponse(
        jobs=[job_to_response(j) for j in jobs],
        total=len(jobs)
    )


@router.delete("/jobs/{job_id}", tags=["jobs"])
async def cancel_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    scheduler: JobSchedulerService = Depends(get_job_scheduler)
):
    """
    Cancela um job em execução.

    ⚠️ Apenas jobs com status 'running' podem ser cancelados.
    """

    success = await scheduler.cancel_job(job_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or not running"
        )

    return {"message": "Job cancelado com sucesso"}
