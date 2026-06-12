"""This module contains the SQLAlchemyWarehouseOrderQueryRepositoryAdapter class."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.orders.domain.exceptions.order_exception import (
    OrderRepositoryException,
)
from src.modules.orders.infrastructure.persistence.models.order_model import OrderModel
from src.modules.warehouses.domain.ports.repositories.warehouse_order_query_repository_port import (
    WarehouseOrderQueryRepositoryPort,
)
from src.modules.warehouses.domain.value_objects.warehouse_referenced_order_vo import (
    WarehouseReferencedOrderVO,
)
from src.shared.domain.enums.order_status_enum import OrderStatusEnum
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class SQLAlchemyWarehouseOrderQueryRepositoryAdapter(WarehouseOrderQueryRepositoryPort):
    """Implements WarehouseOrderQueryRepositoryPort using SQLAlchemy for database operations.

    This adapter participates in the Unit of Work pattern: it never calls
    ``session.commit()`` or ``session.rollback()`` directly. Transaction
    control is the exclusive responsibility of the
    :class:`SQLAlchemyAuthUnitOfWorkAdapter` that owns the session.
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

    async def find_by_warehouse_id(
        self, warehouse_id: UUID
    ) -> WarehouseReferencedOrderVO | None:
        """Find a warehouse by ID.

        Args:
            warehouse_id (UUID): The ID of the warehouse to find.

        Returns:
            WarehouseEntity | None: The found warehouse entity or None if not found.
        """
        try:
            stmt = select(OrderModel).where(OrderModel.warehouse_id == warehouse_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            return (
                WarehouseReferencedOrderVO(
                    order_id=model.id,
                    warehouse_id=model.warehouse_id,
                    order_status=OrderStatusEnum(model.status_order),
                )
                if model
                else None
            )
        except SQLAlchemyError as e:
            self._logger.error(
                "Database error while retrieving order.", exc_info=str(e)
            )
            raise OrderRepositoryException(
                "Database error during order retrieval."
            ) from e
