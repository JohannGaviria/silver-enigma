"""Tests for the WarehouseBySupplierCacheKeyVO value object."""

from dataclasses import FrozenInstanceError
from uuid import UUID

import pytest
from faker import Faker

from src.modules.warehouses.domain.value_objects.warehouse_by_supplier_cache_key_vo import (
    WarehouseBySupplierCacheKeyVO,
)


class TestWarehouseBySupplierCacheKeyVO:
    def test_should_create_cache_key_when_valid_supplier_id_is_provided(
        self, faker: Faker
    ) -> None:
        """from_supplier_id must return a WarehouseBySupplierCacheKeyVO instance."""
        supplier_id = UUID(faker.uuid4())

        key_vo = WarehouseBySupplierCacheKeyVO.from_supplier_id(supplier_id)

        assert isinstance(key_vo, WarehouseBySupplierCacheKeyVO)

    def test_should_embed_supplier_id_in_cache_key_string(self, faker: Faker) -> None:
        """The resulting key string must contain the supplier UUID."""
        supplier_id = UUID(faker.uuid4())

        key_vo = WarehouseBySupplierCacheKeyVO.from_supplier_id(supplier_id)

        assert str(supplier_id) in key_vo.key

    def test_should_use_expected_key_prefix(self, faker: Faker) -> None:
        """The key must start with the established namespace prefix."""
        supplier_id = UUID(faker.uuid4())

        key_vo = WarehouseBySupplierCacheKeyVO.from_supplier_id(supplier_id)

        assert key_vo.key.startswith("cache:warehouses_by_supplier:")

    def test_should_produce_exact_key_format(self, faker: Faker) -> None:
        """The key must follow the exact pattern 'cache:warehouses_by_supplier:<uuid>'."""
        supplier_id = UUID(faker.uuid4())

        key_vo = WarehouseBySupplierCacheKeyVO.from_supplier_id(supplier_id)

        assert key_vo.key == f"cache:warehouses_by_supplier:{supplier_id}"

    def test_should_produce_unique_keys_for_different_supplier_ids(
        self, faker: Faker
    ) -> None:
        """Two different supplier IDs must produce two different cache keys."""
        key_a = WarehouseBySupplierCacheKeyVO.from_supplier_id(UUID(faker.uuid4()))
        key_b = WarehouseBySupplierCacheKeyVO.from_supplier_id(UUID(faker.uuid4()))

        assert key_a.key != key_b.key

    def test_should_produce_identical_keys_for_the_same_supplier_id(
        self, faker: Faker
    ) -> None:
        """The same supplier ID must always yield the same cache key."""
        supplier_id = UUID(faker.uuid4())

        key_a = WarehouseBySupplierCacheKeyVO.from_supplier_id(supplier_id)
        key_b = WarehouseBySupplierCacheKeyVO.from_supplier_id(supplier_id)

        assert key_a.key == key_b.key

    def test_should_be_equal_when_built_from_the_same_supplier_id(
        self, faker: Faker
    ) -> None:
        """Two instances built from the same supplier ID must compare as equal."""
        supplier_id = UUID(faker.uuid4())

        assert WarehouseBySupplierCacheKeyVO.from_supplier_id(
            supplier_id
        ) == WarehouseBySupplierCacheKeyVO.from_supplier_id(supplier_id)

    def test_should_not_be_equal_when_built_from_different_supplier_ids(
        self, faker: Faker
    ) -> None:
        """Two instances built from different supplier IDs must not be equal."""
        assert WarehouseBySupplierCacheKeyVO.from_supplier_id(
            UUID(faker.uuid4())
        ) != WarehouseBySupplierCacheKeyVO.from_supplier_id(UUID(faker.uuid4()))

    def test_should_be_usable_as_dict_key(self, faker: Faker) -> None:
        """The VO must be hashable so it can be used as a dictionary key."""
        supplier_id = UUID(faker.uuid4())
        key_vo = WarehouseBySupplierCacheKeyVO.from_supplier_id(supplier_id)

        mapping = {key_vo: "value"}

        assert mapping[key_vo] == "value"

    def test_should_raise_exception_when_attempting_to_modify_key(
        self, faker: Faker
    ) -> None:
        """The VO must be frozen — mutating the key attribute must raise FrozenInstanceError."""
        key_vo = WarehouseBySupplierCacheKeyVO.from_supplier_id(UUID(faker.uuid4()))

        with pytest.raises(FrozenInstanceError):
            key_vo.key = "cache:warehouses_by_supplier:other"  # type: ignore[misc]
