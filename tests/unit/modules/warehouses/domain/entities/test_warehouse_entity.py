from dataclasses import FrozenInstanceError
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
    def test_should_create_warehouse_entity_when_valid_data_is_provided(
        self, faker: Faker
    ) -> None:
        """Test that the WarehouseEntity can be created successfully when valid data is provided."""
        supplier_id = UUID(faker.uuid4())
        name = WarehouseNameVO(faker.company())
        address = WarehouseAddressVO(faker.address())

        warehouse = WarehouseEntity.create(
            supplier_id=supplier_id, name=name, address=address
        )

        assert warehouse.id is not None
        assert warehouse.supplier_id == supplier_id
        assert warehouse.name == name
        assert warehouse.address == address
        assert warehouse.is_active is True
        assert warehouse.created_at is not None
        assert warehouse.updated_at is not None

    def test_should_return_correct_types_for_warehouse_entity_attributes(
        self, faker: Faker
    ) -> None:
        """Test that the WarehouseEntity attributes return the correct types."""
        warehouse = WarehouseEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )

        assert isinstance(warehouse.id, UUID)
        assert isinstance(warehouse.supplier_id, UUID)
        assert isinstance(warehouse.name, WarehouseNameVO)
        assert isinstance(warehouse.address, WarehouseAddressVO)
        assert isinstance(warehouse.is_active, bool)

    def test_should_set_is_active_to_true_on_creation(self, faker: Faker) -> None:
        """Test that a newly created WarehouseEntity always has is_active set to True."""
        warehouse = WarehouseEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )

        assert warehouse.is_active is True

    def test_should_set_created_at_and_updated_at_to_same_value_on_creation(
        self, faker: Faker
    ) -> None:
        """Test that created_at and updated_at are set to the same timestamp on creation."""
        warehouse = WarehouseEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )

        assert warehouse.created_at == warehouse.updated_at

    def test_should_generate_unique_ids_for_different_warehouse_entities(
        self, faker: Faker
    ) -> None:
        """Test that two different WarehouseEntity instances have unique IDs."""
        name = WarehouseNameVO(faker.company())
        address = WarehouseAddressVO(faker.address())
        supplier_id = UUID(faker.uuid4())

        warehouse1 = WarehouseEntity.create(
            supplier_id=supplier_id, name=name, address=address
        )
        warehouse2 = WarehouseEntity.create(
            supplier_id=supplier_id, name=name, address=address
        )

        assert warehouse1.id != warehouse2.id

    def test_should_raise_exception_when_attempting_to_modify_warehouse_entity_name(
        self, faker: Faker
    ) -> None:
        """Test that the WarehouseEntity raises a FrozenInstanceError.

        when attempting to modify the name after creation.
        """
        warehouse = WarehouseEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )

        with pytest.raises(FrozenInstanceError):
            warehouse.name = WarehouseNameVO(faker.company())  # type: ignore[misc]

    def test_should_raise_exception_when_attempting_to_modify_warehouse_entity_address(
        self, faker: Faker
    ) -> None:
        """Test that the WarehouseEntity raises a FrozenInstanceError.

        when attempting to modify the address after creation.
        """
        warehouse = WarehouseEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )

        with pytest.raises(FrozenInstanceError):
            warehouse.address = WarehouseAddressVO(faker.address())  # type: ignore[misc]

    def test_should_return_equal_warehouse_entities_when_data_is_identical(
        self, faker: Faker
    ) -> None:
        """Test that two WarehouseEntity instances with identical data are considered equal."""
        supplier_id = UUID(faker.uuid4())
        name = WarehouseNameVO(faker.company())
        address = WarehouseAddressVO(faker.address())

        warehouse1 = WarehouseEntity.create(
            supplier_id=supplier_id, name=name, address=address
        )
        warehouse2 = WarehouseEntity(
            id=warehouse1.id,
            supplier_id=supplier_id,
            name=name,
            address=address,
            is_active=warehouse1.is_active,
            created_at=warehouse1.created_at,
            updated_at=warehouse1.updated_at,
        )

        assert warehouse1 == warehouse2
