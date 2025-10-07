"""
User Schemas - Modelos Pydantic para request/response de usuários
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


# Request Schemas
class UserCreateRequest(BaseModel):
    """Schema para criação de usuário"""
    email: EmailStr
    password: str = Field(..., min_length=6, description="Senha com no mínimo 6 caracteres")
    name: str = Field(..., min_length=2, description="Nome completo do usuário")


class UserUpdateRequest(BaseModel):
    """Schema para atualização de usuário"""
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=2)
    password: Optional[str] = Field(None, min_length=6)


class LoginRequest(BaseModel):
    """Schema para login"""
    email: EmailStr
    password: str


# Response Schemas
class UserResponse(BaseModel):
    """Schema de resposta para usuário (sem senha)"""
    id: str
    email: str
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Schema de resposta para login"""
    access_token: str
    token_type: str
    user: dict
