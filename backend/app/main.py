"""
FastAPI Application - Entry Point
Refatorado seguindo Clean Architecture
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
import uvicorn

# Importar routers refatorados
from .presentation.api.v1.endpoints import auth, users, editais, projects, health, chroma, jobs

# Importar container singleton e configurações
from .core.container_instance import container
from .core.config import settings

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
API para gerenciamento de editais com MongoDB e ChromaDB (Clean Architecture)

## 🔐 Autenticação

**Para usar a API:**

1. **Faça Login** no endpoint `/login` com seu email e senha
2. **Copie o token JWT** retornado no campo `access_token`
3. **Clique em 'Authorize' 🔓** no topo da página
4. **Cole apenas o token** (sem a palavra 'Bearer')
5. **Clique em 'Authorize'** e depois 'Close'

Agora você pode usar todos os endpoints protegidos! 🎉

## 🏗️ Arquitetura

Esta API foi construída seguindo os princípios de **Clean Architecture** e **Domain-Driven Design (DDD)**:

- **Domain Layer**: Entidades e regras de negócio puras
- **Application Layer**: Casos de uso (orquestração)
- **Infrastructure Layer**: Implementações concretas (MongoDB, segurança)
- **Presentation Layer**: Controllers e schemas (FastAPI)

Benefícios:
- ✅ Código desacoplado e testável
- ✅ Fácil manutenção e escalabilidade
- ✅ Independência de frameworks e databases
""",
    version="2.0.0",
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
async def startup_event():
    """Inicializa conexões com bancos de dados"""
    print("🚀 Iniciando aplicação...")

    # Conectar MongoDB
    mongodb_conn = container.mongodb_connection()
    await mongodb_conn.connect()

    # Pré-carregar modelo ChromaDB (evita delay na primeira busca)
    try:
        chromadb = container.chromadb_service()
        chromadb.warmup()
    except Exception as e:
        print(f"⚠️ ChromaDB warmup falhou (não crítico): {e}")

    # Inicializar scheduler de jobs
    scheduler = container.job_scheduler_service()
    scheduler.start()
    print("✅ Job Scheduler iniciado (agendado para 01:00 AM)")

    print("✅ Aplicação iniciada com sucesso!")


@app.on_event("shutdown")
async def shutdown_event():
    """Fecha conexões com bancos de dados"""
    print("🛑 Encerrando aplicação...")

    # Parar scheduler
    scheduler = container.job_scheduler_service()
    scheduler.shutdown()
    print("✅ Job Scheduler encerrado")

    # Encerrar executor de processos dos scrapers
    cnpq_scraper = container.cnpq_scraper_service()
    cnpq_scraper.shutdown()
    print("✅ CNPq Scraper executor encerrado")

    fapesq_scraper = container.fapesq_scraper_service()
    fapesq_scraper.shutdown()
    print("✅ FAPESQ Scraper executor encerrado")

    # Desconectar MongoDB
    mongodb_conn = container.mongodb_connection()
    await mongodb_conn.disconnect()

    print("✅ Aplicação encerrada!")


# Incluir routers (nova estrutura)
app.include_router(auth.router, tags=["auth"])
app.include_router(health.router, tags=["health"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(editais.router, prefix="/api/v1", tags=["editais"])
app.include_router(projects.router, prefix="/api/v1", tags=["projects"])
app.include_router(chroma.router, prefix="/api", tags=["chroma"])  # Sem v1 para compatibilidade com visualizer
app.include_router(jobs.router, prefix="/api/v1", tags=["jobs"])


# Rota raiz
@app.get("/")
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "Bem-vindo à API de Editais - Clean Architecture",
        "version": "2.0.0",
        "architecture": "Clean Architecture + DDD",
        "docs": "/docs",
        "health": "/health"
    }


# Rota para servir o visualizador do ChromaDB
@app.get("/visualizer")
async def visualizar_chroma():
    """
    Serve o visualizador do ChromaDB.
    Interface web para visualizar os dados armazenados no ChromaDB.
    """
    html_path = Path(__file__).parent / "presentation" / "static" / "visualizar_chroma.html"
    if html_path.exists():
        return FileResponse(html_path)
    return {
        "message": "Visualizer not found",
        "expected_path": str(html_path),
        "hint": "Make sure visualizar_chroma.html is in app/presentation/static/"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
