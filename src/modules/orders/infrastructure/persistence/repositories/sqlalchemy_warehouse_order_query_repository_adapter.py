"""This module contains the SQLAlchemyWarehouseOrderQueryRepositoryAdapter class."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.orders.domain.exceptions.order_exception import (
    OrderRepositoryException,
)
from src.modules.orders.infrastructure.persistence.models.inventory_allocation_model import (
    InventoryAllocationModel,
)
from src.modules.orders.infrastructure.persistence.models.order_items_model import (
    OrderItemsModel,
)
from src.modules.orders.infrastructure.persistence.models.order_model import OrderModel
from src.modules.warehouses.domain.ports.repositories.warehouse_order_query_repository_port import (
    WarehouseOrderQueryRepositoryPort,
)
from src.shared.domain.enums.order_status_enum import OrderStatusEnum
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class SQLAlchemyWarehouseOrderQueryRepositoryAdapter(WarehouseOrderQueryRepositoryPort):
    """Implements WarehouseOrderQueryRepositoryPort using SQLAlchemy for database operations.

    Following ADR-013, ``orders`` no longer stores ``warehouse_id`` directly:
    the relationship between an order and a warehouse is established at
    fulfillment time through ``inventory_allocations``, one row per
    (order item, warehouse, quantity) combination. This adapter therefore
    joins ``orders`` -> ``order_items`` -> ``inventory_allocations`` to
    determine whether a warehouse is involved in any order with a blocking
    status.

    Until a fulfillment use case starts writing ``inventory_allocations``,
    this query will correctly return False for every warehouse, because no
    allocation rows exist yet — there is no order-warehouse relationship to
    report, which matches the current state of the business process.

    This adapter participates in the Unit of Work pattern: it never calls
    ``session.commit()`` or ``session.rollback()`` directly. Transaction
    control is the exclusive responsibility of the
    :class:`SQLAlchemyWarehouseLifecycleUnitOfWorkAdapter` that owns the session.
    """

    def __init__(
        self, session: AsyncSession, logger_factory_outbound: LoggerFactoryOutboundPort
    ) -> None:
        """Initializes the SQLAlchemyWarehouseOrderQueryRepositoryAdapter.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session provided
                by the Unit of Work.
            logger_factory_outbound (LoggerFactoryOutboundPort): The logger factory
                for creating loggers.
        """
        self.session = session
        self._logger = logger_factory_outbound.get_logger(__name__)

    async def exists_by_warehouse_id_and_statuses(
        self, warehouse_id: UUID, statuses: set[OrderStatusEnum]
    ) -> bool:
        """Check if an order exists for a warehouse with any of the given statuses.

        The relationship is resolved via inventory allocations: a warehouse
        is considered involved in an order if at least one of the order's
        items has an allocation pointing at that warehouse.

        Args:
            warehouse_id (UUID): The ID of the warehouse.
            statuses (set[OrderStatusEnum]): The set of statuses to check.

        Returns:
            bool: True if a matching order exists, False otherwise.
        """
        try:
            stmt = (
                select(OrderModel.id)
                .join(OrderItemsModel, OrderItemsModel.order_id == OrderModel.id)
                .join(
                    InventoryAllocationModel,
                    InventoryAllocationModel.order_item_id == OrderItemsModel.id,
                )
                .where(
                    InventoryAllocationModel.warehouse_id == warehouse_id,
                    OrderModel.status_order.in_(statuses),
                )
                .limit(1)
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none() is not None
        except SQLAlchemyError as e:
            self._logger.error(
                "Database error while retrieving order.", exc_info=str(e)
            )
            raise OrderRepositoryException(
                "Database error during order retrieval."
            ) from e
