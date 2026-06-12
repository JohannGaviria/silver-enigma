from dataclasses import FrozenInstanceError
from decimal import Decimal
from uuid import UUID

import pytest

from src.modules.products.domain.enums.unit_of_measure_enum import (
    UnitOfMeasureEnum,
)
from src.modules.products.domain.exceptions.pagination_exception import (
    InvalidPaginationElementsException,
)
from src.modules.products.domain.value_objects.product_stock_item_vo import (
    ProductStockItemVO,
)
from src.modules.products.domain.value_objects.product_stock_vo import (
    ProductStockVO,
)
from src.modules.products.domain.value_objects.reserved_stock_vo import (
    ReservedStockVO,
)
from src.modules.products.domain.value_objects.total_stock_vo import (
    TotalStockVO,
)


class TestProductStockVO:
    # ---------------------------------------------------------------------------
    # helpers
    # ---------------------------------------------------------------------------

    @staticmethod
    def _build_item() -> ProductStockItemVO:
        """Build a valid ProductStockItemVO."""
        return ProductStockItemVO(
            product_id=UUID("11111111-1111-1111-1111-111111111111"),
            name="Premium Rice",
            description="High quality rice",
            unit_of_measure=UnitOfMeasureEnum.KG,
            unit_price=Decimal("15.50"),
            total_stock=TotalStockVO(100),
            reserved_stock=ReservedStockVO(80),
        )

    # ---------------------------------------------------------------------------
    # creation
    # ---------------------------------------------------------------------------

    def test_should_create_product_stock_vo_when_valid_data_is_provided(
        self,
    ) -> None:
        """Test that a ProductStockVO can be created successfully."""
        item = self._build_item()

        product_stock = ProductStockVO(
            products_stock=[item],
            page=0,
            page_size=10,
            elements=1,
        )

        assert product_stock.products_stock == [item]
        assert product_stock.page == 0
        assert product_stock.page_size == 10
        assert product_stock.elements == 1

    # ---------------------------------------------------------------------------
    # validation
    # ---------------------------------------------------------------------------

    def test_should_raise_exception_when_page_is_negative(
        self,
    ) -> None:
        """Test that an exception is raised when page is negative."""
        with pytest.raises(InvalidPaginationElementsException) as exc_info:
            ProductStockVO(
                products_stock=[],
                page=-1,
                page_size=10,
                elements=0,
            )

        assert "Page must be greater than or equal to 0." in exc_info.value.errors

    def test_should_raise_exception_when_page_size_is_negative(
        self,
    ) -> None:
        """Test that an exception is raised when page_size is negative."""
        with pytest.raises(InvalidPaginationElementsException) as exc_info:
            ProductStockVO(
                products_stock=[],
                page=0,
                page_size=-1,
                elements=0,
            )

        assert "Page size must be greater than or equal to 0." in exc_info.value.errors

    def test_should_raise_exception_when_elements_is_negative(
        self,
    ) -> None:
        """Test that an exception is raised when elements is negative."""
        with pytest.raises(InvalidPaginationElementsException) as exc_info:
            ProductStockVO(
                products_stock=[],
                page=0,
                page_size=10,
                elements=-1,
            )

        assert "Elements must be greater than or equal to 0." in exc_info.value.errors

    def test_should_raise_exception_with_multiple_errors_when_multiple_values_are_invalid(
        self,
    ) -> None:
        """Test that all validation errors are returned when multiple values are invalid."""
        with pytest.raises(InvalidPaginationElementsException) as exc_info:
            ProductStockVO(
                products_stock=[],
                page=-1,
                page_size=-10,
                elements=-100,
            )

        assert "Page must be greater than or equal to 0." in exc_info.value.errors
        assert "Page size must be greater than or equal to 0." in exc_info.value.errors
        assert "Elements must be greater than or equal to 0." in exc_info.value.errors

    # ---------------------------------------------------------------------------
    # immutability
    # ---------------------------------------------------------------------------

    def test_should_raise_exception_when_attempting_to_modify_page(
        self,
    ) -> None:
        """Test that the ProductStockVO is immutable."""
        product_stock = ProductStockVO(
            products_stock=[],
            page=0,
            page_size=10,
            elements=0,
        )

        with pytest.raises(FrozenInstanceError):
            product_stock.page = 1  # type: ignore[misc]

    # ---------------------------------------------------------------------------
    # equality
    # ---------------------------------------------------------------------------

    def test_should_return_equal_product_stock_vos_when_data_is_identical(
        self,
    ) -> None:
        """Test that two ProductStockVO instances with identical data are equal."""
        item = self._build_item()

        vo1 = ProductStockVO(
            products_stock=[item],
            page=0,
            page_size=10,
            elements=1,
        )

        vo2 = ProductStockVO(
            products_stock=[item],
            page=0,
            page_size=10,
            elements=1,
        )

        assert vo1 == vo2

    def test_should_return_different_product_stock_vos_when_data_differs(
        self,
    ) -> None:
        """Test that two ProductStockVO instances with different data are not equal."""
        item = self._build_item()

        vo1 = ProductStockVO(
            products_stock=[item],
            page=0,
            page_size=10,
            elements=1,
        )

        vo2 = ProductStockVO(
            products_stock=[item],
            page=1,
            page_size=10,
            elements=1,
        )

        assert vo1 != vo2
