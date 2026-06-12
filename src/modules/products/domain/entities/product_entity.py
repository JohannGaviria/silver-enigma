"""This module contains the ProductEntity class."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.modules.products.domain.enums.unit_of_measure_enum import UnitOfMeasureEnum
from src.modules.products.domain.value_objects.product_name_vo import ProductNameVO
from src.modules.products.domain.value_objects.unit_price_vo import UnitPriceVO
from src.shared.domain.entities.base_entity import BaseEntity


@dataclass(frozen=True)
class ProductEntity(BaseEntity):
    """Entity representing a product.

    Attributes:
        supplier_id (UUID): The ID of the supplier that owns the product.
        name (ProductNameVO): The name of the product.
        description (str): A description of the product.
        unit_of_measure (UnitOfMeasureEnum): The unit of measure used to
            measure the product.
        unit_price (UnitPriceVO): The unit price of the product.
        is_active (bool): A flag indicating whether the product is active.
    """

    supplier_id: UUID
    name: ProductNameVO
    description: str
    unit_of_measure: UnitOfMeasureEnum
    unit_price: UnitPriceVO
    is_active: bool

    @classmethod
    def create(
        cls,
        supplier_id: UUID,
        name: ProductNameVO,
        description: str,
        unit_of_measure: UnitOfMeasureEnum,
        unit_price: UnitPriceVO,
    ) -> "ProductEntity":
        """Factory method to create a new ProductEntity.

        This method creates a new ProductEntity instance with the specified
        attributes. It sets the created_at and updated_at attributes to the
        current UTC datetime.

        Args:
            supplier_id (UUID): The ID of the supplier that owns the product.
            name (ProductNameVO): The name of the product.
            description (str): A description of the product.
            unit_of_measure (UnitOfMeasureEnum): The unit of measure used to
                measure the product.
            unit_price (UnitPriceVO): The unit price of the product.

        Returns:
            ProductEntity: A new ProductEntity instance.
        """
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            supplier_id=supplier_id,
            name=name,
            description=description,
            unit_of_measure=unit_of_measure,
            unit_price=unit_price,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

    def update(
        self,
        name: ProductNameVO | None = None,
        description: str | None = None,
        unit_of_measure: UnitOfMeasureEnum | None = None,
        unit_price: UnitPriceVO | None = None,
    ) -> "ProductEntity":
        """Factory method to update the attributes of the ProductEntity.

        This method updates the attributes of the ProductEntity instance with
        the specified values. It sets the updated_at attribute to the current
        UTC datetime.

        Args:
            name (ProductNameVO | None): The new name of the product.
            description (str | None): The new description of the product.
            unit_of_measure (UnitOfMeasureEnum | None): The new unit of measure
                of the product.
            unit_price (UnitPriceVO | None): The new unit price of the product.

        Returns:
            ProductEntity: The updated ProductEntity instance.
        """
        now = datetime.now(UTC)
        return ProductEntity(
            id=self.id,
            supplier_id=self.supplier_id,
            name=name if name is not None else self.name,
            description=description if description is not None else self.description,
            unit_of_measure=unit_of_measure
            if unit_of_measure is not None
            else self.unit_of_measure,
            unit_price=unit_price if unit_price is not None else self.unit_price,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=now,
        )

    def update_is_active(self, is_active: bool) -> "ProductEntity":
        """Factory method to update the is_active attribute of the ProductEntity.

        This method updates the is_active attribute of the ProductEntity instance with
        the specified value. It sets the updated_at attribute to the current
        UTC datetime.

        Args:
            is_active (bool): The new is_active value of the product.

        Returns:
            ProductEntity: The updated ProductEntity instance.
        """
        now = datetime.now(UTC)
        return ProductEntity(
            id=self.id,
            supplier_id=self.supplier_id,
            name=self.name,
            description=self.description,
            unit_of_measure=self.unit_of_measure,
            unit_price=self.unit_price,
            is_active=is_active,
            created_at=self.created_at,
            updated_at=now,
        )
