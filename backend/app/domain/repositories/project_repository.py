"""
Project Repository Interface - Contrato para implementações de persistência de projetos
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from ..entities.project import Project


class ProjectRepository(ABC):
    """
    Interface para repositório de projetos.
    Define operações de persistência sem especificar a implementação.
    """

    @abstractmethod
    async def create(self, project: Project) -> Project:
        """
        Cria um novo projeto.

        Args:
            project: Entidade Project a ser persistida

        Returns:
            Project: Projeto criado
        """
        pass

    @abstractmethod
    async def find_by_id(self, project_id: str) -> Optional[Project]:
        """
        Busca um projeto por ID.

        Args:
            project_id: ID do projeto

        Returns:
            Optional[Project]: Projeto encontrado ou None
        """
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Project]:
        """
        Busca todos os projetos de um usuário.

        Args:
            user_id: ID do usuário
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar

        Returns:
            List[Project]: Lista de projetos do usuário
        """
        pass

    @abstractmethod
    async def find_by_edital_uuid(self, edital_uuid: str, skip: int = 0, limit: int = 100) -> List[Project]:
        """
        Busca todos os projetos associados a um edital.

        Args:
            edital_uuid: UUID do edital
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar

        Returns:
            List[Project]: Lista de projetos
        """
        pass

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[Project]:
        """
        Busca todos os projetos com paginação.

        Args:
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar

        Returns:
            List[Project]: Lista de projetos
        """
        pass

    @abstractmethod
    async def update(self, project: Project) -> Project:
        """
        Atualiza um projeto existente.

        Args:
            project: Entidade Project com dados atualizados

        Returns:
            Project: Projeto atualizado

        Raises:
            ProjectNotFoundError: Se o projeto não existe
        """
        pass

    @abstractmethod
    async def delete(self, project_id: str) -> bool:
        """
        Deleta um projeto.

        Args:
            project_id: ID do projeto

        Returns:
            bool: True se deletado com sucesso, False caso contrário
        """
        pass
