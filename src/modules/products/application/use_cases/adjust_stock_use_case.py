"""This module contains the AdjustStockUseCase class."""

from src.modules.products.application.dtos.adjust_stock_dto import (
    AdjustStockCommandDto,
    AdjustStockResponseDto,
)
from src.modules.products.domain.entities.inventory_movement_entity import (
    InventoryMovementEntity,
)
from src.modules.products.domain.entities.stock_entity import StockEntity
from src.modules.products.domain.enums.movement_type_log_enum import MovementTypeLogEnum
from src.modules.products.domain.exceptions.inventory_warehouse_exception import (
    ReferencedWarehouseNotActiveException,
    ReferencedWarehouseNotFoundException,
)
from src.modules.products.domain.exceptions.product_exception import (
    ProductNotActiveException,
    ProductNotFoundException,
)
from src.modules.products.domain.ports.unit_of_work.inventory_unit_of_work_port import (
    InventoryUnitOfWorkPort,
)
from src.modules.products.domain.value_objects.reserved_stock_vo import (
    ReservedStockVO,
)
from src.modules.products.domain.value_objects.total_stock_vo import TotalStockVO
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


class AdjustStockUseCase:
    """Use case for adjusting stock.

    This use case allows suppliers to adjust the stock of a product in a warehouse.
    It ensures that the total stock remains within the reserved stock and that
    the reserved stock does not go below the reserved quantity.
    """

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        inventory_unit_of_work: InventoryUnitOfWorkPort,
    ) -> None:
        """Initializes the AdjustStockUseCase.

        Args:
            logger_factory_outbound (LoggerFactoryOutboundPort): The logger factory outbound port.
            inventory_unit_of_work (InventoryUnitOfWorkPort): The inventory unit of work port
                used to coordinate all repositories required for adjusting stock.
        """
        self._logger = logger_factory_outbound.get_logger(__name__)
        self.inventory_unit_of_work = inventory_unit_of_work

    async def execute(
        self,
        command: AdjustStockCommandDto,
        authenticated_user: AuthenticatedUserCommandDto,
    ) -> AdjustStockResponseDto:
        """Executes the use case for adjusting stock.

        Args:
            command (AdjustStockCommandDto): The command to execute.
            authenticated_user (AuthenticatedUserCommandDto): The authenticated user.

        Returns:
            AdjustStockResponseDto: The response from the use case.

        Raises:
            InsufficientPermissionsException: If the user does not have sufficient permissions.
            ProductNotFoundException: If the product with the given ID does not exist.
            ProductNotActiveException: If the product is not active.
            ReferencedWarehouseNotFoundException: If the warehouse with the given ID does not exist.
            ReferencedWarehouseNotActiveException: If the warehouse is not active.
        """
        self._logger.info(
            "Executing use case for adjusting stock.",
            product_id=command.product_id,
            user_id=authenticated_user.user_id,
        )

        # Authorization check
        if authenticated_user.role != UserRoleEnum.SUPPLIER:
            self._logger.warning(
                "Unauthorized adjustment of stock for product.",
                product_id=command.product_id,
                user_id=authenticated_user.user_id,
                actor_role=authenticated_user.role,
            )
            raise InsufficientPermissionsException("Only suppliers can adjust stock.")

        # Value Objects are validated eagerly at construction time, so domain
        # exceptions will propagate before we open the transaction.
        total_stock = TotalStockVO(command.quantity)

        async with self.inventory_unit_of_work as uow:
            # Find the warehouse by ID and check if it exists
            exists_warehouse = await uow.warehouses.find_by_id(command.warehouse_id)
            if exists_warehouse is None:
                self._logger.warning(
                    "Warehouse not found.",
                    warehouse_id=command.warehouse_id,
                    supplier_id=authenticated_user.user_id,
                )
                raise ReferencedWarehouseNotFoundException()

            # Check if the warehouse belongs to the authenticated supplier
            if exists_warehouse.supplier_id != authenticated_user.user_id:
                self._logger.warning(
                    "The warehouse does not belong to the authenticated supplier.",
                    warehouse_id=command.warehouse_id,
                    supplier_id=authenticated_user.user_id,
                )
                raise InsufficientPermissionsException(
                    "Don't have permission to adjust stock."
                )

            # Check if the warehouse is active
            if not exists_warehouse.is_active:
                self._logger.warning(
                    "The warehouse is not active.",
                    warehouse_id=command.warehouse_id,
                    supplier_id=authenticated_user.user_id,
                )
                raise ReferencedWarehouseNotActiveException()

            # Find the product by ID and check if it exists
            exists_product = await uow.products.find_by_id(command.product_id)
            if exists_product is None:
                self._logger.warning(
                    "Product not found.",
                    product_id=command.product_id,
                    supplier_id=authenticated_user.user_id,
                )
                raise ProductNotFoundException()

            # Check if the product belongs to the authenticated supplier
            if exists_product.supplier_id != authenticated_user.user_id:
                self._logger.warning(
                    "The product does not belong to the authenticated supplier.",
                    product_id=command.product_id,
                    supplier_id=authenticated_user.user_id,
                )
                raise InsufficientPermissionsException(
                    "Don't have permission to adjust stock."
                )

            # Check if the product is active
            if not exists_product.is_active:
                self._logger.warning(
                    "The product is not active.",
                    product_id=command.product_id,
                    supplier_id=authenticated_user.user_id,
                )
                raise ProductNotActiveException()

            # Acquire a row-level lock before reading stock that will be mutated,
            # preventing concurrent transactions from passing stock validation
            # simultaneously and causing overselling.
            exists_stock = await uow.stocks.find_by_product_and_warehouse_for_update(
                command.product_id, command.warehouse_id
            )

            # Create a new stock if it doesn't exist
            if exists_stock is None:
                entity = StockEntity.create(
                    product_id=command.product_id,
                    warehouse_id=command.warehouse_id,
                    total_stock=total_stock,
                    reserved_stock=ReservedStockVO(0),
                )
                stock = await uow.stocks.save(entity)

            # Update the stock if it exists
            else:
                entity = exists_stock.update_total_stock(total_stock)
                stock = await uow.stocks.update(entity)

            # Create a new inventory movement for the release
            inventory_movement = InventoryMovementEntity.create(
                product_id=command.product_id,
                warehouse_id=command.warehouse_id,
                movement_type=MovementTypeLogEnum.RELEASE,
                quantity=command.quantity,
            )
            await uow.inventory_movements.save(inventory_movement)

            # Commit the transaction
            await uow.commit()

        self._logger.info(
            "Adjusted stock successfully.",
            stock_id=stock.id,
            product_id=stock.product_id,
            warehouse_id=stock.warehouse_id,
            supplier_id=authenticated_user.user_id,
        )

        return AdjustStockResponseDto(
            id=stock.id,
            product_id=stock.product_id,
            warehouse_id=stock.warehouse_id,
            total_stock=stock.total_stock.value(),
            reserved_stock=stock.reserved_stock.value(),
            available_stock=stock.total_stock.value() - stock.reserved_stock.value(),
            created_at=stock.created_at,
            updated_at=stock.updated_at,
        )
