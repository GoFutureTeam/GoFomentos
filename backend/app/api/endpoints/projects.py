from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..models.user import User
from ..models.project import Project, ProjectCreate, ProjectUpdate
from ..services.mongo_service import MongoService
from ..services.auth_service import get_current_user

router = APIRouter()

@router.post("/projects", response_model=Project)
async def create_project(project: ProjectCreate, current_user: User = Depends(get_current_user)):
    """
    Cria um novo projeto
    """
    # Garantir que o usuário só pode criar projetos para si mesmo
    if project.user_id != current_user.id:
        project.user_id = current_user.id
    
    return await MongoService.create_project(project)

@router.get("/projects", response_model=List[Project])
async def read_projects(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user)):
    """
    Retorna lista de projetos do usuário atual
    """
    return await MongoService.get_user_projects(current_user.id, skip, limit)

@router.get("/projects/{project_id}", response_model=Project)
async def read_project(project_id: str, current_user: User = Depends(get_current_user)):
    """
    Retorna um projeto específico
    """
    project = await MongoService.get_project(project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Verificar se o projeto pertence ao usuário atual
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )
    
    return project

@router.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, project_update: ProjectUpdate, current_user: User = Depends(get_current_user)):
    """
    Atualiza um projeto
    """
    # Verificar se o projeto existe e pertence ao usuário atual
    project = await MongoService.get_project(project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this project"
        )
    
    updated_project = await MongoService.update_project(project_id, project_update)
    return updated_project

@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str, current_user: User = Depends(get_current_user)):
    """
    Deleta um projeto
    """
    # Verificar se o projeto existe e pertence ao usuário atual
    project = await MongoService.get_project(project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this project"
        )
    
    await MongoService.delete_project(project_id)
