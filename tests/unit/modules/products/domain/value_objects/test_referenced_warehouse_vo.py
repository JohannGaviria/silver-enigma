from dataclasses import FrozenInstanceError
from uuid import UUID

import pytest
from faker import Faker

from src.modules.products.domain.exceptions.inventory_warehouse_exception import (
    InvalidReferencedWarehouseException,
)
from src.modules.products.domain.value_objects.referenced_warehouse_vo import (
    ReferencedWarehouseVO,
)


class TestReferencedWarehouseVO:
    # ---------------------------------------------------------------------------
    # creation
    # ---------------------------------------------------------------------------

    def test_should_create_referenced_warehouse_vo_when_valid_data_is_provided(
        self,
        faker: Faker,
    ) -> None:
        """Test that the ReferencedWarehouseVO can be created successfully when valid data is provided."""
        warehouse_id = UUID(faker.uuid4())
        supplier_id = UUID(faker.uuid4())

        referenced_warehouse = ReferencedWarehouseVO(
            warehouse_id=warehouse_id,
            supplier_id=supplier_id,
            is_active=True,
        )

        assert referenced_warehouse.warehouse_id == warehouse_id
        assert referenced_warehouse.supplier_id == supplier_id
        assert referenced_warehouse.is_active is True

    # ---------------------------------------------------------------------------
    # validation
    # ---------------------------------------------------------------------------

    def test_should_raise_exception_when_warehouse_id_is_none(self) -> None:
        """Test that the ReferencedWarehouseVO raises an exception when warehouse_id is None."""
        with pytest.raises(InvalidReferencedWarehouseException) as exc_info:
            ReferencedWarehouseVO(
                warehouse_id=None,  # type: ignore[arg-type]
                supplier_id=UUID("11111111-1111-1111-1111-111111111111"),
                is_active=True,
            )

        assert "Warehouse ID cannot be None." in exc_info.value.errors

    def test_should_raise_exception_when_supplier_id_is_none(self) -> None:
        """Test that the ReferencedWarehouseVO raises an exception when supplier_id is None."""
        with pytest.raises(InvalidReferencedWarehouseException) as exc_info:
            ReferencedWarehouseVO(
                warehouse_id=UUID("11111111-1111-1111-1111-111111111111"),
                supplier_id=None,  # type: ignore[arg-type]
                is_active=True,
            )

        assert "Supplier ID cannot be None." in exc_info.value.errors

    def test_should_raise_exception_when_is_active_is_none(self) -> None:
        """Test that the ReferencedWarehouseVO raises an exception when is_active is None."""
        with pytest.raises(InvalidReferencedWarehouseException) as exc_info:
            ReferencedWarehouseVO(
                warehouse_id=UUID("11111111-1111-1111-1111-111111111111"),
                supplier_id=UUID("22222222-2222-2222-2222-222222222222"),
                is_active=None,  # type: ignore[arg-type]
            )

        assert "Is active cannot be None." in exc_info.value.errors

    # ---------------------------------------------------------------------------
    # immutability
    # ---------------------------------------------------------------------------

    def test_should_raise_exception_when_attempting_to_modify_warehouse_id(
        self,
        faker: Faker,
    ) -> None:
        """Test that the ReferencedWarehouseVO raises a FrozenInstanceError when attempting to modify warehouse_id."""
        referenced_warehouse = ReferencedWarehouseVO(
            warehouse_id=UUID(faker.uuid4()),
            supplier_id=UUID(faker.uuid4()),
            is_active=True,
        )

        with pytest.raises(FrozenInstanceError):
            referenced_warehouse.warehouse_id = UUID(faker.uuid4())  # type: ignore[misc]

    # ---------------------------------------------------------------------------
    # equality
    # ---------------------------------------------------------------------------

    def test_should_return_equal_referenced_warehouse_vos_when_data_is_identical(
        self,
        faker: Faker,
    ) -> None:
        """Test that two ReferencedWarehouseVO instances with identical data are considered equal."""
        warehouse_id = UUID(faker.uuid4())
        supplier_id = UUID(faker.uuid4())

        vo1 = ReferencedWarehouseVO(
            warehouse_id=warehouse_id,
            supplier_id=supplier_id,
            is_active=True,
        )

        vo2 = ReferencedWarehouseVO(
            warehouse_id=warehouse_id,
            supplier_id=supplier_id,
            is_active=True,
        )

        assert vo1 == vo2

    def test_should_return_different_referenced_warehouse_vos_when_data_differs(
        self,
        faker: Faker,
    ) -> None:
        """Test that two ReferencedWarehouseVO instances with different data are not considered equal."""
        supplier_id = UUID(faker.uuid4())

        vo1 = ReferencedWarehouseVO(
            warehouse_id=UUID(faker.uuid4()),
            supplier_id=supplier_id,
            is_active=True,
        )

        vo2 = ReferencedWarehouseVO(
            warehouse_id=UUID(faker.uuid4()),
            supplier_id=supplier_id,
            is_active=True,
        )

        assert vo1 != vo2
