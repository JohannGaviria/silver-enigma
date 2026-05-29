"""This module contains the UpdateWarehouseUseCase class."""

from src.modules.warehouses.application.dtos.update_warehouse_dto import (
    UpdateWarehouseCommandDto,
    UpdateWarehouseResponseDto,
)
from src.modules.warehouses.domain.exceptions.warehouse_exception import (
    WarehouseNotFoundException,
)
from src.modules.warehouses.domain.ports.unit_of_work.warehouse_unit_of_work_port import (
    WarehouseUnitOfWorkPort,
)
from src.modules.warehouses.domain.value_objects.warehouse_address_vo import (
    WarehouseAddressVO,
)
from src.modules.warehouses.domain.value_objects.warehouse_by_supplier_cache_key_vo import (
    WarehouseBySupplierCacheKeyVO,
)
from src.modules.warehouses.domain.value_objects.warehouse_by_supplier_cache_value_vo import (
    WarehouseBySupplierCacheValueVO,
)
from src.modules.warehouses.domain.value_objects.warehouse_name_vo import (
    WarehouseNameVO,
)
from src.shared.application.dtos.authenticated_user_dto import (
    AuthenticatedUserCommandDto,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.session_exception import (
    InsufficientPermissionsException,
)
from src.shared.domain.ports.outbound.cache_outbound_port import CacheOutboundPort
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class UpdateWarehouseUseCase:
    """Use case for warehouse upgrade.

    This use case updates the name and address of a warehouse and invalidates the cache for the
    warehouse by supplier.
    """

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        warehouse_unit_of_work: WarehouseUnitOfWorkPort,
        cache_outbound: CacheOutboundPort[WarehouseBySupplierCacheValueVO],
    ) -> None:
        """Initializes the UpdateWarehouseUseCase.

        Args:
            logger_factory_outbound (LoggerFactoryOutboundPort): The logger factory outbound port.
            warehouse_unit_of_work (WarehouseUnitOfWorkPort): The warehouse unit of work port.
            cache_outbound (CacheOutboundPort[WarehouseBySupplierCacheValueVO]): The cache outbound port.
        """
        self._logger = logger_factory_outbound.get_logger(__name__)
        self.warehouse_unit_of_work = warehouse_unit_of_work
        self.cache_outbound = cache_outbound

    async def execute(
        self,
        command: UpdateWarehouseCommandDto,
        authenticated_user: AuthenticatedUserCommandDto,
    ) -> UpdateWarehouseResponseDto:
        """Execute the use case that updates a warehouse.

        This method updates the name and address of a warehouse and invalidates the cache for the
        warehouse by supplier.

        Args:
            command (UpdateWarehouseCommandDto): The command to update a warehouse.
            authenticated_user (AuthenticatedUserCommandDto): The authenticated user DTO.

        Returns:
            UpdateWarehouseResponseDto: The response DTO for updating a warehouse.

        Raises:
            InsufficientPermissionsException: If the authenticated user does not have
                permission to update the warehouse.
            WarehouseNotFoundException: If the warehouse with the given ID does not exist.
        """
        self._logger.info(
            "Executing update warehouse use case.",
            user_id=str(authenticated_user.user_id),
        )

        # Authentication check
        if authenticated_user.role != UserRoleEnum.SUPPLIER:
            self._logger.warning(
                "Unauthorized warehouse update attempt.",
                user_id=str(authenticated_user.user_id),
                actor_role=authenticated_user.role,
            )
            raise InsufficientPermissionsException(
                "Only suppliers can update warehouses."
            )

        # Value Objects are validated eagerly at construction time, so domain
        # exceptions will propagate before we open the transaction.
        # If the value objects are None, they will be set to None in the entity.
        name = WarehouseNameVO(command.name) if command.name is not None else None
        address = (
            WarehouseAddressVO(command.address) if command.address is not None else None
        )

        async with self.warehouse_unit_of_work as uow:
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
                    "Don't have permission to update warehouse.",
                    warehouse_id=str(command.warehouse_id),
                    supplier_id=str(exists_warehouse.supplier_id),
                    user_id=str(authenticated_user.user_id),
                )
                raise InsufficientPermissionsException(
                    "The warehouse does not belong to the authenticated supplier."
                )

            # Invalidate the cache for the warehouse by supplier
            key = WarehouseBySupplierCacheKeyVO.from_supplier_id(
                authenticated_user.user_id
            )
            await self.cache_outbound.delete(key)

            # Update the warehouse and persist the changes
            entity = exists_warehouse.update(name=name, address=address)
            warehouse = await uow.warehouses.update(entity)

        self._logger.info(
            "Updated warehouse successfully",
            warehouse_id=str(warehouse.id),
            supplier_id=str(warehouse.supplier_id),
        )

        return UpdateWarehouseResponseDto(
            id=warehouse.id,
            supplier_id=warehouse.supplier_id,
            name=str(warehouse.name),
            address=str(warehouse.address),
            is_active=warehouse.is_active,
            created_at=warehouse.created_at,
            updated_at=warehouse.updated_at,
        )
