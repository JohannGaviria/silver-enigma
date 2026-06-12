"""This module contains the GetProductCatalogUseCase class."""

from src.modules.products.application.dtos.get_product_catalog_dto import (
    GetProductCatalogCommandDto,
    GetProductCatalogResponseDto,
)
from src.modules.products.domain.ports.repositories.inventory_repository_port import (
    InventoryRepositoryPort,
)
from src.shared.application.dtos.authenticated_user_dto import (
    AuthenticatedUserCommandDto,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.session_exception import (
    InsufficientPermissionsException,
)
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class GetProductCatalogUseCase:
    """Use Case for obtaining the product catalog for a buyer."""

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        inventory_repository: InventoryRepositoryPort,
    ) -> None:
        """Initializes the GetProductCatalogUseCase.

        Args:
            logger_factory_outbound: (LoggerFactoryOutboundPort): The logger factory outbound port.
            inventory_repository: (InventoryRepositoryPort): The inventory repository port.
        """
        self._logger = logger_factory_outbound.get_logger(__name__)
        self.inventory_repository = inventory_repository

    async def execute(
        self,
        command: GetProductCatalogCommandDto,
        authenticated_user: AuthenticatedUserCommandDto,
    ) -> GetProductCatalogResponseDto:
        """Execute the use case that retrieves the product catalog.

        This method retrieves the catalog of products available to a buyer user.

        Args:
            command (GetProductCatalogCommandDto): The command for getting the product catalog with filters.
            authenticated_user (AuthenticatedUserCommandDto): The authenticated user.

        Returns:
            GetProductCatalogResponseDto: The response form use case.
        """
        self._logger.info("Executing get product catalog use case.")

        # Authorization check
        if authenticated_user.role != UserRoleEnum.BUYER:
            self._logger.warning(
                "User is not authorized to access the product catalog.",
                user_id=authenticated_user.user_id,
                actor_role=authenticated_user.role,
            )
            raise InsufficientPermissionsException(
                "Only buyers can access the product catalog."
            )

        # Find all products and stock
        products_stock = await self.inventory_repository.find_all_products_and_stock(
            name=command.name,
            unit_of_measure=command.unit_of_measure,
            page=command.page,
            page_size=command.page_size,
        )

        self._logger.info("Products stock found successfully.")

        return GetProductCatalogResponseDto.from_stocks(products_stock)
