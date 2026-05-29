"""Tests for the WarehouseBySupplierCacheValueVO value object."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from uuid import UUID

import pytest
from faker import Faker

from src.modules.warehouses.domain.entities.warehouse_entity import WarehouseEntity
from src.modules.warehouses.domain.value_objects.warehouse_address_vo import (
    WarehouseAddressVO,
)
from src.modules.warehouses.domain.value_objects.warehouse_by_supplier_cache_value_vo import (
    WarehouseBySupplierCacheValueVO,
)
from src.modules.warehouses.domain.value_objects.warehouse_cache_item_vo import (
    WarehouseCacheItemVO,
)
from src.modules.warehouses.domain.value_objects.warehouse_name_vo import (
    WarehouseNameVO,
)


def _make_entity(faker: Faker, supplier_id: UUID | None = None) -> WarehouseEntity:
    """Build a WarehouseEntity with valid VOs."""
    return WarehouseEntity.create(
        supplier_id=supplier_id or UUID(faker.uuid4()),
        name=WarehouseNameVO(faker.company()),
        address=WarehouseAddressVO(faker.address()),
    )


def _make_cache_item(faker: Faker) -> WarehouseCacheItemVO:
    """Build a standalone WarehouseCacheItemVO with valid data."""
    now = datetime.now(UTC)
    return WarehouseCacheItemVO(
        id=UUID(faker.uuid4()),
        supplier_id=UUID(faker.uuid4()),
        name=WarehouseNameVO(faker.company()),
        address=WarehouseAddressVO(faker.address()),
        is_active=True,
        created_at=now,
        updated_at=now,
    )


class TestWarehouseBySupplierCacheValueVO:
    def test_should_create_cache_value_vo_with_empty_warehouse_list(self) -> None:
        """WarehouseBySupplierCacheValueVO must accept an empty list."""
        vo = WarehouseBySupplierCacheValueVO(warehouses=[])

        assert vo.warehouses == []

    def test_should_create_cache_value_vo_with_multiple_items(
        self, faker: Faker
    ) -> None:
        """WarehouseBySupplierCacheValueVO must store all provided cache items."""
        items = [_make_cache_item(faker) for _ in range(3)]

        vo = WarehouseBySupplierCacheValueVO(warehouses=items)

        assert len(vo.warehouses) == 3
        assert vo.warehouses == items

    def test_should_raise_exception_when_attempting_to_replace_warehouses_list(
        self, faker: Faker
    ) -> None:
        """The warehouses attribute must be frozen — reassignment must raise FrozenInstanceError."""
        vo = WarehouseBySupplierCacheValueVO(warehouses=[_make_cache_item(faker)])

        with pytest.raises(FrozenInstanceError):
            vo.warehouses = []  # type: ignore[misc]

    def test_should_return_empty_warehouses_when_entity_list_is_empty(self) -> None:
        """from_warehouses on an empty list must produce an empty warehouses list."""
        vo = WarehouseBySupplierCacheValueVO.from_warehouses([])

        assert vo.warehouses == []

    def test_should_return_correct_number_of_cache_items_from_entities(
        self, faker: Faker
    ) -> None:
        """from_warehouses must produce one WarehouseCacheItemVO per WarehouseEntity."""
        entities = [_make_entity(faker) for _ in range(4)]

        vo = WarehouseBySupplierCacheValueVO.from_warehouses(entities)

        assert len(vo.warehouses) == 4

    def test_should_map_entity_fields_correctly_to_cache_item(
        self, faker: Faker
    ) -> None:
        """Each WarehouseCacheItemVO must mirror the corresponding entity's fields exactly."""
        entity = _make_entity(faker)

        vo = WarehouseBySupplierCacheValueVO.from_warehouses([entity])

        item = vo.warehouses[0]
        assert item.id == entity.id
        assert item.supplier_id == entity.supplier_id
        assert item.name == entity.name
        assert item.address == entity.address
        assert item.is_active == entity.is_active
        assert item.created_at == entity.created_at
        assert item.updated_at == entity.updated_at

    def test_should_return_warehouse_cache_item_vo_instances(
        self, faker: Faker
    ) -> None:
        """Every item produced by from_warehouses must be a WarehouseCacheItemVO."""
        entities = [_make_entity(faker) for _ in range(2)]

        vo = WarehouseBySupplierCacheValueVO.from_warehouses(entities)

        for item in vo.warehouses:
            assert isinstance(item, WarehouseCacheItemVO)

    def test_should_preserve_entity_order_in_warehouses_list(
        self, faker: Faker
    ) -> None:
        """from_warehouses must preserve the order of the input entities."""
        supplier_id = UUID(faker.uuid4())
        entities = [_make_entity(faker, supplier_id) for _ in range(3)]

        vo = WarehouseBySupplierCacheValueVO.from_warehouses(entities)

        for entity, item in zip(entities, vo.warehouses, strict=True):
            assert item.id == entity.id

    def test_should_return_warehouse_by_supplier_cache_value_vo_instance(
        self, faker: Faker
    ) -> None:
        """from_warehouses must return a WarehouseBySupplierCacheValueVO instance."""
        vo = WarehouseBySupplierCacheValueVO.from_warehouses([_make_entity(faker)])

        assert isinstance(vo, WarehouseBySupplierCacheValueVO)

    def test_should_return_dict_with_warehouses_key(self, faker: Faker) -> None:
        """to_dict must return a dict containing a 'warehouses' key."""
        vo = WarehouseBySupplierCacheValueVO.from_warehouses([_make_entity(faker)])

        result = vo.to_dict()

        assert "warehouses" in result

    def test_should_serialize_correct_number_of_warehouse_entries(
        self, faker: Faker
    ) -> None:
        """to_dict must include one entry per warehouse in the list."""
        entities = [_make_entity(faker) for _ in range(3)]
        vo = WarehouseBySupplierCacheValueVO.from_warehouses(entities)

        result = vo.to_dict()

        assert len(result["warehouses"]) == 3

    def test_should_serialize_empty_list_when_no_warehouses(self) -> None:
        """to_dict on an empty VO must return {'warehouses': []}."""
        vo = WarehouseBySupplierCacheValueVO(warehouses=[])

        result = vo.to_dict()

        assert result == {"warehouses": []}

    def test_should_serialize_all_expected_fields_per_warehouse(
        self, faker: Faker
    ) -> None:
        """Each serialized warehouse dict must contain all required fields."""
        vo = WarehouseBySupplierCacheValueVO.from_warehouses([_make_entity(faker)])

        entry = vo.to_dict()["warehouses"][0]

        assert set(entry.keys()) == {
            "id",
            "supplier_id",
            "name",
            "address",
            "is_active",
            "created_at",
            "updated_at",
        }

    def test_should_serialize_id_and_supplier_id_as_strings(self, faker: Faker) -> None:
        """Id and supplier_id must be serialized as UUID strings, not UUID objects."""
        entity = _make_entity(faker)
        vo = WarehouseBySupplierCacheValueVO.from_warehouses([entity])

        entry = vo.to_dict()["warehouses"][0]

        assert isinstance(entry["id"], str)
        assert isinstance(entry["supplier_id"], str)
        assert entry["id"] == str(entity.id)
        assert entry["supplier_id"] == str(entity.supplier_id)

    def test_should_serialize_name_and_address_as_strings(self, faker: Faker) -> None:
        """Name and address must be serialized as plain strings, not VO objects."""
        entity = _make_entity(faker)
        vo = WarehouseBySupplierCacheValueVO.from_warehouses([entity])

        entry = vo.to_dict()["warehouses"][0]

        assert isinstance(entry["name"], str)
        assert isinstance(entry["address"], str)
        assert entry["name"] == str(entity.name)
        assert entry["address"] == str(entity.address)

    def test_should_serialize_created_at_and_updated_at_as_iso_strings(
        self, faker: Faker
    ) -> None:
        """created_at and updated_at must be serialized as ISO 8601 strings."""
        entity = _make_entity(faker)
        vo = WarehouseBySupplierCacheValueVO.from_warehouses([entity])

        entry = vo.to_dict()["warehouses"][0]

        assert isinstance(entry["created_at"], str)
        assert isinstance(entry["updated_at"], str)
        assert entry["created_at"] == entity.created_at.isoformat()
        assert entry["updated_at"] == entity.updated_at.isoformat()

    def test_should_serialize_is_active_as_boolean(self, faker: Faker) -> None:
        """is_active must be serialized as a Python bool."""
        entity = _make_entity(faker)
        vo = WarehouseBySupplierCacheValueVO.from_warehouses([entity])

        entry = vo.to_dict()["warehouses"][0]

        assert isinstance(entry["is_active"], bool)
        assert entry["is_active"] == entity.is_active

    def test_should_produce_correct_field_values_for_every_entity(
        self, faker: Faker
    ) -> None:
        """Each serialized entry must match its corresponding source entity exactly."""
        entities = [_make_entity(faker) for _ in range(3)]
        vo = WarehouseBySupplierCacheValueVO.from_warehouses(entities)

        entries = vo.to_dict()["warehouses"]

        for entity, entry in zip(entities, entries, strict=True):
            assert entry["id"] == str(entity.id)
            assert entry["supplier_id"] == str(entity.supplier_id)
            assert entry["name"] == str(entity.name)
            assert entry["address"] == str(entity.address)
            assert entry["is_active"] == entity.is_active
            assert entry["created_at"] == entity.created_at.isoformat()
            assert entry["updated_at"] == entity.updated_at.isoformat()

    def test_should_be_equal_when_warehouses_lists_are_identical(
        self, faker: Faker
    ) -> None:
        """Two VOs with the same list of items must be equal."""
        entities = [_make_entity(faker) for _ in range(2)]

        vo_a = WarehouseBySupplierCacheValueVO.from_warehouses(entities)
        vo_b = WarehouseBySupplierCacheValueVO.from_warehouses(entities)

        assert vo_a == vo_b

    def test_should_not_be_equal_when_warehouses_lists_differ(
        self, faker: Faker
    ) -> None:
        """Two VOs built from different entity lists must not be equal."""
        vo_a = WarehouseBySupplierCacheValueVO.from_warehouses([_make_entity(faker)])
        vo_b = WarehouseBySupplierCacheValueVO.from_warehouses([_make_entity(faker)])

        assert vo_a != vo_b
