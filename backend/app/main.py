from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
import uvicorn

from .api.endpoints import health, users, editais, projects
from .api.services.auth_service import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from .api.models.user import LoginRequest
from .db.mongodb import mongodb
from .db.chromadb import chromadb_client
from .core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para gerenciamento de editais com MongoDB e ChromaDB\n\n## 🔐 Autenticação\n\n**Para usar a API:**\n\n1. **Faça Login** no endpoint `/login` com seu email e senha\n2. **Copie o token JWT** retornado no campo `access_token`\n3. **Clique em 'Authorize' 🔓** no topo da página\n4. **Cole apenas o token** (sem a palavra 'Bearer')\n5. **Clique em 'Authorize'** e depois 'Close'\n\nAgora você pode usar todos os endpoints protegidos! 🎉",
    version="0.1.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Eventos de inicialização e encerramento
@app.on_event("startup")
async def startup_db_client():
    await mongodb.connect_to_database()
    chromadb_client.connect_to_database()

@app.on_event("shutdown")
async def shutdown_db_client():
    await mongodb.close_database_connection()

# Rota de autenticação - Login com email e senha
@app.post("/login", tags=["auth"])
async def login(credentials: LoginRequest):
    """
    Login com email e senha
    
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
    user = await authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    }

# Incluir routers
app.include_router(health.router, tags=["health"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(editais.router, prefix="/api", tags=["editais"])
app.include_router(projects.router, prefix="/api", tags=["projects"])

# Rota raiz
@app.get("/")
async def root():
    return {"message": "Bem-vindo à API de Editais"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
