import chromadb
from chromadb.config import Settings as ChromaSettings
from ..core.config import settings

class ChromaDB:
    client = None
    collection = None

    def connect_to_database(self):
        """
        Conecta ao banco de dados ChromaDB
        """
        if self.client is None:
            try:
                # Para ambiente de desenvolvimento local
                if settings.CHROMA_HOST == "localhost" or settings.CHROMA_HOST == "127.0.0.1":
                    self.client = chromadb.Client(
                        ChromaSettings(
                            chroma_db_impl="duckdb+parquet",
                            persist_directory=".chroma"
                        )
                    )
                else:
                    # Para ambiente containerizado
                    self.client = chromadb.HttpClient(
                        host=settings.CHROMA_HOST,
                        port=settings.CHROMA_PORT
                    )
                
                # Cria ou obtém a coleção
                self.collection = self.client.get_or_create_collection(
                    name=settings.CHROMA_COLLECTION
                )
                print("Conectado ao ChromaDB!")
            except Exception as e:
                print(f"Aviso: Erro ao conectar ao ChromaDB: {e}")
                print("Continuando sem ChromaDB...")
                self.client = None
                self.collection = None

    def add_texts(self, texts, metadatas, ids):
        """
        Adiciona textos ao ChromaDB
        """
        if self.collection is None:
            self.connect_to_database()
        
        if self.collection is not None:
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
        else:
            print("ChromaDB não disponível - ignorando add_texts")

    def query(self, query_texts, n_results=5, where=None):
        """
        Realiza uma consulta no ChromaDB
        """
        if self.collection is None:
            self.connect_to_database()
        
        if self.collection is not None:
            return self.collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where=where
            )
        else:
            print("ChromaDB não disponível - retornando resultado vazio")
            return {"documents": [], "metadatas": [], "distances": []}


# Instância global do ChromaDB
chromadb_client = ChromaDB()
