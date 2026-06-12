from dataclasses import FrozenInstanceError

import pytest

from src.modules.products.domain.exceptions.stock_exception import (
    InvalidTotalStockException,
)
from src.modules.products.domain.value_objects.total_stock_vo import (
    TotalStockVO,
)


class TestTotalStockVO:
    # ---------------------------------------------------------------------------
    # creation
    # ---------------------------------------------------------------------------

    def test_should_create_total_stock_vo_when_stock_is_zero(self) -> None:
        """Test that the TotalStockVO can be created successfully when stock is zero."""
        total_stock = TotalStockVO(0)

        assert total_stock.total_stock == 0

    def test_should_create_total_stock_vo_when_stock_is_positive(self) -> None:
        """Test that the TotalStockVO can be created successfully when stock is positive."""
        total_stock = TotalStockVO(100)

        assert total_stock.total_stock == 100

    # ---------------------------------------------------------------------------
    # validation
    # ---------------------------------------------------------------------------

    def test_should_raise_exception_when_stock_is_none(self) -> None:
        """Test that the TotalStockVO raises InvalidTotalStockException when stock is None."""
        with pytest.raises(InvalidTotalStockException) as exc_info:
            TotalStockVO(None)  # type: ignore[arg-type]

        assert "Total stock cannot be empty." in exc_info.value.errors

    def test_should_raise_exception_when_stock_is_negative(self) -> None:
        """Test that the TotalStockVO raises InvalidTotalStockException when stock is negative."""
        with pytest.raises(InvalidTotalStockException) as exc_info:
            TotalStockVO(-1)

        assert "Total stock cannot be negative." in exc_info.value.errors

    # ---------------------------------------------------------------------------
    # value
    # ---------------------------------------------------------------------------

    def test_should_return_stock_value(self) -> None:
        """Test that value() returns the underlying stock value."""
        total_stock = TotalStockVO(50)

        assert total_stock.value() == 50

    # ---------------------------------------------------------------------------
    # immutability
    # ---------------------------------------------------------------------------

    def test_should_raise_exception_when_attempting_to_modify_stock(
        self,
    ) -> None:
        """Test that the TotalStockVO raises FrozenInstanceError when attempting to modify stock."""
        total_stock = TotalStockVO(100)

        with pytest.raises(FrozenInstanceError):
            total_stock.total_stock = 200  # type: ignore[misc]

    # ---------------------------------------------------------------------------
    # equality
    # ---------------------------------------------------------------------------

    def test_should_return_equal_total_stock_vos_when_values_are_identical(
        self,
    ) -> None:
        """Test that two TotalStockVO instances with identical values are considered equal."""
        total_stock_1 = TotalStockVO(100)
        total_stock_2 = TotalStockVO(100)

        assert total_stock_1 == total_stock_2

    def test_should_return_different_total_stock_vos_when_values_differ(
        self,
    ) -> None:
        """Test that two TotalStockVO instances with different values are not considered equal."""
        assert TotalStockVO(100) != TotalStockVO(200)
