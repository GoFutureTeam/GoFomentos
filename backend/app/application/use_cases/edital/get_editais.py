"""
Get Editais Use Cases
"""
from typing import List
from ....domain.entities.edital import Edital
from ....domain.repositories.edital_repository import EditalRepository
from ....domain.exceptions.domain_exceptions import EditalNotFoundError


class GetEditaisUseCase:
    """
    Casos de uso para obter editais.
    """

    def __init__(self, edital_repository: EditalRepository):
        """
        Inicializa o caso de uso.

        Args:
            edital_repository: Repositório de editais
        """
        self.edital_repository = edital_repository

    async def execute_all(self, skip: int = 0, limit: int = 100) -> List[Edital]:
        """
        Obtém todos os editais com paginação.

        Args:
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar

        Returns:
            List[Edital]: Lista de editais
        """
        return await self.edital_repository.find_all(skip, limit)

    async def execute_by_uuid(self, edital_uuid: str) -> Edital:
        """
        Obtém um edital por UUID.

        Args:
            edital_uuid: UUID do edital

        Returns:
            Edital: Edital encontrado

        Raises:
            EditalNotFoundError: Se o edital não existir
        """
        edital = await self.edital_repository.find_by_uuid(edital_uuid)
        if not edital:
            raise EditalNotFoundError(edital_uuid)
        return edital

    async def execute_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Edital]:
        """
        Obtém editais por status.

        Args:
            status: Status do edital ('aberto', 'fechado', 'em_breve')
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar

        Returns:
            List[Edital]: Lista de editais
        """
        return await self.edital_repository.find_by_status(status, skip, limit)
