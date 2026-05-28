"""This module contains the GetWarehousesUseCase class."""

from src.modules.warehouses.application.dtos.get_warehouses_dto import (
    GetWarehousesResponseDto,
)
from src.modules.warehouses.domain.ports.repositories.warehouse_repository_port import (
    WarehouserRepositoryPort,
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
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.session_exception import (
    InsufficientPermissionsException,
)
from src.shared.domain.ports.outbound.cache_outbound_port import CacheOutboundPort
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)
from src.shared.domain.value_objects.cache_entry_vo import CacheEntryVO
from src.shared.domain.value_objects.cache_ttl_vo import CacheTTLVO


class GetWarehousesUseCase:
    """Use case for retrieving warehouses.

    This use case retrieves warehouses from the cache, or retrieves them from the repository
    and stores them in the cache.
    """

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        cache_outbound: CacheOutboundPort[WarehouseBySupplierCacheValueVO],
        warehouse_repository: WarehouserRepositoryPort,
    ) -> None:
        """Initialize the GetWarehousesUseCase.

        Args:
            logger_factory_outbound (LoggerFactoryOutboundPort): The logger factory outbound port.
            cache_outbound (CacheOutboundPort[WarehouseBySupplierCacheValueVO]): The cache
                outbound port.
            warehouse_repository (WarehouserRepositoryPort): The warehouse repository port.
        """
        self._logger = logger_factory_outbound.get_logger(__name__)
        self.cache_outbound = cache_outbound
        self.warehouse_repository = warehouse_repository

    async def execute(
        self, authenticated_user: AuthenticatedUserCommandDto
    ) -> GetWarehousesResponseDto:
        """Execute the use case that retrieves warehouses.

        Extracts the warehouses from the cache, or retrieves them from the repository
        and stores them in the cache.

        Args:
            authenticated_user (AuthenticatedUserCommandDto): The authenticated user DTO.

        Returns:
            GetWarehousesResponseDto: The response DTO for retrieving warehouses.
        """
        self._logger.info(
            "Executing get warehouses use case.",
            user_id=str(authenticated_user.user_id),
        )

        # Authorization check
        if authenticated_user.role != UserRoleEnum.SUPPLIER:
            self._logger.warning(
                "Unauthorized warehouse retrieval attempt",
                user_id=str(authenticated_user.user_id),
                actor_role=authenticated_user.role,
            )
            raise InsufficientPermissionsException(
                "Only suppliers can retrieve warehouses."
            )

        key = WarehouseBySupplierCacheKeyVO.from_supplier_id(authenticated_user.user_id)

        # Get the cached warehouses
        # If the cache entry is not found, retrieve the warehouses from the repository
        cached_warehouses = await self.cache_outbound.get(key)
        if cached_warehouses is None:
            # Get warehouses from the repository
            supplier_warehouses = (
                await self.warehouse_repository.find_all_by_supplier_id(
                    authenticated_user.user_id
                )
            )

            # Convert the warehouses to a cache value object
            # and set the cache entry
            cached_warehouses = WarehouseBySupplierCacheValueVO.from_warehouses(
                supplier_warehouses
            )
            entry = CacheEntryVO(key=key, ttl=CacheTTLVO(3600), value=cached_warehouses)
            await self.cache_outbound.set(entry)

            self._logger.info(
                "Retrieved warehouses from repository successfully.",
                supplier_id=str(authenticated_user.user_id),
            )

            return GetWarehousesResponseDto.from_warehouses(supplier_warehouses)

        self._logger.info(
            "Retrieved warehouses from cache successfully.",
            supplier_id=str(authenticated_user.user_id),
        )

        return GetWarehousesResponseDto.from_cache_value(cached_warehouses)
