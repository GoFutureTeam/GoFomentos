"""
ChromaDB Service - Gerenciamento de vetorização e armazenamento
"""
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class ChromaDBService:
    """
    Serviço para vetorização e armazenamento de chunks no ChromaDB.
    """

    def __init__(self, chroma_host: str = "chroma", chroma_port: int = 8000, openai_api_key: str = None):
        """
        Inicializa conexão com ChromaDB.

        Args:
            chroma_host: Host do ChromaDB
            chroma_port: Porta do ChromaDB
            openai_api_key: Chave da API OpenAI para embeddings
        """
        self.client = chromadb.HttpClient(
            host=chroma_host,
            port=chroma_port,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        self.openai_api_key = openai_api_key
        self.collection_name = "editais_chunks"
        self._ensure_collection()

    def _ensure_collection(self):
        """
        Garante que a coleção existe com modelo de embedding da OpenAI.

        Modelo: text-embedding-3-small
        - Otimizado para múltiplas línguas (incluindo português)
        - 1536 dimensões
        - Excelente para textos técnicos e documentos formais
        - Mais preciso que modelos gratuitos
        - Custo: ~$0.02 por 1M tokens
        """
        try:
            # ⭐ EMBEDDING DA OPENAI - Melhor qualidade para português!
            openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=self.openai_api_key,
                model_name="text-embedding-3-small"
            )

            # ⚠️ SEMPRE RECRIAR COLLECTION PARA GARANTIR EMBEDDING CORRETO
            # Verificar se collection existe
            try:
                existing_collection = self.client.get_collection(
                    name=self.collection_name,
                    embedding_function=openai_ef  # ✅ FORÇA USO DO OPENAI EMBEDDING
                )
                
                # Verificar se está usando embedding correto
                collection_metadata = existing_collection.metadata
                if collection_metadata and collection_metadata.get("embedding_provider") == "OpenAI":
                    # Collection já usa OpenAI, pode usar
                    self.collection = existing_collection
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ ChromaDB collection '{self.collection_name}' encontrada com OpenAI embeddings")
                else:
                    # Collection existe mas usa embedding errado, deletar e recriar
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Collection existente usa embedding incorreto. Recriando com OpenAI...")
                    self.client.delete_collection(name=self.collection_name)
                    self.collection = self.client.create_collection(
                        name=self.collection_name,
                        embedding_function=openai_ef,
                        metadata={
                            "description": "Chunks de editais vetorizados",
                            "embedding_model": "text-embedding-3-small",
                            "embedding_provider": "OpenAI",
                            "language": "pt-BR",
                            "optimized_for": "technical documents in Portuguese"
                        }
                    )
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ ChromaDB collection '{self.collection_name}' recriada com OpenAI embeddings")
            except Exception:
                # Collection não existe, criar nova com OpenAI embeddings
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    embedding_function=openai_ef,
                    metadata={
                        "description": "Chunks de editais vetorizados",
                        "embedding_model": "text-embedding-3-small",
                        "embedding_provider": "OpenAI",
                        "language": "pt-BR",
                        "optimized_for": "technical documents in Portuguese"
                    }
                )
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ ChromaDB collection '{self.collection_name}' criada com OpenAI embeddings")
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro ao conectar ChromaDB: {e}")
            raise

    def warmup(self):
        """
        Pré-carrega o modelo de embeddings fazendo uma query dummy.
        Evita delay na primeira busca real.
        """
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔥 Warming up ChromaDB embedding model...")
            # Query simples para forçar download do modelo
            self.collection.query(
                query_texts=["test"],
                n_results=1
            )
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ ChromaDB model ready")
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Warmup failed (não crítico): {e}")

    async def add_chunk(
        self,
        chunk_text: str,
        edital_uuid: str,
        edital_name: str,
        chunk_index: int,
        total_chunks: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Adiciona um chunk vetorizado ao ChromaDB.

        Args:
            chunk_text: Texto do chunk
            edital_uuid: UUID do edital
            edital_name: Nome/apelido do edital
            chunk_index: Índice do chunk
            total_chunks: Total de chunks
            metadata: Metadados adicionais (opcional)

        Returns:
            str: ID do documento no ChromaDB
        """
        # Gerar ID único para o chunk
        chunk_id = f"{edital_uuid}_chunk_{chunk_index}"

        # Preparar metadados
        chunk_metadata = {
            "edital_uuid": edital_uuid,
            "edital_name": edital_name or "Sem nome",
            "chunk_index": chunk_index,
            "total_chunks": total_chunks,
            "created_at": datetime.utcnow().isoformat(),
        }

        # Adicionar metadados customizados
        if metadata:
            for key, value in metadata.items():
                # ChromaDB aceita apenas strings, ints, floats e booleans
                if isinstance(value, (str, int, float, bool)):
                    chunk_metadata[key] = value
                elif value is not None:
                    chunk_metadata[key] = str(value)

        try:
            # Adicionar ao ChromaDB (vetorização automática)
            self.collection.add(
                documents=[chunk_text],
                metadatas=[chunk_metadata],
                ids=[chunk_id]
            )

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 Chunk {chunk_index}/{total_chunks} vetorizado no ChromaDB: {edital_name}")
            return chunk_id

        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro ao vetorizar chunk {chunk_index}: {e}")
            raise

    async def search_similar(
        self,
        query: str,
        n_results: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca chunks similares usando busca vetorial.

        Args:
            query: Texto da consulta
            n_results: Número de resultados
            filter_metadata: Filtros de metadados

        Returns:
            List[Dict]: Lista de resultados
        """
        try:
            where_filter = filter_metadata if filter_metadata else None

            # ⭐ LOG: Verificar embedding function ativa
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 Iniciando busca vetorial...")
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📝 Query: '{query[:100]}...'")
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔢 Buscando {n_results} resultados")

            # Verificar qual embedding function está sendo usada
            if hasattr(self.collection, '_embedding_function'):
                ef_type = type(self.collection._embedding_function).__name__
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚙️ Embedding Function: {ef_type}")

            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter
            )

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ ChromaDB retornou {len(results.get('ids', [[]])[0])} chunks")

            # Formatar resultados
            formatted_results = []
            if results['documents'] and len(results['documents']) > 0:
                for i in range(len(results['documents'][0])):
                    chunk_id = results['ids'][0][i]
                    distance = results['distances'][0][i] if results['distances'] else None
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}

                    # ⭐ LOG: Mostrar cada chunk retornado
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📄 Chunk {i+1}: {chunk_id} | Distance: {distance:.4f} | Index: {metadata.get('chunk_index')}")

                    formatted_results.append({
                        "id": chunk_id,
                        "text": results['documents'][0][i],
                        "metadata": metadata,
                        "distance": distance
                    })

            return formatted_results

        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro na busca vetorial: {e}")
            return []

    async def get_all_documents(self) -> Dict[str, Any]:
        """
        Retorna todos os documentos da coleção.

        Returns:
            Dict: Documentos com metadados
        """
        try:
            result = self.collection.get()
            return {
                "ids": result.get('ids', []),
                "documents": result.get('documents', []),
                "metadatas": result.get('metadatas', []),
                "total": len(result.get('ids', []))
            }
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro ao buscar documentos: {e}")
            return {"ids": [], "documents": [], "metadatas": [], "total": 0}

    async def delete_by_edital(self, edital_uuid: str) -> int:
        """
        Deleta todos os chunks de um edital.

        Args:
            edital_uuid: UUID do edital

        Returns:
            int: Número de chunks deletados
        """
        try:
            # Buscar todos os chunks do edital
            result = self.collection.get(
                where={"edital_uuid": edital_uuid}
            )

            ids_to_delete = result.get('ids', [])
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🗑️ {len(ids_to_delete)} chunks deletados do ChromaDB")
                return len(ids_to_delete)

            return 0

        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro ao deletar chunks: {e}")
            return 0

    async def clear_collection(self) -> bool:
        """
        Limpa toda a coleção.

        Returns:
            bool: True se sucesso
        """
        try:
            self.client.delete_collection(self.collection_name)
            self._ensure_collection()  # Recriar coleção vazia
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🗑️ Coleção ChromaDB limpa")
            return True
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro ao limpar coleção: {e}")
            return False

    async def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas da coleção.

        Returns:
            Dict: Estatísticas
        """
        try:
            result = self.collection.get()
            total_docs = len(result.get('ids', []))

            # Contar editais únicos
            unique_editais = set()
            if result.get('metadatas'):
                for metadata in result['metadatas']:
                    if 'edital_uuid' in metadata:
                        unique_editais.add(metadata['edital_uuid'])

            # ⭐ VERIFICAR EMBEDDING FUNCTION ATIVA
            embedding_info = {
                "model": "UNKNOWN",
                "provider": "UNKNOWN"
            }
            try:
                # Tentar pegar metadados da coleção
                collection_metadata = self.collection.metadata
                if collection_metadata:
                    embedding_info["model"] = collection_metadata.get("embedding_model", "UNKNOWN")
                    embedding_info["provider"] = collection_metadata.get("embedding_provider", "UNKNOWN")

                # Verificar tipo da embedding function
                if hasattr(self.collection, '_embedding_function'):
                    ef = self.collection._embedding_function
                    embedding_info["function_type"] = str(type(ef).__name__)
            except Exception as e:
                embedding_info["error"] = str(e)

            return {
                "total_chunks": total_docs,
                "total_editais": len(unique_editais),
                "collection_name": self.collection_name,
                "unique_editais_ids": list(unique_editais),
                "embedding_info": embedding_info  # ⭐ ADICIONAR INFO DO MODELO
            }

        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro ao obter estatísticas: {e}")
            return {
                "total_chunks": 0,
                "total_editais": 0,
                "collection_name": self.collection_name,
                "error": str(e)
            }
