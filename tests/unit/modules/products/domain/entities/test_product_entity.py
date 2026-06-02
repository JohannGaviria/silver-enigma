from collections.abc import Callable
from dataclasses import FrozenInstanceError
from decimal import Decimal
from typing import Any
from uuid import UUID

import pytest
from faker import Faker

from src.modules.products.domain.entities.product_entity import ProductEntity
from src.modules.products.domain.enums.unit_of_measure_enum import UnitOfMeasureEnum
from src.modules.products.domain.value_objects.product_name_vo import ProductNameVO
from src.modules.products.domain.value_objects.unit_price_vo import UnitPriceVO


class TestProductEntity:
    # ---------------------------------------------------------------------------
    # create
    # ---------------------------------------------------------------------------

    def test_should_create_product_entity_when_valid_data_is_provided(
        self,
        faker: Faker,
    ) -> None:
        """Test that the ProductEntity can be created successfully when valid data is provided."""
        supplier_id = UUID(faker.uuid4())
        name = ProductNameVO(faker.company())
        description = faker.text(max_nb_chars=200)
        unit_of_measure = UnitOfMeasureEnum.UNIT
        unit_price = UnitPriceVO(Decimal(1000))

        product = ProductEntity.create(
            supplier_id=supplier_id,
            name=name,
            description=description,
            unit_of_measure=unit_of_measure,
            unit_price=unit_price,
        )

        assert product.id is not None
        assert product.supplier_id == supplier_id
        assert product.name == name
        assert product.description == description
        assert product.unit_of_measure == unit_of_measure
        assert product.unit_price == unit_price
        assert product.is_active is True

        assert product.created_at is not None
        assert product.updated_at is not None
        assert product.created_at == product.updated_at

        assert isinstance(product.id, UUID)
        assert isinstance(product.name, ProductNameVO)
        assert isinstance(product.unit_price, UnitPriceVO)
        assert isinstance(product.unit_of_measure, UnitOfMeasureEnum)

    def test_should_generate_unique_ids_for_different_product_entities(
        self,
        faker: Faker,
    ) -> None:
        """Test that different ProductEntity instances generate unique IDs."""
        supplier_id = UUID(faker.uuid4())

        product1 = ProductEntity.create(
            supplier_id=supplier_id,
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal(1000)),
        )

        product2 = ProductEntity.create(
            supplier_id=supplier_id,
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal(1000)),
        )

        assert product1.id != product2.id

    # ---------------------------------------------------------------------------
    # update
    # ---------------------------------------------------------------------------

    def test_should_update_product_attributes_when_values_are_provided(
        self,
        faker: Faker,
    ) -> None:
        """Test that the update method returns a new ProductEntity with the updated attributes."""
        product = ProductEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal(1000)),
        )

        new_name = ProductNameVO(faker.company())
        new_description = faker.text()
        new_unit_of_measure = UnitOfMeasureEnum.KG
        new_unit_price = UnitPriceVO(Decimal(2000))

        updated_product = product.update(
            name=new_name,
            description=new_description,
            unit_of_measure=new_unit_of_measure,
            unit_price=new_unit_price,
        )

        assert updated_product.name == new_name
        assert updated_product.description == new_description
        assert updated_product.unit_of_measure == new_unit_of_measure
        assert updated_product.unit_price == new_unit_price

    def test_should_keep_existing_values_when_update_values_are_not_provided(
        self,
        faker: Faker,
    ) -> None:
        """Test that the update method keeps the existing values when new values are not provided."""
        product = ProductEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal(1000)),
        )

        updated_product = product.update()

        assert updated_product.name == product.name
        assert updated_product.description == product.description
        assert updated_product.unit_of_measure == product.unit_of_measure
        assert updated_product.unit_price == product.unit_price

    def test_should_update_only_name_when_other_values_are_not_provided(
        self,
        faker: Faker,
    ) -> None:
        """Test that the update method updates only the name when other values are not provided."""
        product = ProductEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal(1000)),
        )

        new_name = ProductNameVO(faker.company())

        updated_product = product.update(
            name=new_name,
        )

        assert updated_product.name == new_name
        assert updated_product.description == product.description
        assert updated_product.unit_of_measure == product.unit_of_measure
        assert updated_product.unit_price == product.unit_price

    def test_should_update_only_description_when_other_values_are_not_provided(
        self,
        faker: Faker,
    ) -> None:
        """Test that the update method updates only the description when other values are not provided."""
        product = ProductEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal(1000)),
        )

        new_description = faker.text()

        updated_product = product.update(
            description=new_description,
        )

        assert updated_product.name == product.name
        assert updated_product.description == new_description
        assert updated_product.unit_of_measure == product.unit_of_measure
        assert updated_product.unit_price == product.unit_price

    def test_should_update_only_unit_of_measure_when_other_values_are_not_provided(
        self,
        faker: Faker,
    ) -> None:
        """Test that the update method updates only the unit_of_measure when other values are not provided."""
        product = ProductEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal(1000)),
        )

        updated_product = product.update(
            unit_of_measure=UnitOfMeasureEnum.KG,
        )

        assert updated_product.name == product.name
        assert updated_product.description == product.description
        assert updated_product.unit_of_measure == UnitOfMeasureEnum.KG
        assert updated_product.unit_price == product.unit_price

    def test_should_update_only_unit_price_when_other_values_are_not_provided(
        self,
        faker: Faker,
    ) -> None:
        """Test that the update method updates only the unit_price when other values are not provided."""
        product = ProductEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal(1000)),
        )

        new_unit_price = UnitPriceVO(Decimal(5000))

        updated_product = product.update(
            unit_price=new_unit_price,
        )

        assert updated_product.name == product.name
        assert updated_product.description == product.description
        assert updated_product.unit_of_measure == product.unit_of_measure
        assert updated_product.unit_price == new_unit_price

    def test_should_update_updated_at_and_preserve_created_at_when_updating_product(
        self,
        faker: Faker,
    ) -> None:
        """Test that the update method updates the updated_at timestamp and preserves the created_at timestamp."""
        product = ProductEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal(1000)),
        )

        updated_product = product.update(
            name=ProductNameVO(faker.company()),
        )

        assert updated_product.created_at == product.created_at
        assert updated_product.updated_at > product.updated_at

    def test_should_preserve_product_id_when_updating_product(
        self,
        faker: Faker,
    ) -> None:
        """Test that the update method preserves the product ID."""
        product = ProductEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal(1000)),
        )

        updated_product = product.update(
            name=ProductNameVO(faker.company()),
        )

        assert updated_product.id == product.id

    def test_should_preserve_supplier_id_when_updating_product(
        self,
        faker: Faker,
    ) -> None:
        """Test that the update method preserves the supplier ID."""
        supplier_id = UUID(faker.uuid4())

        product = ProductEntity.create(
            supplier_id=supplier_id,
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal(1000)),
        )

        updated_product = product.update(
            name=ProductNameVO(faker.company()),
        )

        assert updated_product.supplier_id == supplier_id

    def test_should_preserve_is_active_when_updating_product(
        self,
        faker: Faker,
    ) -> None:
        """Test that the update method preserves the is_active attribute."""
        product = ProductEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal(1000)),
        )

        updated_product = product.update(
            name=ProductNameVO(faker.company()),
        )

        assert updated_product.is_active == product.is_active

    # ---------------------------------------------------------------------------
    # immutability
    # ---------------------------------------------------------------------------

    @pytest.mark.parametrize(
        ("attribute", "value_factory"),
        [
            (
                "name",
                lambda faker: ProductNameVO(faker.company()),
            ),
            (
                "description",
                lambda faker: faker.text(),
            ),
            (
                "unit_of_measure",
                lambda faker: UnitOfMeasureEnum.KG,
            ),
            (
                "unit_price",
                lambda faker: UnitPriceVO(Decimal(2000)),
            ),
        ],
    )
    def test_should_raise_exception_when_attempting_to_modify_product_entity_attributes(
        self,
        faker: Faker,
        attribute: str,
        value_factory: Callable[[Faker], Any],
    ) -> None:
        """Test that the ProductEntity raises a FrozenInstanceError when attempting to modify its attributes."""
        product = ProductEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal(1000)),
        )

        with pytest.raises(FrozenInstanceError):
            setattr(product, attribute, value_factory(faker))

    # ---------------------------------------------------------------------------
    # equality
    # ---------------------------------------------------------------------------

    def test_should_return_equal_product_entities_when_data_is_identical(
        self,
        faker: Faker,
    ) -> None:
        """Test that two ProductEntity instances with identical data are considered equal."""
        supplier_id = UUID(faker.uuid4())
        name = ProductNameVO(faker.company())
        description = faker.text(max_nb_chars=200)
        unit_of_measure = UnitOfMeasureEnum.UNIT
        unit_price = UnitPriceVO(Decimal(1000))

        product1 = ProductEntity.create(
            supplier_id=supplier_id,
            name=name,
            description=description,
            unit_of_measure=unit_of_measure,
            unit_price=unit_price,
        )

        product2 = ProductEntity(
            id=product1.id,
            supplier_id=product1.supplier_id,
            name=product1.name,
            description=product1.description,
            unit_of_measure=product1.unit_of_measure,
            unit_price=product1.unit_price,
            is_active=product1.is_active,
            created_at=product1.created_at,
            updated_at=product1.updated_at,
        )

        assert product1 == product2
