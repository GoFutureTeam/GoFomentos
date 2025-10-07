"""
Job Repository Interface
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from ..entities.job_execution import JobExecution


class JobRepository(ABC):
    """
    Interface para repositório de execuções de jobs.
    """

    @abstractmethod
    async def create(self, job: JobExecution) -> JobExecution:
        """
        Cria uma nova execução de job.

        Args:
            job: Entidade JobExecution

        Returns:
            JobExecution: Job criado
        """
        pass

    @abstractmethod
    async def find_by_id(self, job_id: str) -> Optional[JobExecution]:
        """
        Busca um job por ID.

        Args:
            job_id: ID do job

        Returns:
            Optional[JobExecution]: Job encontrado ou None
        """
        pass

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[JobExecution]:
        """
        Busca todos os jobs com paginação.

        Args:
            skip: Número de registros a pular
            limit: Número máximo de registros

        Returns:
            List[JobExecution]: Lista de jobs
        """
        pass

    @abstractmethod
    async def find_running(self) -> List[JobExecution]:
        """
        Busca todos os jobs em execução.

        Returns:
            List[JobExecution]: Lista de jobs em execução
        """
        pass

    @abstractmethod
    async def update(self, job: JobExecution) -> JobExecution:
        """
        Atualiza um job existente.

        Args:
            job: Entidade JobExecution com dados atualizados

        Returns:
            JobExecution: Job atualizado
        """
        pass

    @abstractmethod
    async def delete(self, job_id: str) -> bool:
        """
        Deleta um job (apenas para limpeza de histórico muito antigo).

        Args:
            job_id: ID do job

        Returns:
            bool: True se deletado com sucesso
        """
        pass
