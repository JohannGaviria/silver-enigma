from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from src.modules.warehouses.domain.exceptions.warehouse_referenced_order_exception import (
    InvalidWarehouseReferencedOrderException,
)
from src.modules.warehouses.domain.value_objects.warehouse_referenced_order_vo import (
    WarehouseReferencedOrderVO,
)
from src.shared.domain.enums.order_status_enum import OrderStatusEnum


class TestWarehouseReferencedOrderVO:
    def test_should_create_referenced_order_vo_when_values_are_valid(self) -> None:
        """Test that the WarehouseReferencedOrderVO is created successfully.

        when all values are valid.
        """
        order_id = uuid4()
        warehouse_id = uuid4()
        order_status = OrderStatusEnum.DRAFT

        referenced_order_vo = WarehouseReferencedOrderVO(
            order_id=order_id,
            warehouse_id=warehouse_id,
            order_status=order_status,
        )

        assert referenced_order_vo.order_id == order_id
        assert referenced_order_vo.warehouse_id == warehouse_id
        assert referenced_order_vo.order_status == order_status

    def test_should_raise_exception_when_order_id_is_none(self) -> None:
        """Test that the WarehouseReferencedOrderVO raises an exception.

        when order_id is None.
        """
        with pytest.raises(
            InvalidWarehouseReferencedOrderException,
            match="Invalid warehouse referenced order.",
        ):
            WarehouseReferencedOrderVO(
                order_id=None,  # type: ignore[arg-type]
                warehouse_id=uuid4(),
                order_status=OrderStatusEnum.DRAFT,
            )

    def test_should_raise_exception_when_warehouse_id_is_none(self) -> None:
        """Test that the WarehouseReferencedOrderVO raises an exception.

        when warehouse_id is None.
        """
        with pytest.raises(
            InvalidWarehouseReferencedOrderException,
            match="Invalid warehouse referenced order.",
        ):
            WarehouseReferencedOrderVO(
                order_id=uuid4(),
                warehouse_id=None,  # type: ignore[arg-type]
                order_status=OrderStatusEnum.DRAFT,
            )

    def test_should_raise_exception_when_order_status_is_none(self) -> None:
        """Test that the WarehouseReferencedOrderVO raises an exception.

        when order_status is None.
        """
        with pytest.raises(
            InvalidWarehouseReferencedOrderException,
            match="Invalid warehouse referenced order.",
        ):
            WarehouseReferencedOrderVO(
                order_id=uuid4(),
                warehouse_id=uuid4(),
                order_status=None,  # type: ignore[arg-type]
            )

    def test_should_raise_exception_when_attempting_to_modify_attributes(
        self,
    ) -> None:
        """Test that the WarehouseReferencedOrderVO raises a FrozenInstanceError.

        when attempting to modify an attribute after creation.
        """
        referenced_order_vo = WarehouseReferencedOrderVO(
            order_id=uuid4(),
            warehouse_id=uuid4(),
            order_status=OrderStatusEnum.DRAFT,
        )

        with pytest.raises(FrozenInstanceError):
            referenced_order_vo.order_id = uuid4()  # type: ignore[misc]

    def test_should_return_equal_vos_when_values_are_identical(self) -> None:
        """Test that two WarehouseReferencedOrderVO instances with the same values.

        are considered equal.
        """
        order_id = uuid4()
        warehouse_id = uuid4()

        assert WarehouseReferencedOrderVO(
            order_id=order_id,
            warehouse_id=warehouse_id,
            order_status=OrderStatusEnum.DRAFT,
        ) == WarehouseReferencedOrderVO(
            order_id=order_id,
            warehouse_id=warehouse_id,
            order_status=OrderStatusEnum.DRAFT,
        )

    def test_should_return_different_vos_when_values_differ(self) -> None:
        """Test that two WarehouseReferencedOrderVO instances with different values.

        are not considered equal.
        """
        assert WarehouseReferencedOrderVO(
            order_id=uuid4(),
            warehouse_id=uuid4(),
            order_status=OrderStatusEnum.DRAFT,
        ) != WarehouseReferencedOrderVO(
            order_id=uuid4(),
            warehouse_id=uuid4(),
            order_status=OrderStatusEnum.CONFIRMED,
        )
