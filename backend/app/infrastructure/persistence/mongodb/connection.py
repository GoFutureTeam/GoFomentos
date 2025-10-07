"""
MongoDB Connection Manager - Gerencia conexão com MongoDB
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional


class MongoDBConnection:
    """
    Gerenciador de conexão com MongoDB.
    Implementa padrão Singleton para garantir uma única instância de conexão.
    """

    def __init__(self, uri: str, database_name: str):
        """
        Inicializa o gerenciador de conexão.

        Args:
            uri: URI de conexão do MongoDB
            database_name: Nome do banco de dados
        """
        self.uri = uri
        self.database_name = database_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None

    async def connect(self) -> None:
        """Estabelece conexão com o MongoDB"""
        if self.client is None:
            try:
                print(f"Conectando ao MongoDB: {self.uri}")
                self.client = AsyncIOMotorClient(self.uri)
                self.db = self.client[self.database_name]

                # Testar a conexão
                await self.client.server_info()
                print("✅ Conectado ao MongoDB!")
            except Exception as e:
                print(f"❌ Erro ao conectar ao MongoDB: {e}")
                raise e

    async def disconnect(self) -> None:
        """Fecha a conexão com o MongoDB"""
        if self.client is not None:
            self.client.close()
            self.client = None
            self.db = None
            print("✅ Conexão com MongoDB fechada!")

    def get_database(self) -> AsyncIOMotorDatabase:
        """
        Retorna a instância do banco de dados.

        Returns:
            AsyncIOMotorDatabase: Instância do banco

        Raises:
            RuntimeError: Se a conexão não foi estabelecida
        """
        if self.db is None:
            raise RuntimeError("Database connection not established. Call connect() first.")
        return self.db

    def get_collection(self, collection_name: str):
        """
        Retorna uma coleção do MongoDB.

        Args:
            collection_name: Nome da coleção

        Returns:
            AsyncIOMotorCollection: Coleção do MongoDB
        """
        return self.get_database()[collection_name]
