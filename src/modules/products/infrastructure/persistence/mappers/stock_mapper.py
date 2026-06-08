"""This module contains the StockPersistenceMapper class."""

from src.modules.products.domain.entities.stock_entity import StockEntity
from src.modules.products.domain.value_objects.available_stock_vo import (
    AvailableStockVO,
)
from src.modules.products.domain.value_objects.total_stock_vo import TotalStockVO
from src.modules.products.infrastructure.persistence.models.stock_model import (
    StockModel,
)


class StockPersistenceMapper:
    """Mapper for StockModel to StockEntity."""

    @staticmethod
    def to_entity(model: StockModel) -> StockEntity:
        """Map a StockModel to a StockEntity.

        Args:
            model (StockModel): The StockModel to be mapped.

        Returns:
            StockEntity: The mapped StockEntity.
        """
        return StockEntity(
            id=model.id,
            product_id=model.product_id,
            warehouse_id=model.warehouse_id,
            total_stock=TotalStockVO(model.total_stock),
            available_stock=AvailableStockVO(model.available_stock),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: StockEntity) -> StockModel:
        """Map a StockEntity to a StockModel.

        Args:
            entity (StockEntity): The StockEntity to be mapped.

        Returns:
            StockModel: The mapped StockModel.
        """
        return StockModel(
            id=entity.id,
            product_id=entity.product_id,
            warehouse_id=entity.warehouse_id,
            total_stock=entity.total_stock.value(),
            available_stock=entity.available_stock.value(),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
