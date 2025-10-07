"""
Authentication Endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends

from app.presentation.schemas.user_schema import LoginRequest, LoginResponse
from app.application.use_cases.user.authenticate_user import AuthenticateUserUseCase
from app.domain.exceptions.domain_exceptions import InvalidCredentialsError, UserInactiveError
from app.presentation.api.v1.dependencies import get_authenticate_user_use_case


router = APIRouter()


@router.post("/login", response_model=LoginResponse, tags=["auth"])
async def login(
    credentials: LoginRequest,
    authenticate_uc: AuthenticateUserUseCase = Depends(get_authenticate_user_use_case)
):
    """
    Login com email e senha.

    Retorna um JWT token que deve ser usado no header Authorization:

    ```
    Authorization: Bearer <seu_token_aqui>
    ```

    **Exemplo de requisição:**
    ```json
    {
        "email": "user@example.com",
        "password": "sua_senha"
    }
    ```

    **Resposta de sucesso:**
    ```json
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
        "user": {
            "id": "uuid",
            "email": "user@example.com",
            "name": "Nome do Usuário"
        }
    }
    ```
    """
    try:
        result = await authenticate_uc.execute(
            email=credentials.email,
            password=credentials.password
        )
        return result
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except UserInactiveError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
        )
