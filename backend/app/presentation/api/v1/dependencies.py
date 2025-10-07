"""
FastAPI Dependencies - Fornece dependências para os endpoints
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Callable

from app.core.container_instance import container
from app.domain.entities.user import User
from app.domain.exceptions.domain_exceptions import InvalidTokenError, UserNotFoundError

# Security
security = HTTPBearer()


# Dependency Injection helpers
def get_create_user_use_case():
    """Retorna o caso de uso de criação de usuário"""
    return container.create_user_use_case()


def get_authenticate_user_use_case():
    """Retorna o caso de uso de autenticação"""
    return container.authenticate_user_use_case()


def get_user_use_case():
    """Retorna o caso de uso de obter usuário"""
    return container.get_user_use_case()


def get_create_edital_use_case():
    """Retorna o caso de uso de criação de edital"""
    return container.create_edital_use_case()


def get_editais_use_case():
    """Retorna o caso de uso de obter editais"""
    return container.get_editais_use_case()


def get_create_project_use_case():
    """Retorna o caso de uso de criação de projeto"""
    return container.create_project_use_case()


def get_projects_use_case():
    """Retorna o caso de uso de obter projetos"""
    return container.get_projects_use_case()


def get_job_repository():
    """Retorna o repositório de jobs"""
    return container.job_repository()


def get_job_scheduler():
    """Retorna o serviço de scheduler"""
    return container.job_scheduler_service()


# Authentication dependency
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    get_user_uc = Depends(get_user_use_case)
) -> User:
    """
    Dependency para obter o usuário autenticado a partir do token JWT.

    Args:
        credentials: Credenciais do header Authorization
        get_user_uc: Use case para obter usuário

    Returns:
        User: Usuário autenticado

    Raises:
        HTTPException: Se o token for inválido ou o usuário não existir
    """
    try:
        # Extrair token
        token = credentials.credentials

        # Decodificar token e obter email
        jwt_service = container.jwt_service()
        email = jwt_service.extract_subject(token)

        # Buscar usuário
        user = await get_user_uc.execute_by_email(email)

        return user

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erro na autenticação",
            headers={"WWW-Authenticate": "Bearer"},
        )
