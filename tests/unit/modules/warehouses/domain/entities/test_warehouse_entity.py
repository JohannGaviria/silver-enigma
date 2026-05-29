from collections.abc import Callable
from dataclasses import FrozenInstanceError
from typing import Any
from uuid import UUID

import pytest
from faker import Faker

from src.modules.warehouses.domain.entities.warehouse_entity import WarehouseEntity
from src.modules.warehouses.domain.value_objects.warehouse_address_vo import (
    WarehouseAddressVO,
)
from src.modules.warehouses.domain.value_objects.warehouse_name_vo import (
    WarehouseNameVO,
)


class TestWarehouseEntity:
    """Unit test suite for the WarehouseEntity."""

    # ---------------------------------------------------------------------------
    # create
    # ---------------------------------------------------------------------------

    def test_should_create_warehouse_entity_when_valid_data_is_provided(
        self,
        faker: Faker,
    ) -> None:
        """Test that the WarehouseEntity can be created successfully when valid data is provided."""
        supplier_id = UUID(faker.uuid4())
        name = WarehouseNameVO(faker.company())
        address = WarehouseAddressVO(faker.address())

        warehouse = WarehouseEntity.create(
            supplier_id=supplier_id,
            name=name,
            address=address,
        )

        assert warehouse.id is not None
        assert warehouse.supplier_id == supplier_id
        assert warehouse.name == name
        assert warehouse.address == address
        assert warehouse.is_active is True

        assert warehouse.created_at is not None
        assert warehouse.updated_at is not None
        assert warehouse.created_at == warehouse.updated_at

        assert isinstance(warehouse.id, UUID)
        assert isinstance(warehouse.name, WarehouseNameVO)
        assert isinstance(warehouse.address, WarehouseAddressVO)

    def test_should_generate_unique_ids_for_different_warehouse_entities(
        self,
        faker: Faker,
    ) -> None:
        """Test that different WarehouseEntity instances generate unique IDs."""
        supplier_id = UUID(faker.uuid4())
        name = WarehouseNameVO(faker.company())
        address = WarehouseAddressVO(faker.address())

        warehouse1 = WarehouseEntity.create(
            supplier_id=supplier_id,
            name=name,
            address=address,
        )

        warehouse2 = WarehouseEntity.create(
            supplier_id=supplier_id,
            name=name,
            address=address,
        )

        assert warehouse1.id != warehouse2.id

    # ---------------------------------------------------------------------------
    # update
    # ---------------------------------------------------------------------------

    def test_should_update_warehouse_name_and_address_when_values_are_provided(
        self,
        faker: Faker,
    ) -> None:
        """Test that the update method returns a new WarehouseEntity with the updated name and address."""
        warehouse = WarehouseEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )

        new_name = WarehouseNameVO(faker.company())
        new_address = WarehouseAddressVO(faker.address())

        updated_warehouse = warehouse.update(
            name=new_name,
            address=new_address,
        )

        assert updated_warehouse.name == new_name
        assert updated_warehouse.address == new_address

    def test_should_keep_existing_values_when_update_values_are_not_provided(
        self,
        faker: Faker,
    ) -> None:
        """Test that the update method keeps the existing values when new values are not provided."""
        warehouse = WarehouseEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )

        updated_warehouse = warehouse.update()

        assert updated_warehouse.name == warehouse.name
        assert updated_warehouse.address == warehouse.address

    def test_should_update_updated_at_and_preserve_created_at_when_updating_warehouse(
        self,
        faker: Faker,
    ) -> None:
        """Test that the update method updates the updated_at timestamp and preserves the created_at timestamp."""
        warehouse = WarehouseEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )

        updated_warehouse = warehouse.update(
            name=WarehouseNameVO(faker.company()),
        )

        assert updated_warehouse.created_at == warehouse.created_at
        assert updated_warehouse.updated_at > warehouse.updated_at

    def test_should_preserve_warehouse_id_when_updating_warehouse(
        self,
        faker: Faker,
    ) -> None:
        """Test that the update method preserves the warehouse ID."""
        warehouse = WarehouseEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )

        updated_warehouse = warehouse.update(
            name=WarehouseNameVO(faker.company()),
        )

        assert updated_warehouse.id == warehouse.id

    # ---------------------------------------------------------------------------
    # immutability
    # ---------------------------------------------------------------------------

    @pytest.mark.parametrize(
        ("attribute", "value_factory"),
        [
            (
                "name",
                lambda faker: WarehouseNameVO(faker.company()),
            ),
            (
                "address",
                lambda faker: WarehouseAddressVO(faker.address()),
            ),
        ],
    )
    def test_should_raise_exception_when_attempting_to_modify_warehouse_entity_attributes(
        self,
        faker: Faker,
        attribute: str,
        value_factory: Callable[[Faker], Any],
    ) -> None:
        """Test that the WarehouseEntity raises a FrozenInstanceError when attempting to modify its attributes."""
        warehouse = WarehouseEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )

        with pytest.raises(FrozenInstanceError):
            setattr(warehouse, attribute, value_factory(faker))

    # ---------------------------------------------------------------------------
    # equality
    # ---------------------------------------------------------------------------

    def test_should_return_equal_warehouse_entities_when_data_is_identical(
        self,
        faker: Faker,
    ) -> None:
        """Test that two WarehouseEntity instances with identical data are considered equal."""
        supplier_id = UUID(faker.uuid4())
        name = WarehouseNameVO(faker.company())
        address = WarehouseAddressVO(faker.address())

        warehouse1 = WarehouseEntity.create(
            supplier_id=supplier_id,
            name=name,
            address=address,
        )

        warehouse2 = WarehouseEntity(
            id=warehouse1.id,
            supplier_id=warehouse1.supplier_id,
            name=warehouse1.name,
            address=warehouse1.address,
            is_active=warehouse1.is_active,
            created_at=warehouse1.created_at,
            updated_at=warehouse1.updated_at,
        )

        assert warehouse1 == warehouse2
