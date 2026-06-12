from dataclasses import FrozenInstanceError
from datetime import datetime
from uuid import UUID

import pytest
from faker import Faker

from src.modules.products.domain.value_objects.product_name_vo import ProductNameVO
from src.modules.products.domain.value_objects.reserved_stock_vo import (
    ReservedStockVO,
)
from src.modules.products.domain.value_objects.total_stock_vo import TotalStockVO
from src.modules.products.domain.value_objects.warehouse_stock_item_vo import (
    WarehouseStockItemVO,
)


class TestWarehouseStockItemVO:
    # ---------------------------------------------------------------------------
    # creation
    # ---------------------------------------------------------------------------

    def test_should_create_warehouse_stock_item_vo_when_valid_data_is_provided(
        self,
        faker: Faker,
    ) -> None:
        """Test that a WarehouseStockItemVO can be created successfully when valid data is provided."""
        stock_id = UUID(faker.uuid4())
        product_id = UUID(faker.uuid4())
        supplier_id = UUID(faker.uuid4())

        created_at = faker.date_time()
        updated_at = faker.date_time()

        warehouse_stock_item = WarehouseStockItemVO(
            stock_id=stock_id,
            product_id=product_id,
            supplier_id=supplier_id,
            name=ProductNameVO("Premium Rice"),
            total_stock=TotalStockVO(100),
            reserved_stock=ReservedStockVO(80),
            available_stock=80,
            created_at=created_at,
            updated_at=updated_at,
        )

        assert warehouse_stock_item.stock_id == stock_id
        assert warehouse_stock_item.product_id == product_id
        assert warehouse_stock_item.supplier_id == supplier_id
        assert warehouse_stock_item.name == ProductNameVO("Premium Rice")
        assert warehouse_stock_item.total_stock == TotalStockVO(100)
        assert warehouse_stock_item.reserved_stock == ReservedStockVO(80)
        assert warehouse_stock_item.available_stock == 80
        assert warehouse_stock_item.created_at == created_at
        assert warehouse_stock_item.updated_at == updated_at

    # ---------------------------------------------------------------------------
    # immutability
    # ---------------------------------------------------------------------------

    def test_should_raise_exception_when_attempting_to_modify_stock_id(
        self,
        faker: Faker,
    ) -> None:
        """Test that the WarehouseStockItemVO is immutable."""
        warehouse_stock_item = WarehouseStockItemVO(
            stock_id=UUID(faker.uuid4()),
            product_id=UUID(faker.uuid4()),
            supplier_id=UUID(faker.uuid4()),
            name=ProductNameVO("Premium Rice"),
            total_stock=TotalStockVO(100),
            reserved_stock=ReservedStockVO(80),
            available_stock=80,
            created_at=faker.date_time(),
            updated_at=faker.date_time(),
        )

        with pytest.raises(FrozenInstanceError):
            warehouse_stock_item.stock_id = UUID(faker.uuid4())  # type: ignore[misc]

    # ---------------------------------------------------------------------------
    # equality
    # ---------------------------------------------------------------------------

    def test_should_return_equal_warehouse_stock_item_vos_when_data_is_identical(
        self,
    ) -> None:
        """Test that two WarehouseStockItemVO instances with identical data are equal."""
        stock_id = UUID("11111111-1111-1111-1111-111111111111")
        product_id = UUID("22222222-2222-2222-2222-222222222222")
        supplier_id = UUID("33333333-3333-3333-3333-333333333333")

        created_at = datetime(2025, 1, 1, 10, 0, 0)
        updated_at = datetime(2025, 1, 2, 10, 0, 0)

        vo1 = WarehouseStockItemVO(
            stock_id=stock_id,
            product_id=product_id,
            supplier_id=supplier_id,
            name=ProductNameVO("Premium Rice"),
            total_stock=TotalStockVO(100),
            reserved_stock=ReservedStockVO(80),
            available_stock=80,
            created_at=created_at,
            updated_at=updated_at,
        )

        vo2 = WarehouseStockItemVO(
            stock_id=stock_id,
            product_id=product_id,
            supplier_id=supplier_id,
            name=ProductNameVO("Premium Rice"),
            total_stock=TotalStockVO(100),
            reserved_stock=ReservedStockVO(80),
            available_stock=80,
            created_at=created_at,
            updated_at=updated_at,
        )

        assert vo1 == vo2

    def test_should_return_different_warehouse_stock_item_vos_when_data_differs(
        self,
    ) -> None:
        """Test that two WarehouseStockItemVO instances with different data are not equal."""
        created_at = datetime(2025, 1, 1, 10, 0, 0)
        updated_at = datetime(2025, 1, 2, 10, 0, 0)

        vo1 = WarehouseStockItemVO(
            stock_id=UUID("11111111-1111-1111-1111-111111111111"),
            product_id=UUID("22222222-2222-2222-2222-222222222222"),
            supplier_id=UUID("33333333-3333-3333-3333-333333333333"),
            name=ProductNameVO("Premium Rice"),
            total_stock=TotalStockVO(100),
            reserved_stock=ReservedStockVO(80),
            available_stock=80,
            created_at=created_at,
            updated_at=updated_at,
        )

        vo2 = WarehouseStockItemVO(
            stock_id=UUID("44444444-4444-4444-4444-444444444444"),
            product_id=UUID("22222222-2222-2222-2222-222222222222"),
            supplier_id=UUID("33333333-3333-3333-3333-333333333333"),
            name=ProductNameVO("Premium Rice"),
            total_stock=TotalStockVO(100),
            reserved_stock=ReservedStockVO(80),
            available_stock=80,
            created_at=created_at,
            updated_at=updated_at,
        )

        assert vo1 != vo2
