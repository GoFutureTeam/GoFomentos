"""
Create Project Use Case
"""
from typing import Optional
from ....domain.entities.project import Project
from ....domain.repositories.project_repository import ProjectRepository


class CreateProjectUseCase:
    """
    Caso de uso para criar um novo projeto.
    """

    def __init__(self, project_repository: ProjectRepository):
        """
        Inicializa o caso de uso.

        Args:
            project_repository: Repositório de projetos
        """
        self.project_repository = project_repository

    async def execute(
        self,
        titulo_projeto: str,
        objetivo_principal: str,
        nome_empresa: str,
        resumo_atividades: str,
        cnae: str,
        user_id: str,
        documento_url: Optional[str] = None,
        edital_uuid: Optional[str] = None
    ) -> Project:
        """
        Executa o caso de uso de criação de projeto.

        Args:
            titulo_projeto: Título do projeto
            objetivo_principal: Objetivo principal do projeto
            nome_empresa: Nome da empresa
            resumo_atividades: Resumo das atividades
            cnae: CNAE da empresa
            user_id: ID do usuário proprietário
            documento_url: URL do documento (opcional)
            edital_uuid: UUID do edital relacionado (opcional)

        Returns:
            Project: Projeto criado
        """
        # Criar entidade de domínio
        project = Project.create(
            titulo_projeto=titulo_projeto,
            objetivo_principal=objetivo_principal,
            nome_empresa=nome_empresa,
            resumo_atividades=resumo_atividades,
            cnae=cnae,
            user_id=user_id,
            documento_url=documento_url,
            edital_uuid=edital_uuid
        )

        # Persistir
        created_project = await self.project_repository.create(project)

        return created_project
