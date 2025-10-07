"""
MongoDB Project Repository Implementation
"""
from typing import Optional, List
from ....domain.entities.project import Project
from ....domain.repositories.project_repository import ProjectRepository
from ....domain.exceptions.domain_exceptions import ProjectNotFoundError
from .connection import MongoDBConnection


class MongoProjectRepository(ProjectRepository):
    """
    Implementação concreta do ProjectRepository usando MongoDB.
    """

    def __init__(self, db_connection: MongoDBConnection):
        """
        Inicializa o repositório.

        Args:
            db_connection: Conexão com MongoDB
        """
        self.db_connection = db_connection
        self.collection_name = "projects"

    def _get_collection(self):
        """Retorna a coleção de projetos"""
        return self.db_connection.get_collection(self.collection_name)

    async def create(self, project: Project) -> Project:
        """Cria um novo projeto"""
        collection = self._get_collection()
        await collection.insert_one(project.to_dict())
        return project

    async def find_by_id(self, project_id: str) -> Optional[Project]:
        """Busca projeto por ID"""
        collection = self._get_collection()
        data = await collection.find_one({"id": project_id})

        if data:
            return Project.from_dict(data)
        return None

    async def find_by_user_id(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Project]:
        """Busca todos os projetos de um usuário"""
        collection = self._get_collection()
        cursor = collection.find({"user_id": user_id}).skip(skip).limit(limit)
        projects_data = await cursor.to_list(length=limit)

        return [Project.from_dict(data) for data in projects_data]

    async def find_by_edital_uuid(self, edital_uuid: str, skip: int = 0, limit: int = 100) -> List[Project]:
        """Busca todos os projetos associados a um edital"""
        collection = self._get_collection()
        cursor = collection.find({"edital_uuid": edital_uuid}).skip(skip).limit(limit)
        projects_data = await cursor.to_list(length=limit)

        return [Project.from_dict(data) for data in projects_data]

    async def find_all(self, skip: int = 0, limit: int = 100) -> List[Project]:
        """Busca todos os projetos com paginação"""
        collection = self._get_collection()
        cursor = collection.find().skip(skip).limit(limit)
        projects_data = await cursor.to_list(length=limit)

        return [Project.from_dict(data) for data in projects_data]

    async def update(self, project: Project) -> Project:
        """Atualiza um projeto existente"""
        collection = self._get_collection()

        # Verificar se o projeto existe
        existing = await collection.find_one({"id": project.id})
        if not existing:
            raise ProjectNotFoundError(project.id)

        # Atualizar projeto
        await collection.update_one(
            {"id": project.id},
            {"$set": project.to_dict()}
        )

        return project

    async def delete(self, project_id: str) -> bool:
        """Deleta um projeto"""
        collection = self._get_collection()
        result = await collection.delete_one({"id": project_id})
        return result.deleted_count > 0
