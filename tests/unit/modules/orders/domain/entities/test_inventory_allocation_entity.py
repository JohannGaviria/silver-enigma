from collections.abc import Callable
from dataclasses import FrozenInstanceError
from typing import Any
from uuid import UUID

import pytest
from faker import Faker

from src.modules.orders.domain.entities.inventory_allocation_entity import (
    InventoryAllocationEntity,
)
from src.modules.orders.domain.value_objects.quantity_vo import QuantityVO


class TestInventoryAllocationEntity:
    # ---------------------------------------------------------------------------
    # create
    # ---------------------------------------------------------------------------

    def test_should_create_inventory_allocation_entity_when_valid_data_is_provided(
        self,
        faker: Faker,
    ) -> None:
        """Test that the InventoryAllocationEntity can be created successfully when valid data is provided."""
        order_item_id = UUID(faker.uuid4())
        warehouse_id = UUID(faker.uuid4())
        quantity = QuantityVO(10)

        allocation = InventoryAllocationEntity.create(
            order_item_id=order_item_id,
            warehouse_id=warehouse_id,
            quantity=quantity,
        )

        assert allocation.id is not None
        assert allocation.order_item_id == order_item_id
        assert allocation.warehouse_id == warehouse_id
        assert allocation.quantity == quantity
        assert allocation.quantity.value() == 10

        assert allocation.created_at is not None
        assert allocation.updated_at is not None
        assert allocation.created_at == allocation.updated_at

        assert isinstance(allocation.id, UUID)
        assert isinstance(allocation.quantity, QuantityVO)

    def test_should_create_inventory_allocation_entity_with_minimum_quantity(
        self,
        faker: Faker,
    ) -> None:
        """Test that the InventoryAllocationEntity can be created with quantity of 1."""
        order_item_id = UUID(faker.uuid4())
        warehouse_id = UUID(faker.uuid4())
        quantity = QuantityVO(1)

        allocation = InventoryAllocationEntity.create(
            order_item_id=order_item_id,
            warehouse_id=warehouse_id,
            quantity=quantity,
        )

        assert allocation.quantity.value() == 1

    def test_should_create_inventory_allocation_entity_with_large_quantity(
        self,
        faker: Faker,
    ) -> None:
        """Test that the InventoryAllocationEntity can be created with a large quantity."""
        order_item_id = UUID(faker.uuid4())
        warehouse_id = UUID(faker.uuid4())
        quantity = QuantityVO(999999)

        allocation = InventoryAllocationEntity.create(
            order_item_id=order_item_id,
            warehouse_id=warehouse_id,
            quantity=quantity,
        )

        assert allocation.quantity.value() == 999999

    def test_should_generate_unique_ids_for_different_inventory_allocation_entities(
        self,
        faker: Faker,
    ) -> None:
        """Test that different InventoryAllocationEntity instances generate unique IDs."""
        order_item_id = UUID(faker.uuid4())
        warehouse_id = UUID(faker.uuid4())
        quantity = QuantityVO(10)

        allocation1 = InventoryAllocationEntity.create(
            order_item_id=order_item_id,
            warehouse_id=warehouse_id,
            quantity=quantity,
        )

        allocation2 = InventoryAllocationEntity.create(
            order_item_id=order_item_id,
            warehouse_id=warehouse_id,
            quantity=quantity,
        )

        assert allocation1.id != allocation2.id

    def test_should_create_inventory_allocation_entity_with_different_order_item_ids(
        self,
        faker: Faker,
    ) -> None:
        """Test that InventoryAllocationEntity can be created with different order item IDs."""
        order_item_id1 = UUID(faker.uuid4())
        order_item_id2 = UUID(faker.uuid4())
        warehouse_id = UUID(faker.uuid4())
        quantity = QuantityVO(10)

        allocation1 = InventoryAllocationEntity.create(
            order_item_id=order_item_id1,
            warehouse_id=warehouse_id,
            quantity=quantity,
        )

        allocation2 = InventoryAllocationEntity.create(
            order_item_id=order_item_id2,
            warehouse_id=warehouse_id,
            quantity=quantity,
        )

        assert allocation1.order_item_id != allocation2.order_item_id

    def test_should_create_inventory_allocation_entity_with_different_warehouse_ids(
        self,
        faker: Faker,
    ) -> None:
        """Test that InventoryAllocationEntity can be created with different warehouse IDs.

        This models the case where a single order item is fulfilled by
        splitting its quantity across multiple warehouses (ADR-013).
        """
        order_item_id = UUID(faker.uuid4())
        warehouse_id1 = UUID(faker.uuid4())
        warehouse_id2 = UUID(faker.uuid4())
        quantity = QuantityVO(5)

        allocation1 = InventoryAllocationEntity.create(
            order_item_id=order_item_id,
            warehouse_id=warehouse_id1,
            quantity=quantity,
        )

        allocation2 = InventoryAllocationEntity.create(
            order_item_id=order_item_id,
            warehouse_id=warehouse_id2,
            quantity=quantity,
        )

        assert allocation1.order_item_id == allocation2.order_item_id
        assert allocation1.warehouse_id != allocation2.warehouse_id

    # ---------------------------------------------------------------------------
    # immutability
    # ---------------------------------------------------------------------------

    @pytest.mark.parametrize(
        ("attribute", "value_factory"),
        [
            (
                "order_item_id",
                lambda faker: UUID(faker.uuid4()),
            ),
            (
                "warehouse_id",
                lambda faker: UUID(faker.uuid4()),
            ),
            (
                "quantity",
                lambda faker: QuantityVO(20),
            ),
        ],
    )
    def test_should_raise_exception_when_attempting_to_modify_inventory_allocation_entity_attributes(
        self,
        faker: Faker,
        attribute: str,
        value_factory: Callable[[Faker], Any],
    ) -> None:
        """Test that the InventoryAllocationEntity raises a FrozenInstanceError when attempting to modify its attributes."""
        allocation = InventoryAllocationEntity.create(
            order_item_id=UUID(faker.uuid4()),
            warehouse_id=UUID(faker.uuid4()),
            quantity=QuantityVO(10),
        )

        with pytest.raises(FrozenInstanceError):
            setattr(allocation, attribute, value_factory(faker))

    # ---------------------------------------------------------------------------
    # equality
    # ---------------------------------------------------------------------------

    def test_should_return_equal_inventory_allocation_entities_when_data_is_identical(
        self,
        faker: Faker,
    ) -> None:
        """Test that two InventoryAllocationEntity instances with identical data are considered equal."""
        order_item_id = UUID(faker.uuid4())
        warehouse_id = UUID(faker.uuid4())
        quantity = QuantityVO(10)

        allocation1 = InventoryAllocationEntity.create(
            order_item_id=order_item_id,
            warehouse_id=warehouse_id,
            quantity=quantity,
        )

        allocation2 = InventoryAllocationEntity(
            id=allocation1.id,
            order_item_id=allocation1.order_item_id,
            warehouse_id=allocation1.warehouse_id,
            quantity=allocation1.quantity,
            created_at=allocation1.created_at,
            updated_at=allocation1.updated_at,
        )

        assert allocation1 == allocation2

    def test_should_return_different_inventory_allocation_entities_when_ids_differ(
        self,
        faker: Faker,
    ) -> None:
        """Test that two InventoryAllocationEntity instances with different IDs are not equal."""
        order_item_id = UUID(faker.uuid4())
        warehouse_id = UUID(faker.uuid4())
        quantity = QuantityVO(10)

        allocation1 = InventoryAllocationEntity.create(
            order_item_id=order_item_id,
            warehouse_id=warehouse_id,
            quantity=quantity,
        )

        allocation2 = InventoryAllocationEntity.create(
            order_item_id=order_item_id,
            warehouse_id=warehouse_id,
            quantity=quantity,
        )

        assert allocation1 != allocation2

    def test_should_return_different_inventory_allocation_entities_when_quantities_differ(
        self,
        faker: Faker,
    ) -> None:
        """Test that two InventoryAllocationEntity instances with different quantities are not equal."""
        order_item_id = UUID(faker.uuid4())
        warehouse_id = UUID(faker.uuid4())

        allocation1 = InventoryAllocationEntity.create(
            order_item_id=order_item_id,
            warehouse_id=warehouse_id,
            quantity=QuantityVO(10),
        )

        allocation2 = InventoryAllocationEntity.create(
            order_item_id=order_item_id,
            warehouse_id=warehouse_id,
            quantity=QuantityVO(20),
        )

        assert allocation1 != allocation2
