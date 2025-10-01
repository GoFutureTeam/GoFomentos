from datetime import datetime, timedelta
from typing import Optional
import os
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..models.user import User, UserInDB
from ...db.mongodb import mongodb
from ...core.config import settings

# Configurações de segurança
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
 
# Usa argon2 - algoritmo moderno e seguro, sem limitações de tamanho
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# HTTPBearer para aceitar apenas JWT token no header Authorization
security = HTTPBearer()


def verify_password(plain_password, hashed_password):
    # Argon2 é mais seguro e moderno que bcrypt
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    # Argon2 não tem limitação de tamanho de senha
    return pwd_context.hash(password)


async def get_user(email: str):
    users_collection = mongodb.get_collection("users")
    user = await users_collection.find_one({"email": email})
    if user:
        return UserInDB(**user)


async def authenticate_user(email: str, password: str):
    user = await get_user(email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Valida o JWT token e retorna o usuário autenticado"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Extrai o token do header Authorization
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user(email)
    if user is None:
        raise credentials_exception
    return user
