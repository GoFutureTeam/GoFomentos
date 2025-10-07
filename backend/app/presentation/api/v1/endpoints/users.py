"""
User Endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List

from app.presentation.schemas.user_schema import UserCreateRequest, UserResponse
from app.application.use_cases.user.create_user import CreateUserUseCase
from app.application.use_cases.user.get_user import GetUserUseCase
from app.domain.entities.user import User
from app.domain.exceptions.domain_exceptions import UserAlreadyExistsError, UserNotFoundError
from app.presentation.api.v1.dependencies import get_create_user_use_case, get_user_use_case, get_current_user


router = APIRouter()


def user_to_response(user: User) -> UserResponse:
    """Converte entidade User para UserResponse"""
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["users"])
async def create_user(
    user_data: UserCreateRequest,
    create_user_uc: CreateUserUseCase = Depends(get_create_user_use_case)
):
    """
    Cria um novo usuário.
    """
    try:
        user = await create_user_uc.execute(
            email=user_data.email,
            password=user_data.password,
            name=user_data.name
        )
        return user_to_response(user)
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/users/me", response_model=UserResponse, tags=["users"])
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Retorna o usuário atual autenticado.
    """
    return user_to_response(current_user)


@router.get("/users/{user_id}", response_model=UserResponse, tags=["users"])
async def read_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    get_user_uc: GetUserUseCase = Depends(get_user_use_case)
):
    """
    Retorna um usuário específico.
    """
    try:
        user = await get_user_uc.execute_by_id(user_id)
        return user_to_response(user)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
