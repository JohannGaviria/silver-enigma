"""This module contains the GetWarehouseStock class."""

from src.modules.products.application.dtos.get_warehouse_stock_dto import (
    GetWarehouseStockCommandDto,
    GetWarehouseStockResponseDto,
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


class GetWarehouseStockUseCase:
    """Use case for getting the warehouse stock."""

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        inventory_repository: InventoryRepositoryPort,
    ) -> None:
        """Initializes a GetWarehouseStockUseCase instance.

        Args:
            logger_factory_outbound (LoggerFactoryOutboundPort): The logger factory outbound port.
            inventory_repository (InventoryRepositoryPort): The inventory repository port.
        """
        self._logger = logger_factory_outbound.get_logger(__name__)
        self.inventory_repository = inventory_repository

    async def execute(
        self,
        command: GetWarehouseStockCommandDto,
        authenticated_user: AuthenticatedUserCommandDto,
    ) -> GetWarehouseStockResponseDto:
        """Execute the use case that gets the warehouse stock.

        Args:
            command (GetWarehouseStockCommandDto): The command to execute.
            authenticated_user (AuthenticatedUserCommandDto): The authenticated user.

        Returns:
            GetWarehouseStockResponseDto: The response from the use case.
        """
        self._logger.info(
            "Executing get warehouse stock use case.",
            user_id=authenticated_user.user_id,
            warehouse_id=command.warehouse_id,
        )

        # Authorization check
        if authenticated_user.role != UserRoleEnum.SUPPLIER:
            self._logger.warning(
                "Unauthorized warehouse stock retrieval attempt.",
                user_id=authenticated_user.user_id,
                actor_role=authenticated_user.role,
            )
            raise InsufficientPermissionsException(
                "Only suppliers can get warehouse stock."
            )

        # Get the warehouse stock
        warehouse_stock = (
            await self.inventory_repository.find_inventory_by_user_and_warehouse(
                user_id=authenticated_user.user_id,
                warehouse_id=command.warehouse_id,
                page=command.page,
                page_size=command.page_size,
            )
        )

        self._logger.info("Found warehouse stock successfully.")

        return GetWarehouseStockResponseDto.from_stocks(warehouse_stock)
