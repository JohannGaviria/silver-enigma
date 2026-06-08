from dataclasses import FrozenInstanceError
from typing import Any
from uuid import UUID

import pytest
from faker import Faker

from src.modules.products.domain.entities.inventory_movement_entity import (
    InventoryMovementEntity,
)
from src.modules.products.domain.enums.movement_type_log_enum import (
    MovementTypeLogEnum,
)


class TestInventoryMovementEntity:
    # ---------------------------------------------------------------------------
    # create
    # ---------------------------------------------------------------------------

    def test_should_create_inventory_movement_entity_when_valid_data_is_provided(
        self,
        faker: Faker,
    ) -> None:
        """Test that the InventoryMovementEntity can be created successfully when valid data is provided."""
        product_id = UUID(faker.uuid4())
        warehouse_id = UUID(faker.uuid4())
        order_id = UUID(faker.uuid4())

        movement = InventoryMovementEntity.create(
            product_id=product_id,
            warehouse_id=warehouse_id,
            order_id=order_id,
            movement_type=MovementTypeLogEnum.RESERVE,
            quantity=10,
        )

        assert movement.id is not None
        assert movement.product_id == product_id
        assert movement.warehouse_id == warehouse_id
        assert movement.order_id == order_id
        assert movement.movement_type == MovementTypeLogEnum.RESERVE
        assert movement.quantity == 10

        assert movement.created_at is not None
        assert movement.updated_at is not None
        assert movement.created_at == movement.updated_at

        assert isinstance(movement.id, UUID)

    def test_should_create_inventory_movement_entity_without_order_id(
        self,
        faker: Faker,
    ) -> None:
        """Test that the InventoryMovementEntity can be created when order_id is not provided."""
        movement = InventoryMovementEntity.create(
            product_id=UUID(faker.uuid4()),
            warehouse_id=UUID(faker.uuid4()),
            movement_type=MovementTypeLogEnum.DECREMENT,
            quantity=5,
        )

        assert movement.order_id is None

    def test_should_generate_unique_ids_for_different_inventory_movements(
        self,
        faker: Faker,
    ) -> None:
        """Test that different InventoryMovementEntity instances generate unique IDs."""
        product_id = UUID(faker.uuid4())
        warehouse_id = UUID(faker.uuid4())

        movement1 = InventoryMovementEntity.create(
            product_id=product_id,
            warehouse_id=warehouse_id,
            movement_type=MovementTypeLogEnum.RESERVE,
            quantity=10,
        )

        movement2 = InventoryMovementEntity.create(
            product_id=product_id,
            warehouse_id=warehouse_id,
            movement_type=MovementTypeLogEnum.RESERVE,
            quantity=10,
        )

        assert movement1.id != movement2.id

    # ---------------------------------------------------------------------------
    # immutability
    # ---------------------------------------------------------------------------

    @pytest.mark.parametrize(
        ("attribute", "value"),
        [
            ("quantity", 100),
            ("movement_type", MovementTypeLogEnum.RELEASE),
        ],
    )
    def test_should_raise_exception_when_attempting_to_modify_inventory_movement_attributes(
        self,
        faker: Faker,
        attribute: str,
        value: Any,
    ) -> None:
        """Test that the InventoryMovementEntity raises a FrozenInstanceError when attempting to modify its attributes."""
        movement = InventoryMovementEntity.create(
            product_id=UUID(faker.uuid4()),
            warehouse_id=UUID(faker.uuid4()),
            movement_type=MovementTypeLogEnum.RESERVE,
            quantity=10,
        )

        with pytest.raises(FrozenInstanceError):
            setattr(movement, attribute, value)

    # ---------------------------------------------------------------------------
    # equality
    # ---------------------------------------------------------------------------

    def test_should_return_equal_inventory_movements_when_data_is_identical(
        self,
        faker: Faker,
    ) -> None:
        """Test that two InventoryMovementEntity instances with identical data are considered equal."""
        movement1 = InventoryMovementEntity.create(
            product_id=UUID(faker.uuid4()),
            warehouse_id=UUID(faker.uuid4()),
            order_id=UUID(faker.uuid4()),
            movement_type=MovementTypeLogEnum.RESERVE,
            quantity=10,
        )

        movement2 = InventoryMovementEntity(
            id=movement1.id,
            product_id=movement1.product_id,
            warehouse_id=movement1.warehouse_id,
            order_id=movement1.order_id,
            movement_type=movement1.movement_type,
            quantity=movement1.quantity,
            created_at=movement1.created_at,
            updated_at=movement1.updated_at,
        )

        assert movement1 == movement2
