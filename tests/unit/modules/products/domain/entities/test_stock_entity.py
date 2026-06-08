from dataclasses import FrozenInstanceError
from typing import Any
from uuid import UUID

import pytest
from faker import Faker

from src.modules.products.domain.entities.stock_entity import StockEntity
from src.modules.products.domain.exceptions.stock_exception import (
    StockConflictException,
)
from src.modules.products.domain.value_objects.available_stock_vo import (
    AvailableStockVO,
)
from src.modules.products.domain.value_objects.total_stock_vo import TotalStockVO


class TestStockEntity:
    # ---------------------------------------------------------------------------
    # create
    # ---------------------------------------------------------------------------

    def test_should_create_stock_entity_when_valid_data_is_provided(
        self,
        faker: Faker,
    ) -> None:
        """Test that the StockEntity can be created successfully when valid data is provided."""
        product_id = UUID(faker.uuid4())
        warehouse_id = UUID(faker.uuid4())
        total_stock = TotalStockVO(100)
        available_stock = AvailableStockVO(75)

        stock = StockEntity.create(
            product_id=product_id,
            warehouse_id=warehouse_id,
            total_stock=total_stock,
            available_stock=available_stock,
        )

        assert stock.id is not None
        assert stock.product_id == product_id
        assert stock.warehouse_id == warehouse_id
        assert stock.total_stock == total_stock
        assert stock.available_stock == available_stock

        assert stock.created_at is not None
        assert stock.updated_at is not None
        assert stock.created_at == stock.updated_at

        assert isinstance(stock.id, UUID)
        assert isinstance(stock.total_stock, TotalStockVO)
        assert isinstance(stock.available_stock, AvailableStockVO)

    def test_should_generate_unique_ids_for_different_stock_entities(
        self,
        faker: Faker,
    ) -> None:
        """Test that different StockEntity instances generate unique IDs."""
        product_id = UUID(faker.uuid4())
        warehouse_id = UUID(faker.uuid4())

        stock1 = StockEntity.create(
            product_id=product_id,
            warehouse_id=warehouse_id,
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(50),
        )

        stock2 = StockEntity.create(
            product_id=product_id,
            warehouse_id=warehouse_id,
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(50),
        )

        assert stock1.id != stock2.id

    # ---------------------------------------------------------------------------
    # update_total_stock
    # ---------------------------------------------------------------------------

    def test_should_update_total_stock_when_new_value_is_greater_than_or_equal_to_available_stock(
        self,
        faker: Faker,
    ) -> None:
        """Test that total stock can be updated when it is not lower than available stock."""
        stock = StockEntity.create(
            product_id=UUID(faker.uuid4()),
            warehouse_id=UUID(faker.uuid4()),
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(50),
        )

        updated_stock = stock.update_total_stock(
            total_stock=TotalStockVO(80),
        )

        assert updated_stock.total_stock == TotalStockVO(80)
        assert updated_stock.available_stock == stock.available_stock

        assert updated_stock.id == stock.id
        assert updated_stock.product_id == stock.product_id
        assert updated_stock.warehouse_id == stock.warehouse_id
        assert updated_stock.created_at == stock.created_at

        assert updated_stock.updated_at >= stock.updated_at
        assert updated_stock != stock

    def test_should_raise_stock_conflict_exception_when_total_stock_is_lower_than_available_stock(
        self,
        faker: Faker,
    ) -> None:
        """Test that updating total stock below available stock raises an exception."""
        stock = StockEntity.create(
            product_id=UUID(faker.uuid4()),
            warehouse_id=UUID(faker.uuid4()),
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(50),
        )

        with pytest.raises(StockConflictException):
            stock.update_total_stock(
                total_stock=TotalStockVO(40),
            )

    # ---------------------------------------------------------------------------
    # immutability
    # ---------------------------------------------------------------------------

    @pytest.mark.parametrize(
        ("attribute", "value"),
        [
            ("total_stock", TotalStockVO(200)),
            ("available_stock", AvailableStockVO(150)),
        ],
    )
    def test_should_raise_exception_when_attempting_to_modify_stock_entity_attributes(
        self,
        faker: Faker,
        attribute: str,
        value: Any,
    ) -> None:
        """Test that the StockEntity raises a FrozenInstanceError when attempting to modify its attributes."""
        stock = StockEntity.create(
            product_id=UUID(faker.uuid4()),
            warehouse_id=UUID(faker.uuid4()),
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(50),
        )

        with pytest.raises(FrozenInstanceError):
            setattr(stock, attribute, value)

    # ---------------------------------------------------------------------------
    # equality
    # ---------------------------------------------------------------------------

    def test_should_return_equal_stock_entities_when_data_is_identical(
        self,
        faker: Faker,
    ) -> None:
        """Test that two StockEntity instances with identical data are considered equal."""
        stock1 = StockEntity.create(
            product_id=UUID(faker.uuid4()),
            warehouse_id=UUID(faker.uuid4()),
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(50),
        )

        stock2 = StockEntity(
            id=stock1.id,
            product_id=stock1.product_id,
            warehouse_id=stock1.warehouse_id,
            total_stock=stock1.total_stock,
            available_stock=stock1.available_stock,
            created_at=stock1.created_at,
            updated_at=stock1.updated_at,
        )

        assert stock1 == stock2
