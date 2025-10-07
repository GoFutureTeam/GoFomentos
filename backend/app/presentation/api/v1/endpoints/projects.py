"""
Project Endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List

from app.presentation.schemas.project_schema import ProjectCreateRequest, ProjectResponse
from app.application.use_cases.project.create_project import CreateProjectUseCase
from app.application.use_cases.project.get_projects import GetProjectsUseCase
from app.domain.entities.user import User
from app.domain.entities.project import Project
from app.domain.exceptions.domain_exceptions import ProjectNotFoundError, ProjectAccessDeniedError
from app.presentation.api.v1.dependencies import (
    get_create_project_use_case,
    get_projects_use_case,
    get_current_user
)


router = APIRouter()


def project_to_response(project: Project) -> ProjectResponse:
    """Converte entidade Project para ProjectResponse"""
    return ProjectResponse(
        id=project.id,
        titulo_projeto=project.titulo_projeto,
        objetivo_principal=project.objetivo_principal,
        nome_empresa=project.nome_empresa,
        resumo_atividades=project.resumo_atividades,
        cnae=project.cnae,
        user_id=project.user_id,
        documento_url=project.documento_url,
        edital_uuid=project.edital_uuid,
        created_at=project.created_at,
        updated_at=project.updated_at
    )


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED, tags=["projects"])
async def create_project(
    project_data: ProjectCreateRequest,
    current_user: User = Depends(get_current_user),
    create_project_uc: CreateProjectUseCase = Depends(get_create_project_use_case)
):
    """
    Cria um novo projeto.
    """
    project = await create_project_uc.execute(
        titulo_projeto=project_data.titulo_projeto,
        objetivo_principal=project_data.objetivo_principal,
        nome_empresa=project_data.nome_empresa,
        resumo_atividades=project_data.resumo_atividades,
        cnae=project_data.cnae,
        user_id=current_user.id,
        documento_url=project_data.documento_url,
        edital_uuid=project_data.edital_uuid
    )
    return project_to_response(project)


@router.get("/projects/me", response_model=List[ProjectResponse], tags=["projects"])
async def read_my_projects(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    get_projects_uc: GetProjectsUseCase = Depends(get_projects_use_case)
):
    """
    Retorna todos os projetos do usuário autenticado.
    """
    projects = await get_projects_uc.execute_by_user(current_user.id, skip, limit)
    return [project_to_response(p) for p in projects]


@router.get("/projects/{project_id}", response_model=ProjectResponse, tags=["projects"])
async def read_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    get_projects_uc: GetProjectsUseCase = Depends(get_projects_use_case)
):
    """
    Retorna um projeto específico.
    """
    try:
        project = await get_projects_uc.execute_by_id(project_id, current_user.id)
        return project_to_response(project)
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    except ProjectAccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )
