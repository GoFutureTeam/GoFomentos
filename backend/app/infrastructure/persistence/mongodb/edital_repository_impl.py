"""
MongoDB Edital Repository Implementation
"""
from typing import Optional, List
from ....domain.entities.edital import Edital
from ....domain.repositories.edital_repository import EditalRepository
from ....domain.exceptions.domain_exceptions import EditalNotFoundError
from .connection import MongoDBConnection


class MongoEditalRepository(EditalRepository):
    """
    Implementação concreta do EditalRepository usando MongoDB.
    """

    def __init__(self, db_connection: MongoDBConnection):
        """
        Inicializa o repositório.

        Args:
            db_connection: Conexão com MongoDB
        """
        self.db_connection = db_connection
        self.collection_name = "editais"

    def _get_collection(self):
        """Retorna a coleção de editais"""
        return self.db_connection.get_collection(self.collection_name)

    async def create(self, edital: Edital) -> Edital:
        """Cria um novo edital"""
        collection = self._get_collection()
        await collection.insert_one(edital.to_dict())
        return edital

    async def find_by_uuid(self, edital_uuid: str) -> Optional[Edital]:
        """Busca edital por UUID"""
        collection = self._get_collection()
        data = await collection.find_one({"uuid": edital_uuid})

        if data:
            # Remove _id do MongoDB antes de converter
            data.pop('_id', None)
            return Edital.from_dict(data)
        return None

    async def find_all(self, skip: int = 0, limit: int = 100) -> List[Edital]:
        """Busca todos os editais com paginação"""
        collection = self._get_collection()
        cursor = collection.find().skip(skip).limit(limit)
        editais_data = await cursor.to_list(length=limit)

        # Remove _id do MongoDB antes de converter
        return [Edital.from_dict({k: v for k, v in data.items() if k != '_id'}) for data in editais_data]

    async def find_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Edital]:
        """Busca editais por status"""
        collection = self._get_collection()
        cursor = collection.find({"status": status}).skip(skip).limit(limit)
        editais_data = await cursor.to_list(length=limit)

        # Remove _id do MongoDB antes de converter
        return [Edital.from_dict({k: v for k, v in data.items() if k != '_id'}) for data in editais_data]

    async def find_by_financiador(self, financiador: str, skip: int = 0, limit: int = 100) -> List[Edital]:
        """Busca editais por financiador"""
        collection = self._get_collection()
        query = {
            "$or": [
                {"financiador_1": {"$regex": financiador, "$options": "i"}},
                {"financiador_2": {"$regex": financiador, "$options": "i"}}
            ]
        }
        cursor = collection.find(query).skip(skip).limit(limit)
        editais_data = await cursor.to_list(length=limit)

        # Remove _id do MongoDB antes de converter
        return [Edital.from_dict({k: v for k, v in data.items() if k != '_id'}) for data in editais_data]

    async def update(self, edital: Edital) -> Edital:
        """Atualiza um edital existente"""
        collection = self._get_collection()

        # Verificar se o edital existe
        existing = await collection.find_one({"uuid": edital.uuid})
        if not existing:
            raise EditalNotFoundError(edital.uuid)

        # Atualizar edital
        await collection.update_one(
            {"uuid": edital.uuid},
            {"$set": edital.to_dict()}
        )

        return edital

    async def delete(self, edital_uuid: str) -> bool:
        """Deleta um edital"""
        collection = self._get_collection()
        result = await collection.delete_one({"uuid": edital_uuid})
        return result.deleted_count > 0

    async def exists_by_link(self, link: str) -> bool:
        """Verifica se um edital com o link existe"""
        collection = self._get_collection()
        count = await collection.count_documents({"link": link})
        return count > 0

    async def save_partial_extraction(
        self,
        edital_uuid: str,
        chunk_index: int,
        variables: dict,
        status: str = "in_progress"
    ) -> None:
        """
        Salva extração parcial de variáveis (por chunk).
        Adiciona ao array extraction_chunks.
        """
        from datetime import datetime
        collection = self._get_collection()

        chunk_data = {
            "chunk_index": chunk_index,
            "extracted_at": datetime.utcnow(),
            "variables": variables
        }

        # Atualizar ou criar o edital com o chunk
        await collection.update_one(
            {"uuid": edital_uuid},
            {
                "$set": {
                    "extraction_status": status,
                    "updated_at": datetime.utcnow()
                },
                "$push": {"extraction_chunks": chunk_data}
            },
            upsert=True
        )

    async def save_final_extraction(
        self,
        edital_uuid: str,
        consolidated_variables: dict,
        status: str = "completed"
    ) -> None:
        """
        Salva extração final consolidada de variáveis.
        Atualiza os campos principais do edital com as variáveis consolidadas.
        """
        from datetime import datetime
        collection = self._get_collection()

        print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] 🔗 DEBUG REPO: Link recebido no save_final_extraction: '{consolidated_variables.get('link')}'")

        # Preparar dados consolidados
        update_data = {
            "extraction_status": status,
            "consolidated_variables": consolidated_variables,
            "updated_at": datetime.utcnow()
        }

        # Adicionar variáveis consolidadas aos campos principais
        # (para facilitar busca e consumo pelo frontend)
        for key, value in consolidated_variables.items():
            if key == "uuid":
                continue
            if value is not None:
                update_data[key] = value

        print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] 🔗 DEBUG REPO: Link em update_data: '{update_data.get('link')}'")

        # Atualizar edital
        await collection.update_one(
            {"uuid": edital_uuid},
            {"$set": update_data}
        )
