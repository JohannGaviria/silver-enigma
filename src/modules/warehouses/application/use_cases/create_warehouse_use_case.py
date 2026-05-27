"""This module contains the CreateWarehouseUseCase class."""

from src.modules.warehouses.application.dtos.create_warehouse_dto import (
    CreateWarehouseCommandDto,
    CreateWarehouseResponseDto,
)
from src.modules.warehouses.domain.entities.warehouse_entity import WarehouseEntity
from src.modules.warehouses.domain.ports.unit_of_work.warehouse_unit_of_work_port import (
    WarehouseUnitOfWorkPort,
)
from src.modules.warehouses.domain.value_objects.warehouse_address_vo import (
    WarehouseAddressVO,
)
from src.modules.warehouses.domain.value_objects.warehouse_by_supplier_cache_key_vo import (
    WarehouseBySupplierCacheKeyVO,
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


class CreateWarehouseUseCase:
    """Use case for creating a warehouse."""

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        cache_outbound: CacheOutboundPort,
        warehouse_unit_of_work: WarehouseUnitOfWorkPort,
    ) -> None:
        """Initialize the CreateWarehouseUseCase.

        Args:
            logger_factory_outbound (LoggerFactoryOutboundPort): The logger factory outbound port.
            cache_outbound (CacheOutboundPort): The cache outbound port.
            warehouse_unit_of_work (WarehouseUnitOfWorkPort): The warehouse unit of work port.
        """
        self._logger = logger_factory_outbound.get_logger(__name__)
        self.cache_outbound = cache_outbound
        self.warehouse_unit_of_work = warehouse_unit_of_work

    async def execute(
        self,
        command: CreateWarehouseCommandDto,
        authenticated_user: AuthenticatedUserCommandDto,
    ) -> CreateWarehouseResponseDto:
        """Execute the use case that creates a warehouse.

        Args:
            command (CreateWarehouseCommandDto): The command DTO for creating a warehouse.
            authenticated_user (AuthenticatedUserCommandDto): The authenticated user DTO.

        Returns:
            CreateWarehouseResponseDto: The response DTO for creating a warehouse.
        """
        self._logger.info(
            "Executing create warehouse use case",
            supplier_id=str(authenticated_user.user_id),
        )

        # Authorization check
        if authenticated_user.role != UserRoleEnum.SUPPLIER:
            self._logger.warning(
                "Unauthorized warehouse creation attempt",
                actor_role=authenticated_user.role,
            )
            raise InsufficientPermissionsException(
                "Only suppliers can create warehouses."
            )

        # Value Objects are validated eagerly at construction time, so domain
        # exceptions will propagate before we open the transaction.
        name = WarehouseNameVO(command.name)
        address = WarehouseAddressVO(command.address)

        # Invalidate the cache for the warehouse by supplier
        key = WarehouseBySupplierCacheKeyVO.from_supplier_id(authenticated_user.user_id)
        await self.cache_outbound.delete(key)

        async with self.warehouse_unit_of_work as uow:
            # Create and persist the new warehouse
            entity = WarehouseEntity.create(
                supplier_id=authenticated_user.user_id, name=name, address=address
            )
            warehouse = await uow.warehouses.save(entity)
            await uow.commit()

        self._logger.info("Created warehouse", warehouse_id=str(warehouse.id))

        return CreateWarehouseResponseDto(
            id=warehouse.id,
            supplier_id=warehouse.supplier_id,
            name=str(warehouse.name),
            address=str(warehouse.address),
            is_active=warehouse.is_active,
            created_at=warehouse.created_at,
            updated_at=warehouse.updated_at,
        )
