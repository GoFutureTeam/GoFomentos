"""
MongoDB Job Repository Implementation
"""
from typing import Optional, List
from ....domain.entities.job_execution import JobExecution
from ....domain.repositories.job_repository import JobRepository
from .connection import MongoDBConnection


class MongoJobRepository(JobRepository):
    """
    Implementação concreta do JobRepository usando MongoDB.
    """

    def __init__(self, db_connection: MongoDBConnection):
        """
        Inicializa o repositório.

        Args:
            db_connection: Conexão com MongoDB
        """
        self.db_connection = db_connection
        self.collection_name = "job_executions"

    def _get_collection(self):
        """Retorna a coleção de jobs"""
        return self.db_connection.get_collection(self.collection_name)

    async def create(self, job: JobExecution) -> JobExecution:
        """Cria uma nova execução de job"""
        collection = self._get_collection()
        await collection.insert_one(job.to_dict())
        return job

    async def find_by_id(self, job_id: str) -> Optional[JobExecution]:
        """Busca job por ID"""
        collection = self._get_collection()
        data = await collection.find_one({"id": job_id})

        if data:
            # Remover _id do MongoDB
            data.pop("_id", None)
            return JobExecution.from_dict(data)
        return None

    async def find_all(self, skip: int = 0, limit: int = 100) -> List[JobExecution]:
        """Busca todos os jobs com paginação, ordenados por data (mais recentes primeiro)"""
        collection = self._get_collection()
        cursor = collection.find().sort("created_at", -1).skip(skip).limit(limit)
        jobs_data = await cursor.to_list(length=limit)

        jobs = []
        for data in jobs_data:
            data.pop("_id", None)
            jobs.append(JobExecution.from_dict(data))
        return jobs

    async def find_running(self) -> List[JobExecution]:
        """Busca todos os jobs em execução"""
        collection = self._get_collection()
        cursor = collection.find({"status": "running"})
        jobs_data = await cursor.to_list(length=None)

        jobs = []
        for data in jobs_data:
            data.pop("_id", None)
            jobs.append(JobExecution.from_dict(data))
        return jobs

    async def update(self, job: JobExecution) -> JobExecution:
        """Atualiza um job existente"""
        collection = self._get_collection()

        # Atualizar job
        await collection.update_one(
            {"id": job.id},
            {"$set": job.to_dict()}
        )

        return job

    async def delete(self, job_id: str) -> bool:
        """Deleta um job"""
        collection = self._get_collection()
        result = await collection.delete_one({"id": job_id})
        return result.deleted_count > 0
