from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from src.modules.products.domain.exceptions.product_referenced_order_exception import (
    InvalidProductReferencedOrderException,
)
from src.modules.products.domain.value_objects.product_referenced_order_vo import (
    ProductReferencedOrderVO,
)
from src.shared.domain.enums.order_status_enum import OrderStatusEnum


class TestProductReferencedOrderVO:
    def test_should_create_referenced_order_vo_when_values_are_valid(self) -> None:
        """Test that the ProductReferencedOrderVO is created successfully.

        when all values are valid.
        """
        order_id = uuid4()
        product_id = uuid4()
        order_status = OrderStatusEnum.DRAFT

        referenced_order_vo = ProductReferencedOrderVO(
            order_id=order_id,
            product_id=product_id,
            order_status=order_status,
        )

        assert referenced_order_vo.order_id == order_id
        assert referenced_order_vo.product_id == product_id
        assert referenced_order_vo.order_status == order_status

    def test_should_raise_exception_when_order_id_is_none(self) -> None:
        """Test that the ProductReferencedOrderVO raises an exception.

        when order_id is None.
        """
        with pytest.raises(
            InvalidProductReferencedOrderException,
            match="Invalid product referenced order.",
        ):
            ProductReferencedOrderVO(
                order_id=None,  # type: ignore[arg-type]
                product_id=uuid4(),
                order_status=OrderStatusEnum.DRAFT,
            )

    def test_should_raise_exception_when_product_id_is_none(self) -> None:
        """Test that the ProductReferencedOrderVO raises an exception.

        when product_id is None.
        """
        with pytest.raises(
            InvalidProductReferencedOrderException,
            match="Invalid product referenced order.",
        ):
            ProductReferencedOrderVO(
                order_id=uuid4(),
                product_id=None,  # type: ignore[arg-type]
                order_status=OrderStatusEnum.DRAFT,
            )

    def test_should_raise_exception_when_order_status_is_none(self) -> None:
        """Test that the ProductReferencedOrderVO raises an exception.

        when order_status is None.
        """
        with pytest.raises(
            InvalidProductReferencedOrderException,
            match="Invalid product referenced order.",
        ):
            ProductReferencedOrderVO(
                order_id=uuid4(),
                product_id=uuid4(),
                order_status=None,  # type: ignore[arg-type]
            )

    def test_should_raise_exception_when_attempting_to_modify_attributes(
        self,
    ) -> None:
        """Test that the ProductReferencedOrderVO raises a FrozenInstanceError.

        when attempting to modify an attribute after creation.
        """
        referenced_order_vo = ProductReferencedOrderVO(
            order_id=uuid4(),
            product_id=uuid4(),
            order_status=OrderStatusEnum.DRAFT,
        )

        with pytest.raises(FrozenInstanceError):
            referenced_order_vo.order_id = uuid4()  # type: ignore[misc]

    def test_should_return_equal_vos_when_values_are_identical(self) -> None:
        """Test that two ProductReferencedOrderVO instances with the same values.

        are considered equal.
        """
        order_id = uuid4()
        product_id = uuid4()

        assert ProductReferencedOrderVO(
            order_id=order_id,
            product_id=product_id,
            order_status=OrderStatusEnum.DRAFT,
        ) == ProductReferencedOrderVO(
            order_id=order_id,
            product_id=product_id,
            order_status=OrderStatusEnum.DRAFT,
        )

    def test_should_return_different_vos_when_values_differ(self) -> None:
        """Test that two ProductReferencedOrderVO instances with different values.

        are not considered equal.
        """
        assert ProductReferencedOrderVO(
            order_id=uuid4(),
            product_id=uuid4(),
            order_status=OrderStatusEnum.DRAFT,
        ) != ProductReferencedOrderVO(
            order_id=uuid4(),
            product_id=uuid4(),
            order_status=OrderStatusEnum.CONFIRMED,
        )
