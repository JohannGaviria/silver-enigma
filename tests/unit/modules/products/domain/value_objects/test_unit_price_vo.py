from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from src.modules.products.domain.exceptions.product_exception import (
    InvalidUnitPriceException,
)
from src.modules.products.domain.value_objects.unit_price_vo import UnitPriceVO


class TestUnitPriceVO:
    # ---------------------------------------------------------------------------
    # creation
    # ---------------------------------------------------------------------------

    def test_should_create_unit_price_vo_when_price_is_zero(self) -> None:
        """Test that the UnitPriceVO can be created successfully when the price is zero."""
        unit_price = UnitPriceVO(Decimal("0"))

        assert unit_price.price == Decimal("0")

    def test_should_create_unit_price_vo_when_price_is_positive(self) -> None:
        """Test that the UnitPriceVO can be created successfully when the price is positive."""
        unit_price = UnitPriceVO(Decimal("12500.50"))

        assert unit_price.price == Decimal("12500.50")

    # ---------------------------------------------------------------------------
    # validation
    # ---------------------------------------------------------------------------

    def test_should_raise_exception_when_price_is_none(self) -> None:
        """Test that the UnitPriceVO raises a InvalidUnitPriceException when the price is None."""
        with pytest.raises(InvalidUnitPriceException) as exc_info:
            UnitPriceVO(None)  # type: ignore[arg-type]

        assert "Price cannot be empty." in exc_info.value.errors

    def test_should_raise_exception_when_price_is_negative(self) -> None:
        """Test that the UnitPriceVO raises a InvalidUnitPriceException when the price is negative."""
        with pytest.raises(InvalidUnitPriceException) as exc_info:
            UnitPriceVO(Decimal("-1"))

        assert "Price cannot be negative." in exc_info.value.errors

    # ---------------------------------------------------------------------------
    # immutability
    # ---------------------------------------------------------------------------

    def test_should_raise_exception_when_attempting_to_modify_price(
        self,
    ) -> None:
        """Test that the UnitPriceVO raises a FrozenInstanceError when attempting to modify the price."""
        unit_price = UnitPriceVO(Decimal("100"))

        with pytest.raises(FrozenInstanceError):
            unit_price.price = Decimal("200")  # type: ignore[misc]

    # ---------------------------------------------------------------------------
    # equality
    # ---------------------------------------------------------------------------

    def test_should_return_equal_unit_price_vos_when_prices_are_identical(
        self,
    ) -> None:
        """Test that two UnitPriceVO instances with identical prices are considered equal."""
        price = Decimal("100.50")

        unit_price_1 = UnitPriceVO(price)
        unit_price_2 = UnitPriceVO(price)

        assert unit_price_1 == unit_price_2
