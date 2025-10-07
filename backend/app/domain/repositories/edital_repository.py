"""
Edital Repository Interface - Contrato para implementações de persistência de editais
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from ..entities.edital import Edital


class EditalRepository(ABC):
    """
    Interface para repositório de editais.
    Define operações de persistência sem especificar a implementação.
    """

    @abstractmethod
    async def create(self, edital: Edital) -> Edital:
        """
        Cria um novo edital.

        Args:
            edital: Entidade Edital a ser persistida

        Returns:
            Edital: Edital criado
        """
        pass

    @abstractmethod
    async def find_by_uuid(self, edital_uuid: str) -> Optional[Edital]:
        """
        Busca um edital por UUID.

        Args:
            edital_uuid: UUID do edital

        Returns:
            Optional[Edital]: Edital encontrado ou None
        """
        pass

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[Edital]:
        """
        Busca todos os editais com paginação.

        Args:
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar

        Returns:
            List[Edital]: Lista de editais
        """
        pass

    @abstractmethod
    async def find_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Edital]:
        """
        Busca editais por status.

        Args:
            status: Status do edital ('aberto', 'fechado', 'em_breve')
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar

        Returns:
            List[Edital]: Lista de editais
        """
        pass

    @abstractmethod
    async def find_by_financiador(self, financiador: str, skip: int = 0, limit: int = 100) -> List[Edital]:
        """
        Busca editais por financiador.

        Args:
            financiador: Nome do financiador
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar

        Returns:
            List[Edital]: Lista de editais
        """
        pass

    @abstractmethod
    async def update(self, edital: Edital) -> Edital:
        """
        Atualiza um edital existente.

        Args:
            edital: Entidade Edital com dados atualizados

        Returns:
            Edital: Edital atualizado

        Raises:
            EditalNotFoundError: Se o edital não existe
        """
        pass

    @abstractmethod
    async def delete(self, edital_uuid: str) -> bool:
        """
        Deleta um edital.

        Args:
            edital_uuid: UUID do edital

        Returns:
            bool: True se deletado com sucesso, False caso contrário
        """
        pass

    @abstractmethod
    async def exists_by_link(self, link: str) -> bool:
        """
        Verifica se um edital com o link existe.

        Args:
            link: Link a verificar

        Returns:
            bool: True se existe, False caso contrário
        """
        pass

    @abstractmethod
    async def save_partial_extraction(
        self,
        edital_uuid: str,
        chunk_index: int,
        variables: dict,
        status: str = "in_progress"
    ) -> None:
        """
        Salva extração parcial de variáveis (por chunk).

        Args:
            edital_uuid: UUID do edital
            chunk_index: Índice do chunk
            variables: Variáveis extraídas do chunk
            status: Status da extração
        """
        pass

    @abstractmethod
    async def save_final_extraction(
        self,
        edital_uuid: str,
        consolidated_variables: dict,
        status: str = "completed"
    ) -> None:
        """
        Salva extração final consolidada de variáveis.

        Args:
            edital_uuid: UUID do edital
            consolidated_variables: Variáveis consolidadas
            status: Status final
        """
        pass
