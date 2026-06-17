"""This module contains the SQLAlchemyProductQueryRepositoryAdapter class."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.orders.domain.exceptions.order_exception import (
    OrderRepositoryException,
)
from src.modules.orders.domain.ports.repositories.product_query_repository_port import (
    ProductQueryRepositoryPort,
)
from src.modules.orders.domain.value_objects.quantity_vo import QuantityVO
from src.modules.orders.domain.value_objects.referenced_product_vo import (
    ReferencedProductVO,
)
from src.modules.products.infrastructure.persistence.models.product_model import (
    ProductModel,
)
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class SQLAlchemyProductQueryRepositoryAdapter(ProductQueryRepositoryPort):
    """Implements orders' ProductQueryRepositoryPort using SQLAlchemy.

    This adapter lives in the products infrastructure layer because it is the
    products module that owns the data.  The orders module defines the port
    (consumer-owned contract), and this class fulfils it without exposing
    any products domain entity to the orders bounded context — only the
    :class:`ReferencedProductVO` value object crosses the boundary.

    This adapter participates in the Unit of Work pattern: it never calls
    ``session.commit()`` or ``session.rollback()`` directly. Transaction
    control is the exclusive responsibility of the
    :class:`SQLAlchemyOrderManagementUnitOfWorkAdapter` that owns the session.
    """

    def __init__(
        self,
        session: AsyncSession,
        logger_factory_outbound: LoggerFactoryOutboundPort,
    ) -> None:
        """Initializes the SQLAlchemyProductQueryRepositoryAdapter.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session provided
                by the Unit of Work.
            logger_factory_outbound (LoggerFactoryOutboundPort): The logger factory
                for creating loggers.
        """
        self.session = session
        self._logger = logger_factory_outbound.get_logger(__name__)

    async def find_by_ids(self, product_ids: list[UUID]) -> list[ReferencedProductVO]:
        """Find products by their IDs and return them as ReferencedProductVO instances.

        Only fields required by the orders bounded context are projected —
        the full ProductEntity never leaves the products module.

        Args:
            product_ids (list[UUID]): A list of product IDs to look up.

        Returns:
            list[ReferencedProductVO]: Products found for the given IDs.
                Products that do not exist are silently omitted; callers are
                responsible for detecting missing IDs when needed.

        Raises:
            OrderRepositoryException: If any database error occurs.
        """
        if not product_ids:
            return []

        try:
            stmt = select(
                ProductModel.id,
                ProductModel.supplier_id,
                ProductModel.name,
                ProductModel.unit_price,
                ProductModel.is_active,
            ).where(ProductModel.id.in_(product_ids))

            result = await self.session.execute(stmt)

            referenced_products = [
                ReferencedProductVO(
                    product_id=row.id,
                    supplier_id=row.supplier_id,
                    name=row.name,
                    quantity=QuantityVO(1),
                    unit_price=row.unit_price,
                    is_active=row.is_active,
                )
                for row in result.all()
            ]

            self._logger.debug(
                "Products fetched for order validation.",
                requested=len(product_ids),
                found=len(referenced_products),
            )

            return referenced_products

        except SQLAlchemyError as e:
            self._logger.error(
                "Database error while querying products for order.",
                exc_info=str(e),
            )
            raise OrderRepositoryException(
                "Database error during product query for order."
            ) from e
