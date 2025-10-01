from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..models.user import User, UserCreate, UserUpdate
from ..services.mongo_service import MongoService
from ..services.auth_service import get_current_user

router = APIRouter()

@router.post("/users", response_model=User)
async def create_user(user: UserCreate):
    """
    Cria um novo usuário
    """
    try:
        return await MongoService.create_user(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Retorna o usuário atual
    """
    return current_user

@router.get("/users/{user_id}", response_model=User)
async def read_user(user_id: str, current_user: User = Depends(get_current_user)):
    """
    Retorna um usuário específico
    """
    user = await MongoService.get_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, user_update: UserUpdate, current_user: User = Depends(get_current_user)):
    """
    Atualiza um usuário
    """
    # Verificar se o usuário está atualizando seu próprio perfil ou é um admin
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    updated_user = await MongoService.update_user(user_id, user_update)
    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, current_user: User = Depends(get_current_user)):
    """
    Deleta um usuário
    """
    # Verificar se o usuário está deletando seu próprio perfil ou é um admin
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )
    
    result = await MongoService.delete_user(user_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
