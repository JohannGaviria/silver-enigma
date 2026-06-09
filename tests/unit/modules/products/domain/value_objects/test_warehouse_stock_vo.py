from dataclasses import FrozenInstanceError
from datetime import datetime
from uuid import UUID

import pytest

from src.modules.products.domain.exceptions.pagination_exception import (
    InvalidPaginationElementsException,
)
from src.modules.products.domain.value_objects.available_stock_vo import (
    AvailableStockVO,
)
from src.modules.products.domain.value_objects.product_name_vo import ProductNameVO
from src.modules.products.domain.value_objects.total_stock_vo import TotalStockVO
from src.modules.products.domain.value_objects.warehouse_stock_item_vo import (
    WarehouseStockItemVO,
)
from src.modules.products.domain.value_objects.warehouse_stock_vo import (
    WarehouseStockVO,
)


class TestWarehouseStockVO:
    # ---------------------------------------------------------------------------
    # helpers
    # ---------------------------------------------------------------------------

    @staticmethod
    def _build_item() -> WarehouseStockItemVO:
        """Build a valid WarehouseStockItemVO."""
        return WarehouseStockItemVO(
            stock_id=UUID("11111111-1111-1111-1111-111111111111"),
            product_id=UUID("22222222-2222-2222-2222-222222222222"),
            supplier_id=UUID("33333333-3333-3333-3333-333333333333"),
            name=ProductNameVO("Premium Rice"),
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(80),
            stock_disponible=80,
            created_at=datetime(2025, 1, 1, 10, 0, 0),
            updated_at=datetime(2025, 1, 2, 10, 0, 0),
        )

    # ---------------------------------------------------------------------------
    # creation
    # ---------------------------------------------------------------------------

    def test_should_create_warehouse_stock_vo_when_valid_data_is_provided(
        self,
    ) -> None:
        """Test that a WarehouseStockVO can be created successfully."""
        item = self._build_item()

        warehouse_stock = WarehouseStockVO(
            warehouse_stock=[item],
            page=0,
            page_size=10,
            elements=1,
        )

        assert warehouse_stock.warehouse_stock == [item]
        assert warehouse_stock.page == 0
        assert warehouse_stock.page_size == 10
        assert warehouse_stock.elements == 1

    # ---------------------------------------------------------------------------
    # validation
    # ---------------------------------------------------------------------------

    def test_should_raise_exception_when_page_is_negative(
        self,
    ) -> None:
        """Test that an exception is raised when page is negative."""
        with pytest.raises(InvalidPaginationElementsException) as exc_info:
            WarehouseStockVO(
                warehouse_stock=[],
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
            WarehouseStockVO(
                warehouse_stock=[],
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
            WarehouseStockVO(
                warehouse_stock=[],
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
            WarehouseStockVO(
                warehouse_stock=[],
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
        """Test that the WarehouseStockVO is immutable."""
        warehouse_stock = WarehouseStockVO(
            warehouse_stock=[],
            page=0,
            page_size=10,
            elements=0,
        )

        with pytest.raises(FrozenInstanceError):
            warehouse_stock.page = 1  # type: ignore[misc]

    # ---------------------------------------------------------------------------
    # equality
    # ---------------------------------------------------------------------------

    def test_should_return_equal_warehouse_stock_vos_when_data_is_identical(
        self,
    ) -> None:
        """Test that two WarehouseStockVO instances with identical data are equal."""
        item = self._build_item()

        vo1 = WarehouseStockVO(
            warehouse_stock=[item],
            page=0,
            page_size=10,
            elements=1,
        )

        vo2 = WarehouseStockVO(
            warehouse_stock=[item],
            page=0,
            page_size=10,
            elements=1,
        )

        assert vo1 == vo2

    def test_should_return_different_warehouse_stock_vos_when_data_differs(
        self,
    ) -> None:
        """Test that two WarehouseStockVO instances with different data are not equal."""
        item = self._build_item()

        vo1 = WarehouseStockVO(
            warehouse_stock=[item],
            page=0,
            page_size=10,
            elements=1,
        )

        vo2 = WarehouseStockVO(
            warehouse_stock=[item],
            page=1,
            page_size=10,
            elements=1,
        )

        assert vo1 != vo2
