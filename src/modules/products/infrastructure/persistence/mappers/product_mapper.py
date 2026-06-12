"""This module contains the ProductMapper class."""

from src.modules.products.domain.entities.product_entity import ProductEntity
from src.modules.products.domain.enums.unit_of_measure_enum import UnitOfMeasureEnum
from src.modules.products.domain.value_objects.product_name_vo import ProductNameVO
from src.modules.products.domain.value_objects.unit_price_vo import UnitPriceVO
from src.modules.products.infrastructure.persistence.models.product_model import (
    ProductModel,
)


class ProductPersistenceMapper:
    """Class responsible for mapping Product entities to and from SQLAlchemy models."""

    @staticmethod
    def to_entity(model: ProductModel) -> ProductEntity:
        """Map a SQLAlchemy model to a Product entity.

        Args:
            model (ProductModel): The SQLAlchemy model to map.

        Returns:
            ProductEntity: The mapped Product entity.
        """
        return ProductEntity(
            id=model.id,
            supplier_id=model.supplier_id,
            name=ProductNameVO(model.name),
            description=model.description,
            unit_of_measure=UnitOfMeasureEnum(model.unit_of_measure),
            unit_price=UnitPriceVO(model.unit_price),
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: ProductEntity) -> ProductModel:
        """Map a Product entity to a SQLAlchemy model.

        Args:
            entity (ProductEntity): The Product entity to map.

        Returns:
            ProductModel: The mapped SQLAlchemy model.
        """
        return ProductModel(
            id=entity.id,
            supplier_id=entity.supplier_id,
            name=str(entity.name),
            description=entity.description,
            unit_of_measure=entity.unit_of_measure.value,
            unit_price=entity.unit_price.value(),
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
