"""
Create Edital Use Case
"""
from typing import Dict, Any, Optional
from datetime import date
from ....domain.entities.edital import Edital
from ....domain.repositories.edital_repository import EditalRepository


class CreateEditalUseCase:
    """
    Caso de uso para criar um novo edital.
    """

    def __init__(self, edital_repository: EditalRepository):
        """
        Inicializa o caso de uso.

        Args:
            edital_repository: Repositório de editais
        """
        self.edital_repository = edital_repository

    async def execute(self, apelido_edital: str, link: str, **kwargs) -> Edital:
        """
        Executa o caso de uso de criação de edital.

        Args:
            apelido_edital: Nome/título do edital
            link: URL do edital
            **kwargs: Outros campos opcionais do edital

        Returns:
            Edital: Edital criado
        """
        # Criar entidade de domínio
        edital = Edital.create(
            apelido_edital=apelido_edital,
            link=link,
            **kwargs
        )

        # Persistir
        created_edital = await self.edital_repository.create(edital)

        return created_edital
