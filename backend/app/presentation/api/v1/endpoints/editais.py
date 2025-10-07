"""
Edital Endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List

from app.presentation.schemas.edital_schema import EditalCreateRequest, EditalResponse
from app.application.use_cases.edital.create_edital import CreateEditalUseCase
from app.application.use_cases.edital.get_editais import GetEditaisUseCase
from app.domain.entities.user import User
from app.domain.entities.edital import Edital
from app.domain.exceptions.domain_exceptions import EditalNotFoundError
from app.presentation.api.v1.dependencies import (
    get_create_edital_use_case,
    get_editais_use_case,
    get_current_user
)


router = APIRouter()


def edital_to_response(edital: Edital) -> EditalResponse:
    """Converte entidade Edital para EditalResponse"""
    return EditalResponse(
        uuid=edital.uuid,
        apelido_edital=edital.apelido_edital,
        link=edital.link,
        financiador_1=edital.financiador_1,
        financiador_2=edital.financiador_2,
        area_foco=edital.area_foco,
        tipo_proponente=edital.tipo_proponente,
        empresas_que_podem_submeter=edital.empresas_que_podem_submeter,
        duracao_min_meses=edital.duracao_min_meses,
        duracao_max_meses=edital.duracao_max_meses,
        valor_min_R=edital.valor_min_R,
        valor_max_R=edital.valor_max_R,
        tipo_recurso=edital.tipo_recurso,
        recepcao_recursos=edital.recepcao_recursos,
        custeio=edital.custeio,
        capital=edital.capital,
        contrapartida_min_pct=edital.contrapartida_min_pct,
        contrapartida_max_pct=edital.contrapartida_max_pct,
        tipo_contrapartida=edital.tipo_contrapartida,
        data_inicial_submissao=edital.data_inicial_submissao,
        data_final_submissao=edital.data_final_submissao,
        data_resultado=edital.data_resultado,
        descricao_completa=edital.descricao_completa,
        origem=edital.origem,
        observacoes=edital.observacoes,
        status=edital.status,
        created_at=edital.created_at,
        updated_at=edital.updated_at
    )


@router.post("/editais", response_model=EditalResponse, status_code=status.HTTP_201_CREATED, tags=["editais"])
async def create_edital(
    edital_data: EditalCreateRequest,
    current_user: User = Depends(get_current_user),
    create_edital_uc: CreateEditalUseCase = Depends(get_create_edital_use_case)
):
    """
    Cria um novo edital manualmente.

    Campos obrigatórios:
    - apelido_edital: Nome/título do edital
    - link: URL do edital
    """
    edital = await create_edital_uc.execute(
        **edital_data.model_dump(by_alias=True, exclude_unset=True)
    )
    return edital_to_response(edital)


@router.get("/editais", response_model=List[EditalResponse], tags=["editais"])
async def read_editais(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    get_editais_uc: GetEditaisUseCase = Depends(get_editais_use_case)
):
    """
    Retorna lista de editais com paginação.
    """
    editais = await get_editais_uc.execute_all(skip, limit)
    return [edital_to_response(e) for e in editais]


@router.get("/editais/{edital_uuid}", response_model=EditalResponse, tags=["editais"])
async def read_edital(
    edital_uuid: str,
    current_user: User = Depends(get_current_user),
    get_editais_uc: GetEditaisUseCase = Depends(get_editais_use_case)
):
    """
    Retorna um edital específico.
    """
    try:
        edital = await get_editais_uc.execute_by_uuid(edital_uuid)
        return edital_to_response(edital)
    except EditalNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Edital not found"
        )
