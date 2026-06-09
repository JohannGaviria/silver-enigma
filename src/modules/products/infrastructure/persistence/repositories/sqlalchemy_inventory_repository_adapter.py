"""This module contains the SQLAlchemyInventoryRepositoryAdapter class."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.products.domain.exceptions.inventory_exception import (
    InventoryRepositoryException,
)
from src.modules.products.domain.ports.repositories.inventory_repository_port import (
    InventoryRepositoryPort,
)
from src.modules.products.domain.value_objects.available_stock_vo import (
    AvailableStockVO,
)
from src.modules.products.domain.value_objects.product_name_vo import ProductNameVO
from src.modules.products.domain.value_objects.total_stock_vo import TotalStockVO
from src.modules.products.domain.value_objects.warehouse_stock_item_vo import (
    WarehouseStockItemVO,
)
from src.modules.products.domain.value_objects.warehouse_stock_vo import (
    WarehouseStockVO,
)
from src.modules.products.infrastructure.persistence.models.product_model import (
    ProductModel,
)
from src.modules.products.infrastructure.persistence.models.stock_model import (
    StockModel,
)
from src.modules.warehouses.infrastructure.persistence.models.warehouse_model import (
    WarehouseModel,
)
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class SQLAlchemyInventoryRepositoryAdapter(InventoryRepositoryPort):
    """Implements InventoryRepositoryPort using SQLAlchemy for database operations.

    This adapter participates in the Unit of Work pattern: it never calls
    ``session.commit()`` or ``session.rollback()`` directly. Transaction
    control is the exclusive responsibility of the
    :class:`SQLAlchemyProductUnitOfWorkAdapter` that owns the session.
    """

    def __init__(
        self, session: AsyncSession, logger_factory_outbound: LoggerFactoryOutboundPort
    ) -> None:
        """Initializes the SQLAlchemyInventoryRepositoryAdapter.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session provided
                by the Unit of Work.
            logger_factory_outbound (LoggerFactoryOutboundPort): The logger factory
                for creating loggers.
        """
        self.session = session
        self._logger = logger_factory_outbound.get_logger(__name__)

    async def find_inventory_by_user_and_warehouse(
        self, user_id: UUID, warehouse_id: UUID, page: int, page_size: int
    ) -> WarehouseStockVO:
        """Finds the inventory of a user for a warehouse.

        Args:
            user_id (UUID): The ID of the user.
            warehouse_id (UUID): The ID of the warehouse.
            page (int): The page number.
            page_size (int): The page size.

        Returns:
            WarehouseStockVO: The warehouse stock.

        Raises:
            InventoryRepositoryException: If any other database error occurs.
        """
        try:
            # Antes
            # offset = page * page_size
            # Ahora
            offset = (page - 1) * page_size

            filters = (
                WarehouseModel.id == warehouse_id,
                ProductModel.supplier_id == user_id,
                WarehouseModel.supplier_id == user_id,
            )

            count_stmt = (
                select(func.count())
                .select_from(StockModel)
                .join(
                    ProductModel,
                    ProductModel.id == StockModel.product_id,
                )
                .join(
                    WarehouseModel,
                    WarehouseModel.id == StockModel.warehouse_id,
                )
                .where(*filters)
            )

            count_result = await self.session.execute(count_stmt)
            elements = count_result.scalar_one()

            stmt = (
                select(
                    ProductModel.id.label("product_id"),
                    ProductModel.supplier_id.label("supplier_id"),
                    ProductModel.name.label("product_name"),
                    StockModel.id.label("stock_id"),
                    StockModel.total_stock,
                    StockModel.available_stock,
                    StockModel.created_at,
                    StockModel.updated_at,
                )
                .join(
                    ProductModel,
                    ProductModel.id == StockModel.product_id,
                )
                .join(
                    WarehouseModel,
                    WarehouseModel.id == StockModel.warehouse_id,
                )
                .where(*filters)
                .offset(offset)
                .limit(page_size)
            )

            result = await self.session.execute(stmt)

            warehouse_stock = [
                WarehouseStockItemVO(
                    stock_id=row.stock_id,
                    product_id=row.product_id,
                    supplier_id=row.supplier_id,
                    name=ProductNameVO(row.product_name),
                    total_stock=TotalStockVO(row.total_stock),
                    available_stock=AvailableStockVO(row.available_stock),
                    stock_disponible=row.total_stock - row.available_stock,
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                )
                for row in result.all()
            ]

            return WarehouseStockVO(
                warehouse_stock=warehouse_stock,
                page=page,
                page_size=page_size,
                elements=elements,
            )

        except SQLAlchemyError as e:
            self._logger.error(
                "Database error while retrieving inventory.", exc_info=str(e)
            )
            raise InventoryRepositoryException(
                "Database error during inventory retrieval."
            ) from e
