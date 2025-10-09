"""
Dependency Injection Container - Gerencia todas as dependências da aplicação
"""
from dependency_injector import containers, providers

# Infrastructure
from ..infrastructure.persistence.mongodb.connection import MongoDBConnection
from ..infrastructure.persistence.mongodb.user_repository_impl import MongoUserRepository
from ..infrastructure.persistence.mongodb.edital_repository_impl import MongoEditalRepository
from ..infrastructure.persistence.mongodb.project_repository_impl import MongoProjectRepository
from ..infrastructure.persistence.mongodb.job_repository_impl import MongoJobRepository
from ..infrastructure.persistence.mongodb.conversation_repository_impl import ConversationRepositoryImpl
from ..infrastructure.security.password_service import Argon2PasswordService
from ..infrastructure.security.jwt_service import JWTService

# Application Services
from ..application.services.cnpq_scraper_service import CNPqScraperService
from ..application.services.fapesq_scraper_service import FapesqScraperService
from ..application.services.paraiba_gov_scraper_service import ParaibaGovScraperService
from ..application.services.confap_scraper_service import ConfapScraperService
from ..application.services.capes_scraper_service import CapesScraperService
from ..application.services.finep_scraper_service import FinepScraperService
from ..application.services.openai_extractor_service import OpenAIExtractorService
from ..application.services.job_scheduler_service import JobSchedulerService
from ..application.services.chromadb_service import ChromaDBService
from ..application.services.chat_service import ChatService

# Use Cases - User
from ..application.use_cases.user.create_user import CreateUserUseCase
from ..application.use_cases.user.authenticate_user import AuthenticateUserUseCase
from ..application.use_cases.user.get_user import GetUserUseCase

# Use Cases - Edital
from ..application.use_cases.edital.create_edital import CreateEditalUseCase
from ..application.use_cases.edital.get_editais import GetEditaisUseCase

# Use Cases - Project
from ..application.use_cases.project.create_project import CreateProjectUseCase
from ..application.use_cases.project.get_projects import GetProjectsUseCase

from .config import settings


class Container(containers.DeclarativeContainer):
    """
    Container de injeção de dependências.
    Centraliza a criação e gerenciamento de todas as dependências da aplicação.
    """

    # Configuration
    config = providers.Configuration()

    # Database Connection
    mongodb_connection = providers.Singleton(
        MongoDBConnection,
        uri=settings.MONGO_URI,
        database_name=settings.MONGO_DB
    )

    # Security Services
    password_service = providers.Singleton(
        Argon2PasswordService
    )

    jwt_service = providers.Singleton(
        JWTService,
        secret_key=settings.SECRET_KEY,
        algorithm="HS256",
        expiration_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Repositories
    user_repository = providers.Factory(
        MongoUserRepository,
        db_connection=mongodb_connection
    )

    edital_repository = providers.Factory(
        MongoEditalRepository,
        db_connection=mongodb_connection
    )

    project_repository = providers.Factory(
        MongoProjectRepository,
        db_connection=mongodb_connection
    )

    job_repository = providers.Factory(
        MongoJobRepository,
        db_connection=mongodb_connection
    )

    conversation_repository = providers.Factory(
        ConversationRepositoryImpl,
        database=mongodb_connection.provided.db
    )

    # Use Cases - User
    create_user_use_case = providers.Factory(
        CreateUserUseCase,
        user_repository=user_repository,
        password_service=password_service
    )

    authenticate_user_use_case = providers.Factory(
        AuthenticateUserUseCase,
        user_repository=user_repository,
        password_service=password_service,
        jwt_service=jwt_service
    )

    get_user_use_case = providers.Factory(
        GetUserUseCase,
        user_repository=user_repository
    )

    # Use Cases - Edital
    create_edital_use_case = providers.Factory(
        CreateEditalUseCase,
        edital_repository=edital_repository
    )

    get_editais_use_case = providers.Factory(
        GetEditaisUseCase,
        edital_repository=edital_repository
    )

    # Use Cases - Project
    create_project_use_case = providers.Factory(
        CreateProjectUseCase,
        project_repository=project_repository
    )

    get_projects_use_case = providers.Factory(
        GetProjectsUseCase,
        project_repository=project_repository
    )

    # Application Services - ChromaDB
    chromadb_service = providers.Singleton(
        ChromaDBService,
        chroma_host=settings.CHROMA_HOST,
        chroma_port=settings.CHROMA_PORT,
        openai_api_key=settings.OPENAI_API_KEY  # ⭐ Passar API key para embeddings da OpenAI
    )

    # Application Services - Jobs
    cnpq_scraper_service = providers.Factory(
        CNPqScraperService,
        max_workers=settings.JOB_MAX_WORKERS
    )

    fapesq_scraper_service = providers.Factory(
        FapesqScraperService,
        max_workers=settings.JOB_MAX_WORKERS
    )

    paraiba_gov_scraper_service = providers.Factory(
        ParaibaGovScraperService,
        max_workers=settings.JOB_MAX_WORKERS
    )

    confap_scraper_service = providers.Factory(
        ConfapScraperService,
        max_workers=settings.JOB_MAX_WORKERS
    )

    capes_scraper_service = providers.Factory(
        CapesScraperService,
        max_workers=settings.JOB_MAX_WORKERS
    )

    finep_scraper_service = providers.Factory(
        FinepScraperService,
        max_workers=settings.JOB_MAX_WORKERS
    )

    openai_extractor_service = providers.Factory(
        OpenAIExtractorService,
        openai_api_key=config.OPENAI_API_KEY,
        edital_repository=edital_repository,
        chromadb_service=chromadb_service,
        chunk_delay_ms=settings.JOB_CHUNK_DELAY_MS
    )

    job_scheduler_service = providers.Singleton(
        JobSchedulerService,
        job_repository=job_repository,
        edital_repository=edital_repository,
        cnpq_scraper_service=cnpq_scraper_service,
        fapesq_scraper_service=fapesq_scraper_service,
        paraiba_gov_scraper_service=paraiba_gov_scraper_service,
        confap_scraper_service=confap_scraper_service,
        capes_scraper_service=capes_scraper_service,
        finep_scraper_service=finep_scraper_service,
        openai_service=openai_extractor_service,
        pdf_processing_delay_ms=settings.JOB_PDF_PROCESSING_DELAY_MS
    )

    # Application Services - Chat (RAG)
    chat_service = providers.Factory(
        ChatService,
        openai_api_key=settings.OPENAI_API_KEY,
        chromadb_service=chromadb_service,
        conversation_repository=conversation_repository,
        model=settings.CHAT_MODEL,
        temperature=settings.CHAT_TEMPERATURE,
        top_k_chunks=settings.CHAT_TOP_K_CHUNKS,
        max_context_length=settings.CHAT_MAX_CONTEXT_LENGTH,
        distance_threshold=settings.CHAT_DISTANCE_THRESHOLD
    )
