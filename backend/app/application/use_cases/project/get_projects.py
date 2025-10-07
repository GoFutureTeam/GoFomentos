"""
Get Projects Use Cases
"""
from typing import List
from ....domain.entities.project import Project
from ....domain.repositories.project_repository import ProjectRepository
from ....domain.exceptions.domain_exceptions import ProjectNotFoundError, ProjectAccessDeniedError


class GetProjectsUseCase:
    """
    Casos de uso para obter projetos.
    """

    def __init__(self, project_repository: ProjectRepository):
        """
        Inicializa o caso de uso.

        Args:
            project_repository: Repositório de projetos
        """
        self.project_repository = project_repository

    async def execute_by_id(self, project_id: str, requesting_user_id: str) -> Project:
        """
        Obtém um projeto por ID com verificação de permissão.

        Args:
            project_id: ID do projeto
            requesting_user_id: ID do usuário fazendo a requisição

        Returns:
            Project: Projeto encontrado

        Raises:
            ProjectNotFoundError: Se o projeto não existir
            ProjectAccessDeniedError: Se o usuário não tiver permissão
        """
        project = await self.project_repository.find_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(project_id)

        # Verificar se o usuário tem permissão
        if not project.belongs_to_user(requesting_user_id):
            raise ProjectAccessDeniedError(project_id, requesting_user_id)

        return project

    async def execute_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Project]:
        """
        Obtém todos os projetos de um usuário.

        Args:
            user_id: ID do usuário
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar

        Returns:
            List[Project]: Lista de projetos do usuário
        """
        return await self.project_repository.find_by_user_id(user_id, skip, limit)
