import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from ..core.config import settings
from ..api.services.auth_service import get_password_hash
from datetime import datetime
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_mongodb():
    """
    Inicializa o banco de dados MongoDB com dados de exemplo
    """
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB]
    
    # Criar usuário admin
    if await db.users.count_documents({"email": "admin@gofomentos.com"}) == 0:
        logger.info("Criando usuário administrador...")
        await db.users.insert_one({
            "id": str(uuid.uuid4()),
            "email": "admin@gofomentos.com",
            "name": "Administrador GoFomentos",
            "hashed_password": get_password_hash("admin123"),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        logger.info("✅ Usuário admin criado: admin@gofomentos.com / admin123")
    
    # Criar edital de exemplo
    if await db.editais.count_documents({}) == 0:
        logger.info("Criando edital de exemplo...")
        edital_uuid = str(uuid.uuid4())
        await db.editais.insert_one({
            "uuid": edital_uuid,
            "apelido_edital": "Edital de Inovação 2025",
            "financiador_1": "CNPQ",
            "financiador_2": "FINEP",
            "area_foco": "Tecnologia da Informação",
            "tipo_proponente": "Empresa de Base Tecnológica",
            "empresas_que_podem_submeter": "Startups e PMEs",
            "duracao_min_meses": 12,
            "duracao_max_meses": 24,
            "valor_min_R": 100000.0,
            "valor_max_R": 500000.0,
            "tipo_recurso": "Não reembolsável",
            "recepcao_recursos": "Parcelas trimestrais",
            "custeio": True,
            "capital": True,
            "contrapartida_min_pct": 10.0,
            "contrapartida_max_pct": 20.0,
            "tipo_contrapartida": "Financeira e econômica",
            "data_inicial_submissao": datetime(2025, 1, 1),
            "data_final_submissao": datetime(2025, 2, 28),
            "data_resultado": datetime(2025, 4, 15),
            "descricao_completa": "Edital para financiamento de projetos inovadores em tecnologia da informação.",
            "origem": "http://exemplo.gov.br/edital-2025",
            "link": "http://exemplo.gov.br/edital-2025",
            "observacoes": "Prioridade para projetos com impacto social.",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
    
    logger.info("Inicialização do MongoDB concluída!")

async def init_chromadb():
    """
    Inicializa o banco de dados ChromaDB com dados de exemplo
    """
    from ...db.chromadb import chromadb_client
    from ...processors.embedding_generator import EmbeddingGenerator
    
    logger.info("Inicializando ChromaDB...")
    
    # Verificar se já existem dados
    chromadb_client.connect_to_database()
    collection = chromadb_client.collection
    
    if collection.count() == 0:
        logger.info("Criando dados de exemplo no ChromaDB...")
        
        # Exemplo de chunks e metadados
        chunks = [
            "O presente edital tem como objetivo financiar projetos inovadores em tecnologia da informação.",
            "Os projetos devem ter duração entre 12 e 24 meses.",
            "O valor do financiamento varia de R$ 100.000,00 a R$ 500.000,00.",
            "A contrapartida mínima é de 10% e máxima de 20% do valor total.",
            "As inscrições estarão abertas de 01/01/2025 a 28/02/2025."
        ]
        
        edital_uuid = "exemplo-uuid-123"  # Substitua por um UUID real se necessário
        pdf_url = "http://exemplo.gov.br/edital-2025"
        page_numbers = [1, 1, 2, 2, 3]
        
        embedding_generator = EmbeddingGenerator()
        embedding_generator.generate_and_store_embeddings(
            chunks=chunks,
            edital_uuid=edital_uuid,
            pdf_url=pdf_url,
            page_numbers=page_numbers
        )
    
    logger.info("Inicialização do ChromaDB concluída!")

async def init_db():
    """
    Inicializa todos os bancos de dados
    """
    logger.info("Inicializando bancos de dados...")
    
    await init_mongodb()
    # Comentado porque o ChromaDB não é assíncrono e pode causar problemas
    # await init_chromadb()
    
    logger.info("Inicialização concluída!")

if __name__ == "__main__":
    asyncio.run(init_db())
