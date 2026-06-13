"""This module contains the ToggleWarehouseStatusUseCase class."""

from src.modules.warehouses.application.dtos.toggle_warehouse_status_dto import (
    ToggleWarehouseStatusCommandDto,
    ToggleWarehouseStatusResponseDto,
)
from src.modules.warehouses.domain.exceptions.warehouse_exception import (
    WarehouseHasActiveOrdersException,
    WarehouseNotFoundException,
)
from src.modules.warehouses.domain.ports.unit_of_work.warehouse_lifecycle_unit_of_work_port import (
    WarehouseLifecycleUnitOfWorkPort,
)
from src.modules.warehouses.domain.value_objects.warehouse_by_supplier_cache_key_vo import (
    WarehouseBySupplierCacheKeyVO,
)
from src.modules.warehouses.domain.value_objects.warehouse_by_supplier_cache_value_vo import (
    WarehouseBySupplierCacheValueVO,
)
from src.shared.application.dtos.authenticated_user_dto import (
    AuthenticatedUserCommandDto,
)
from src.shared.domain.enums.order_status_enum import OrderStatusEnum
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.session_exception import (
    InsufficientPermissionsException,
)
from src.shared.domain.ports.outbound.cache_outbound_port import CacheOutboundPort
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class ToggleWarehouseStatusUseCase:
    """Use case for toggling the status of a warehouse.

    This use case toggles the status of a warehouse and invalidates the cache for the warehouse by supplier.
    """

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        warehouse_lifecycle_unit_of_work: WarehouseLifecycleUnitOfWorkPort,
        cache_outbound: CacheOutboundPort[WarehouseBySupplierCacheValueVO],
    ) -> None:
        """Initialize the ToggleWarehouseStatusUseCase.

        Args:
            logger_factory_outbound (LoggerFactoryOutboundPort): The logger factory outbound port.
            warehouse_lifecycle_unit_of_work (WarehouseLifecycleUnitOfWorkPort): The warehouse
                lifecycle unit of work port.
            cache_outbound (CacheOutboundPort[WarehouseBySupplierCacheValueVO]): The cache outbound port.
        """
        self._logger = logger_factory_outbound.get_logger(__name__)
        self.warehouse_lifecycle_unit_of_work = warehouse_lifecycle_unit_of_work
        self.cache_outbound = cache_outbound

    async def execute(
        self,
        command: ToggleWarehouseStatusCommandDto,
        authenticated_user: AuthenticatedUserCommandDto,
    ) -> ToggleWarehouseStatusResponseDto:
        """Execute the use case that toggles the status of a warehouse.

        This method toggles the status of a warehouse and invalidates the cache for the warehouse by supplier.

        Args:
            command (ToggleWarehouseStatusCommandDto): The command DTO for toggling the status.
            authenticated_user (AuthenticatedUserCommandDto): The authenticated user DTO.

        Returns:
            ToggleWarehouseStatusResponseDto: The response DTO for toggling the status.

        Raises:
            InsufficientPermissionsException: If the authenticated user does not have the SUPPLIER role
                or if the warehouse does not belong to the authenticated supplier.
            WarehouseNotFoundException: If the warehouse with the given ID does not exist.
        """
        self._logger.info(
            "Executing toggle warehouse status use case.",
            user_id=str(authenticated_user.user_id),
        )

        # Authorization check
        if authenticated_user.role != UserRoleEnum.SUPPLIER:
            self._logger.warning(
                "Unauthorized warehouse status toggle attempt.",
                actor_role=authenticated_user.role,
            )
            raise InsufficientPermissionsException(
                "Only suppliers can toggle warehouse statuses."
            )

        async with self.warehouse_lifecycle_unit_of_work as uow:
            # Find the warehouse by ID and check if it exists
            exists_warehouse = await uow.warehouses.find_by_id(command.warehouse_id)
            if exists_warehouse is None:
                self._logger.warning(
                    "Warehouse not found.",
                    warehouse_id=str(command.warehouse_id),
                )
                raise WarehouseNotFoundException()

            # Check if the warehouse belongs to the authenticated supplier
            if exists_warehouse.supplier_id != authenticated_user.user_id:
                self._logger.warning(
                    "The warehouse does not belong to the authenticated supplier.",
                    warehouse_id=str(command.warehouse_id),
                    supplier_id=str(exists_warehouse.supplier_id),
                    user_id=str(authenticated_user.user_id),
                )
                raise InsufficientPermissionsException(
                    "Don't have permission to toggle warehouse status."
                )

            # Constants for the blocking order statuses
            BLOCKING_ORDER_STATUSES = {
                OrderStatusEnum.CONFIRMED,
                OrderStatusEnum.PROCESSING,
                OrderStatusEnum.SHIPPED,
            }

            # Validate that a warehouse cannot be deactivated if it has orders
            # with the status CONFIRMED, PROCESSING, or SHIPPED associated with it.
            has_blocking_orders = (
                await uow.orders_query.exists_by_warehouse_id_and_statuses(
                    command.warehouse_id,
                    BLOCKING_ORDER_STATUSES,
                )
            )
            if has_blocking_orders:
                self._logger.warning(
                    "Cannot toggle warehouse status with active orders.",
                    warehouse_id=command.warehouse_id,
                    supplier_id=authenticated_user.user_id,
                )
                raise WarehouseHasActiveOrdersException(
                    "Cannot toggle warehouse status with active orders."
                )

            # Invalidate the cache for the warehouse by supplier
            key = WarehouseBySupplierCacheKeyVO.from_supplier_id(
                authenticated_user.user_id
            )
            await self.cache_outbound.delete(key)

            # Update the warehouse and persist the changes
            entity = exists_warehouse.update_is_active(command.is_active)
            warehouse = await uow.warehouses.update(entity)
            await uow.commit()

        self._logger.info(
            "Toggled warehouse status successfully.",
            warehouse_id=str(warehouse.id),
            supplier_id=str(warehouse.supplier_id),
        )

        return ToggleWarehouseStatusResponseDto(
            id=warehouse.id,
            supplier_id=warehouse.supplier_id,
            name=str(warehouse.name),
            address=str(warehouse.address),
            is_active=warehouse.is_active,
            created_at=warehouse.created_at,
            updated_at=warehouse.updated_at,
        )
