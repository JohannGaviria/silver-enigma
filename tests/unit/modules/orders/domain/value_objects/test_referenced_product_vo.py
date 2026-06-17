from dataclasses import FrozenInstanceError
from decimal import Decimal
from uuid import uuid4

import pytest

from src.modules.orders.domain.exceptions.order_exception import (
    InvalidReferencedProductException,
)
from src.modules.orders.domain.value_objects.quantity_vo import QuantityVO
from src.modules.orders.domain.value_objects.referenced_product_vo import (
    ReferencedProductVO,
)


class TestReferencedProductVO:
    # ---------------------------------------------------------------------------
    # creation
    # ---------------------------------------------------------------------------

    def test_should_create_referenced_product_vo_when_values_are_valid(self) -> None:
        """Test that ReferencedProductVO is created successfully when all values are valid."""
        product_id = uuid4()
        supplier_id = uuid4()
        name = "Premium Rice"
        quantity = QuantityVO(10)
        unit_price = Decimal("99.99")
        is_active = True

        referenced_product = ReferencedProductVO(
            product_id=product_id,
            supplier_id=supplier_id,
            name=name,
            quantity=quantity,
            unit_price=unit_price,
            is_active=is_active,
        )

        assert referenced_product.product_id == product_id
        assert referenced_product.supplier_id == supplier_id
        assert referenced_product.name == name
        assert referenced_product.quantity == quantity
        assert referenced_product.quantity.value() == 10
        assert referenced_product.unit_price == unit_price
        assert referenced_product.is_active is True

    def test_should_create_referenced_product_vo_when_is_active_is_false(self) -> None:
        """Test that ReferencedProductVO can be created with is_active=False."""
        referenced_product = ReferencedProductVO(
            product_id=uuid4(),
            supplier_id=uuid4(),
            name="Test Product",
            quantity=QuantityVO(5),
            unit_price=Decimal("50.00"),
            is_active=False,
        )

        assert referenced_product.is_active is False

    def test_should_create_referenced_product_vo_with_decimal_unit_price(self) -> None:
        """Test that ReferencedProductVO can be created with decimal unit price."""
        unit_price = Decimal("123.45")
        referenced_product = ReferencedProductVO(
            product_id=uuid4(),
            supplier_id=uuid4(),
            name="Test Product",
            quantity=QuantityVO(5),
            unit_price=unit_price,
            is_active=True,
        )

        assert referenced_product.unit_price == unit_price
        assert isinstance(referenced_product.unit_price, Decimal)

    # ---------------------------------------------------------------------------
    # validation
    # ---------------------------------------------------------------------------

    def test_should_raise_exception_when_product_id_is_none(self) -> None:
        """Test that ReferencedProductVO raises InvalidReferencedProductException when product_id is None."""
        with pytest.raises(InvalidReferencedProductException) as exc_info:
            ReferencedProductVO(
                product_id=None,  # type: ignore[arg-type]
                supplier_id=uuid4(),
                name="Test Product",
                quantity=QuantityVO(5),
                unit_price=Decimal("50.00"),
                is_active=True,
            )

        assert "Product ID cannot be None." in exc_info.value.errors

    def test_should_raise_exception_when_supplier_id_is_none(self) -> None:
        """Test that ReferencedProductVO raises InvalidReferencedProductException when supplier_id is None."""
        with pytest.raises(InvalidReferencedProductException) as exc_info:
            ReferencedProductVO(
                product_id=uuid4(),
                supplier_id=None,  # type: ignore[arg-type]
                name="Test Product",
                quantity=QuantityVO(5),
                unit_price=Decimal("50.00"),
                is_active=True,
            )

        assert "Supplier ID cannot be None." in exc_info.value.errors

    def test_should_raise_exception_when_name_is_none(self) -> None:
        """Test that ReferencedProductVO raises InvalidReferencedProductException when name is None."""
        with pytest.raises(InvalidReferencedProductException) as exc_info:
            ReferencedProductVO(
                product_id=uuid4(),
                supplier_id=uuid4(),
                name=None,  # type: ignore[arg-type]
                quantity=QuantityVO(5),
                unit_price=Decimal("50.00"),
                is_active=True,
            )

        assert "Name cannot be None." in exc_info.value.errors

    def test_should_raise_exception_when_quantity_is_none(self) -> None:
        """Test that ReferencedProductVO raises InvalidReferencedProductException when quantity is None."""
        with pytest.raises(InvalidReferencedProductException) as exc_info:
            ReferencedProductVO(
                product_id=uuid4(),
                supplier_id=uuid4(),
                name="Test Product",
                quantity=None,  # type: ignore[arg-type]
                unit_price=Decimal("50.00"),
                is_active=True,
            )

        assert "Quantity cannot be None." in exc_info.value.errors

    def test_should_raise_exception_when_unit_price_is_none(self) -> None:
        """Test that ReferencedProductVO raises InvalidReferencedProductException when unit_price is None."""
        with pytest.raises(InvalidReferencedProductException) as exc_info:
            ReferencedProductVO(
                product_id=uuid4(),
                supplier_id=uuid4(),
                name="Test Product",
                quantity=QuantityVO(5),
                unit_price=None,  # type: ignore[arg-type]
                is_active=True,
            )

        assert "Unit price cannot be None." in exc_info.value.errors

    def test_should_raise_exception_when_is_active_is_none(self) -> None:
        """Test that ReferencedProductVO raises InvalidReferencedProductException when is_active is None."""
        with pytest.raises(InvalidReferencedProductException) as exc_info:
            ReferencedProductVO(
                product_id=uuid4(),
                supplier_id=uuid4(),
                name="Test Product",
                quantity=QuantityVO(5),
                unit_price=Decimal("50.00"),
                is_active=None,  # type: ignore[arg-type]
            )

        assert "Is active cannot be None." in exc_info.value.errors

    def test_should_raise_exception_with_multiple_errors_when_multiple_fields_are_invalid(
        self,
    ) -> None:
        """Test that all validation errors are returned when multiple fields are invalid."""
        with pytest.raises(InvalidReferencedProductException) as exc_info:
            ReferencedProductVO(
                product_id=None,  # type: ignore[arg-type]
                supplier_id=None,  # type: ignore[arg-type]
                name=None,  # type: ignore[arg-type]
                quantity=None,  # type: ignore[arg-type]
                unit_price=None,  # type: ignore[arg-type]
                is_active=None,  # type: ignore[arg-type]
            )

        errors = exc_info.value.errors
        assert "Product ID cannot be None." in errors
        assert "Supplier ID cannot be None." in errors
        assert "Name cannot be None." in errors
        assert "Quantity cannot be None." in errors
        assert "Unit price cannot be None." in errors
        assert "Is active cannot be None." in errors

    # ---------------------------------------------------------------------------
    # immutability
    # ---------------------------------------------------------------------------

    def test_should_raise_exception_when_attempting_to_modify_product_id(self) -> None:
        """Test that ReferencedProductVO raises FrozenInstanceError when attempting to modify product_id."""
        referenced_product = ReferencedProductVO(
            product_id=uuid4(),
            supplier_id=uuid4(),
            name="Test Product",
            quantity=QuantityVO(5),
            unit_price=Decimal("50.00"),
            is_active=True,
        )

        with pytest.raises(FrozenInstanceError):
            referenced_product.product_id = uuid4()  # type: ignore[misc]

    def test_should_raise_exception_when_attempting_to_modify_supplier_id(self) -> None:
        """Test that ReferencedProductVO raises FrozenInstanceError when attempting to modify supplier_id."""
        referenced_product = ReferencedProductVO(
            product_id=uuid4(),
            supplier_id=uuid4(),
            name="Test Product",
            quantity=QuantityVO(5),
            unit_price=Decimal("50.00"),
            is_active=True,
        )

        with pytest.raises(FrozenInstanceError):
            referenced_product.supplier_id = uuid4()  # type: ignore[misc]

    def test_should_raise_exception_when_attempting_to_modify_name(self) -> None:
        """Test that ReferencedProductVO raises FrozenInstanceError when attempting to modify name."""
        referenced_product = ReferencedProductVO(
            product_id=uuid4(),
            supplier_id=uuid4(),
            name="Test Product",
            quantity=QuantityVO(5),
            unit_price=Decimal("50.00"),
            is_active=True,
        )

        with pytest.raises(FrozenInstanceError):
            referenced_product.name = "New Name"  # type: ignore[misc]

    def test_should_raise_exception_when_attempting_to_modify_quantity(self) -> None:
        """Test that ReferencedProductVO raises FrozenInstanceError when attempting to modify quantity."""
        referenced_product = ReferencedProductVO(
            product_id=uuid4(),
            supplier_id=uuid4(),
            name="Test Product",
            quantity=QuantityVO(5),
            unit_price=Decimal("50.00"),
            is_active=True,
        )

        with pytest.raises(FrozenInstanceError):
            referenced_product.quantity = QuantityVO(10)  # type: ignore[misc]

    def test_should_raise_exception_when_attempting_to_modify_unit_price(self) -> None:
        """Test that ReferencedProductVO raises FrozenInstanceError when attempting to modify unit_price."""
        referenced_product = ReferencedProductVO(
            product_id=uuid4(),
            supplier_id=uuid4(),
            name="Test Product",
            quantity=QuantityVO(5),
            unit_price=Decimal("50.00"),
            is_active=True,
        )

        with pytest.raises(FrozenInstanceError):
            referenced_product.unit_price = Decimal("75.00")  # type: ignore[misc]

    def test_should_raise_exception_when_attempting_to_modify_is_active(self) -> None:
        """Test that ReferencedProductVO raises FrozenInstanceError when attempting to modify is_active."""
        referenced_product = ReferencedProductVO(
            product_id=uuid4(),
            supplier_id=uuid4(),
            name="Test Product",
            quantity=QuantityVO(5),
            unit_price=Decimal("50.00"),
            is_active=True,
        )

        with pytest.raises(FrozenInstanceError):
            referenced_product.is_active = False  # type: ignore[misc]

    # ---------------------------------------------------------------------------
    # equality
    # ---------------------------------------------------------------------------

    def test_should_return_equal_referenced_product_vos_when_values_are_identical(
        self,
    ) -> None:
        """Test that two ReferencedProductVO instances with identical values are equal."""
        product_id = uuid4()
        supplier_id = uuid4()
        name = "Premium Rice"
        quantity = QuantityVO(10)
        unit_price = Decimal("99.99")
        is_active = True

        product_1 = ReferencedProductVO(
            product_id=product_id,
            supplier_id=supplier_id,
            name=name,
            quantity=quantity,
            unit_price=unit_price,
            is_active=is_active,
        )

        product_2 = ReferencedProductVO(
            product_id=product_id,
            supplier_id=supplier_id,
            name=name,
            quantity=quantity,
            unit_price=unit_price,
            is_active=is_active,
        )

        assert product_1 == product_2

    def test_should_return_different_referenced_product_vos_when_values_differ(
        self,
    ) -> None:
        """Test that two ReferencedProductVO instances with different values are not equal."""
        product_1 = ReferencedProductVO(
            product_id=uuid4(),
            supplier_id=uuid4(),
            name="Product A",
            quantity=QuantityVO(10),
            unit_price=Decimal("99.99"),
            is_active=True,
        )

        product_2 = ReferencedProductVO(
            product_id=uuid4(),
            supplier_id=uuid4(),
            name="Product B",
            quantity=QuantityVO(10),
            unit_price=Decimal("99.99"),
            is_active=True,
        )

        assert product_1 != product_2

    def test_should_return_different_referenced_product_vos_when_product_id_differs(
        self,
    ) -> None:
        """Test that two ReferencedProductVO instances with different product_id are not equal."""
        supplier_id = uuid4()
        name = "Product"
        quantity = QuantityVO(10)
        unit_price = Decimal("99.99")
        is_active = True

        product_1 = ReferencedProductVO(
            product_id=uuid4(),
            supplier_id=supplier_id,
            name=name,
            quantity=quantity,
            unit_price=unit_price,
            is_active=is_active,
        )

        product_2 = ReferencedProductVO(
            product_id=uuid4(),
            supplier_id=supplier_id,
            name=name,
            quantity=quantity,
            unit_price=unit_price,
            is_active=is_active,
        )

        assert product_1 != product_2

    # ---------------------------------------------------------------------------
    # hash
    # ---------------------------------------------------------------------------

    def test_should_be_hashable(self) -> None:
        """Test that ReferencedProductVO is hashable and can be used as a dictionary key."""
        referenced_product = ReferencedProductVO(
            product_id=uuid4(),
            supplier_id=uuid4(),
            name="Test Product",
            quantity=QuantityVO(5),
            unit_price=Decimal("50.00"),
            is_active=True,
        )

        dictionary = {referenced_product: "test_value"}

        assert dictionary[referenced_product] == "test_value"

    def test_should_have_same_hash_when_values_are_equal(self) -> None:
        """Test that two ReferencedProductVO instances with the same values have the same hash."""
        product_id = uuid4()
        supplier_id = uuid4()
        name = "Test Product"
        quantity = QuantityVO(5)
        unit_price = Decimal("50.00")
        is_active = True

        product_1 = ReferencedProductVO(
            product_id=product_id,
            supplier_id=supplier_id,
            name=name,
            quantity=quantity,
            unit_price=unit_price,
            is_active=is_active,
        )

        product_2 = ReferencedProductVO(
            product_id=product_id,
            supplier_id=supplier_id,
            name=name,
            quantity=quantity,
            unit_price=unit_price,
            is_active=is_active,
        )

        assert hash(product_1) == hash(product_2)
