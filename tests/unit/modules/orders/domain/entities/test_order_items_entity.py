from collections.abc import Callable
from dataclasses import FrozenInstanceError
from decimal import Decimal
from typing import Any
from uuid import UUID

import pytest
from faker import Faker

from src.modules.orders.domain.entities.order_items_entity import OrderItemsEntity
from src.modules.orders.domain.value_objects.quantity_vo import QuantityVO


class TestOrderItemsEntity:
    # ---------------------------------------------------------------------------
    # create
    # ---------------------------------------------------------------------------

    def test_should_create_order_items_entity_when_valid_data_is_provided(
        self,
        faker: Faker,
    ) -> None:
        """Test that the OrderItemsEntity can be created successfully when valid data is provided."""
        order_id = UUID(faker.uuid4())
        product_id = UUID(faker.uuid4())
        quantity = QuantityVO(10)
        unit_price = Decimal("99.99")

        order_item = OrderItemsEntity.create(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
        )

        assert order_item.id is not None
        assert order_item.order_id == order_id
        assert order_item.product_id == product_id
        assert order_item.quantity == quantity
        assert order_item.quantity.value() == 10
        assert order_item.unit_price == unit_price

        assert order_item.created_at is not None
        assert order_item.updated_at is not None
        assert order_item.created_at == order_item.updated_at

        assert isinstance(order_item.id, UUID)
        assert isinstance(order_item.quantity, QuantityVO)
        assert isinstance(order_item.unit_price, Decimal)

    def test_should_create_order_items_entity_with_minimum_quantity(
        self,
        faker: Faker,
    ) -> None:
        """Test that the OrderItemsEntity can be created with quantity of 1."""
        order_id = UUID(faker.uuid4())
        product_id = UUID(faker.uuid4())
        quantity = QuantityVO(1)
        unit_price = Decimal("50.00")

        order_item = OrderItemsEntity.create(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
        )

        assert order_item.quantity.value() == 1

    def test_should_create_order_items_entity_with_large_quantity(
        self,
        faker: Faker,
    ) -> None:
        """Test that the OrderItemsEntity can be created with a large quantity."""
        order_id = UUID(faker.uuid4())
        product_id = UUID(faker.uuid4())
        quantity = QuantityVO(999999)
        unit_price = Decimal("999.99")

        order_item = OrderItemsEntity.create(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
        )

        assert order_item.quantity.value() == 999999

    def test_should_create_order_items_entity_with_decimal_unit_price(
        self,
        faker: Faker,
    ) -> None:
        """Test that the OrderItemsEntity can be created with a decimal unit price."""
        order_id = UUID(faker.uuid4())
        product_id = UUID(faker.uuid4())
        quantity = QuantityVO(5)
        unit_price = Decimal("123.45")

        order_item = OrderItemsEntity.create(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
        )

        assert order_item.unit_price == unit_price
        assert isinstance(order_item.unit_price, Decimal)

    def test_should_generate_unique_ids_for_different_order_items_entities(
        self,
        faker: Faker,
    ) -> None:
        """Test that different OrderItemsEntity instances generate unique IDs."""
        order_id = UUID(faker.uuid4())
        product_id = UUID(faker.uuid4())
        quantity = QuantityVO(10)
        unit_price = Decimal("99.99")

        order_item1 = OrderItemsEntity.create(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
        )

        order_item2 = OrderItemsEntity.create(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
        )

        assert order_item1.id != order_item2.id

    def test_should_create_order_items_entity_with_different_order_ids(
        self,
        faker: Faker,
    ) -> None:
        """Test that OrderItemsEntity can be created with different order IDs."""
        order_id1 = UUID(faker.uuid4())
        order_id2 = UUID(faker.uuid4())
        product_id = UUID(faker.uuid4())
        quantity = QuantityVO(10)
        unit_price = Decimal("99.99")

        order_item1 = OrderItemsEntity.create(
            order_id=order_id1,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
        )

        order_item2 = OrderItemsEntity.create(
            order_id=order_id2,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
        )

        assert order_item1.order_id != order_item2.order_id

    # ---------------------------------------------------------------------------
    # immutability
    # ---------------------------------------------------------------------------

    @pytest.mark.parametrize(
        ("attribute", "value_factory"),
        [
            (
                "order_id",
                lambda faker: UUID(faker.uuid4()),
            ),
            (
                "product_id",
                lambda faker: UUID(faker.uuid4()),
            ),
            (
                "quantity",
                lambda faker: QuantityVO(20),
            ),
            (
                "unit_price",
                lambda faker: Decimal("199.99"),
            ),
        ],
    )
    def test_should_raise_exception_when_attempting_to_modify_order_items_entity_attributes(
        self,
        faker: Faker,
        attribute: str,
        value_factory: Callable[[Faker], Any],
    ) -> None:
        """Test that the OrderItemsEntity raises a FrozenInstanceError when attempting to modify its attributes."""
        order_item = OrderItemsEntity.create(
            order_id=UUID(faker.uuid4()),
            product_id=UUID(faker.uuid4()),
            quantity=QuantityVO(10),
            unit_price=Decimal("99.99"),
        )

        with pytest.raises(FrozenInstanceError):
            setattr(order_item, attribute, value_factory(faker))

    # ---------------------------------------------------------------------------
    # equality
    # ---------------------------------------------------------------------------

    def test_should_return_equal_order_items_entities_when_data_is_identical(
        self,
        faker: Faker,
    ) -> None:
        """Test that two OrderItemsEntity instances with identical data are considered equal."""
        order_id = UUID(faker.uuid4())
        product_id = UUID(faker.uuid4())
        quantity = QuantityVO(10)
        unit_price = Decimal("99.99")

        order_item1 = OrderItemsEntity.create(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
        )

        order_item2 = OrderItemsEntity(
            id=order_item1.id,
            order_id=order_item1.order_id,
            product_id=order_item1.product_id,
            quantity=order_item1.quantity,
            unit_price=order_item1.unit_price,
            created_at=order_item1.created_at,
            updated_at=order_item1.updated_at,
        )

        assert order_item1 == order_item2

    def test_should_return_different_order_items_entities_when_ids_differ(
        self,
        faker: Faker,
    ) -> None:
        """Test that two OrderItemsEntity instances with different IDs are not equal."""
        order_id = UUID(faker.uuid4())
        product_id = UUID(faker.uuid4())
        quantity = QuantityVO(10)
        unit_price = Decimal("99.99")

        order_item1 = OrderItemsEntity.create(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
        )

        order_item2 = OrderItemsEntity.create(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
        )

        assert order_item1 != order_item2

    def test_should_return_different_order_items_entities_when_quantities_differ(
        self,
        faker: Faker,
    ) -> None:
        """Test that two OrderItemsEntity instances with different quantities are not equal."""
        order_id = UUID(faker.uuid4())
        product_id = UUID(faker.uuid4())
        unit_price = Decimal("99.99")

        order_item1 = OrderItemsEntity.create(
            order_id=order_id,
            product_id=product_id,
            quantity=QuantityVO(10),
            unit_price=unit_price,
        )

        order_item2 = OrderItemsEntity.create(
            order_id=order_id,
            product_id=product_id,
            quantity=QuantityVO(20),
            unit_price=unit_price,
        )

        assert order_item1 != order_item2
