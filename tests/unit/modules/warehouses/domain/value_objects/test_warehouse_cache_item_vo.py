"""Tests for the WarehouseCacheItemVO value object."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import pytest
from faker import Faker

from src.modules.warehouses.domain.value_objects.warehouse_address_vo import (
    WarehouseAddressVO,
)
from src.modules.warehouses.domain.value_objects.warehouse_cache_item_vo import (
    WarehouseCacheItemVO,
)
from src.modules.warehouses.domain.value_objects.warehouse_name_vo import (
    WarehouseNameVO,
)


def _make_cache_item(
    faker: Faker,
    **overrides: Any,
) -> WarehouseCacheItemVO:
    now = datetime.now(UTC)

    return WarehouseCacheItemVO(
        id=overrides.get("id", UUID(faker.uuid4())),
        supplier_id=overrides.get("supplier_id", UUID(faker.uuid4())),
        name=overrides.get("name", WarehouseNameVO(faker.company())),
        address=overrides.get("address", WarehouseAddressVO(faker.address())),
        is_active=overrides.get("is_active", True),
        created_at=overrides.get("created_at", now),
        updated_at=overrides.get("updated_at", now),
    )


class TestWarehouseCacheItemVO:
    def test_should_create_cache_item_vo_when_valid_data_is_provided(
        self, faker: Faker
    ) -> None:
        """WarehouseCacheItemVO must be created successfully with valid arguments."""
        item = _make_cache_item(faker)

        assert item is not None

    def test_should_store_all_provided_field_values(self, faker: Faker) -> None:
        """Every field passed to the constructor must be stored and retrievable."""
        now = datetime.now(UTC)
        supplier_id = UUID(faker.uuid4())
        warehouse_id = UUID(faker.uuid4())
        name = WarehouseNameVO(faker.company())
        address = WarehouseAddressVO(faker.address())

        item = WarehouseCacheItemVO(
            id=warehouse_id,
            supplier_id=supplier_id,
            name=name,
            address=address,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        assert item.id == warehouse_id
        assert item.supplier_id == supplier_id
        assert item.name == name
        assert item.address == address
        assert item.is_active is True
        assert item.created_at == now
        assert item.updated_at == now

    def test_should_store_is_active_false_when_provided(self, faker: Faker) -> None:
        """is_active must be stored as False when explicitly set to False."""
        item = _make_cache_item(faker, is_active=False)

        assert item.is_active is False

    def test_should_return_correct_types_for_all_attributes(self, faker: Faker) -> None:
        """Each attribute must return the expected type."""
        item = _make_cache_item(faker)

        assert isinstance(item.id, UUID)
        assert isinstance(item.supplier_id, UUID)
        assert isinstance(item.name, WarehouseNameVO)
        assert isinstance(item.address, WarehouseAddressVO)
        assert isinstance(item.is_active, bool)
        assert isinstance(item.created_at, datetime)
        assert isinstance(item.updated_at, datetime)

    def test_should_raise_exception_when_attempting_to_modify_id(
        self, faker: Faker
    ) -> None:
        """Mutating the id field must raise FrozenInstanceError."""
        item = _make_cache_item(faker)

        with pytest.raises(FrozenInstanceError):
            item.id = UUID(faker.uuid4())  # type: ignore[misc]

    def test_should_raise_exception_when_attempting_to_modify_supplier_id(
        self, faker: Faker
    ) -> None:
        """Mutating the supplier_id field must raise FrozenInstanceError."""
        item = _make_cache_item(faker)

        with pytest.raises(FrozenInstanceError):
            item.supplier_id = UUID(faker.uuid4())  # type: ignore[misc]

    def test_should_raise_exception_when_attempting_to_modify_name(
        self, faker: Faker
    ) -> None:
        """Mutating the name field must raise FrozenInstanceError."""
        item = _make_cache_item(faker)

        with pytest.raises(FrozenInstanceError):
            item.name = WarehouseNameVO(faker.company())  # type: ignore[misc]

    def test_should_raise_exception_when_attempting_to_modify_address(
        self, faker: Faker
    ) -> None:
        """Mutating the address field must raise FrozenInstanceError."""
        item = _make_cache_item(faker)

        with pytest.raises(FrozenInstanceError):
            item.address = WarehouseAddressVO(faker.address())  # type: ignore[misc]

    def test_should_raise_exception_when_attempting_to_modify_is_active(
        self, faker: Faker
    ) -> None:
        """Mutating the is_active field must raise FrozenInstanceError."""
        item = _make_cache_item(faker)

        with pytest.raises(FrozenInstanceError):
            item.is_active = False  # type: ignore[misc]

    def test_should_be_equal_when_all_fields_are_identical(self, faker: Faker) -> None:
        """Two WarehouseCacheItemVO instances with identical fields must be equal."""
        now = datetime.now(UTC)
        warehouse_id = UUID(faker.uuid4())
        supplier_id = UUID(faker.uuid4())
        name = WarehouseNameVO(faker.company())
        address = WarehouseAddressVO(faker.address())

        item_a = WarehouseCacheItemVO(
            id=warehouse_id,
            supplier_id=supplier_id,
            name=name,
            address=address,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        item_b = WarehouseCacheItemVO(
            id=warehouse_id,
            supplier_id=supplier_id,
            name=name,
            address=address,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        assert item_a == item_b

    def test_should_not_be_equal_when_ids_differ(self, faker: Faker) -> None:
        """Two instances that differ only in id must not be equal."""
        now = datetime.now(UTC)
        supplier_id = UUID(faker.uuid4())
        name = WarehouseNameVO(faker.company())
        address = WarehouseAddressVO(faker.address())

        item_a = WarehouseCacheItemVO(
            id=UUID(faker.uuid4()),
            supplier_id=supplier_id,
            name=name,
            address=address,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        item_b = WarehouseCacheItemVO(
            id=UUID(faker.uuid4()),
            supplier_id=supplier_id,
            name=name,
            address=address,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        assert item_a != item_b

    def test_should_not_be_equal_when_supplier_ids_differ(self, faker: Faker) -> None:
        """Two instances that differ only in supplier_id must not be equal."""
        now = datetime.now(UTC)
        warehouse_id = UUID(faker.uuid4())
        name = WarehouseNameVO(faker.company())
        address = WarehouseAddressVO(faker.address())

        item_a = WarehouseCacheItemVO(
            id=warehouse_id,
            supplier_id=UUID(faker.uuid4()),
            name=name,
            address=address,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        item_b = WarehouseCacheItemVO(
            id=warehouse_id,
            supplier_id=UUID(faker.uuid4()),
            name=name,
            address=address,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        assert item_a != item_b
