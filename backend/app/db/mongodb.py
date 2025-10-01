from motor.motor_asyncio import AsyncIOMotorClient
from ..core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    async def connect_to_database(self):
        """
        Conecta ao banco de dados MongoDB
        """
        if self.client is None:
            try:
                # Usar a URI configurada (funciona tanto em container quanto local)
                mongo_uri = settings.MONGO_URI
                
                print(f"Tentando conectar ao MongoDB: {mongo_uri}")
                self.client = AsyncIOMotorClient(mongo_uri)
                self.db = self.client[settings.MONGO_DB]
                
                # Testar a conexão
                await self.client.server_info()
                print("Conectado ao MongoDB!")
            except Exception as e:
                print(f"Erro ao conectar ao MongoDB: {e}")
                raise e

    async def close_database_connection(self):
        """
        Fecha a conexão com o banco de dados
        """
        if self.client is not None:
            self.client.close()
            print("Conexão com MongoDB fechada!")

    def get_collection(self, collection_name: str):
        """
        Retorna uma coleção do MongoDB
        """
        return self.db[collection_name]


# Instância global do MongoDB
mongodb = MongoDB()
