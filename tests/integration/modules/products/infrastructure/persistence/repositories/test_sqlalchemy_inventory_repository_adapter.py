from decimal import Decimal
from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
from faker import Faker
from sqlalchemy.exc import SQLAlchemyError

from src.modules.products.domain.entities.product_entity import ProductEntity
from src.modules.products.domain.entities.stock_entity import StockEntity
from src.modules.products.domain.enums.unit_of_measure_enum import UnitOfMeasureEnum
from src.modules.products.domain.exceptions.inventory_exception import (
    InventoryRepositoryException,
)
from src.modules.products.domain.value_objects.available_stock_vo import (
    AvailableStockVO,
)
from src.modules.products.domain.value_objects.product_name_vo import ProductNameVO
from src.modules.products.domain.value_objects.total_stock_vo import TotalStockVO
from src.modules.products.domain.value_objects.unit_price_vo import UnitPriceVO
from src.modules.products.infrastructure.persistence.repositories.sqlalchemy_inventory_repository_adapter import (
    SQLAlchemyInventoryRepositoryAdapter,
)
from src.modules.products.infrastructure.persistence.repositories.sqlalchemy_product_repository_adapter import (
    SQLAlchemyProductRepositoryAdapter,
)
from src.modules.products.infrastructure.persistence.repositories.sqlalchemy_stock_repository_adapter import (
    SQLAlchemyStockRepositoryAdapter,
)
from src.modules.warehouses.domain.entities.warehouse_entity import WarehouseEntity
from src.modules.warehouses.domain.value_objects.warehouse_address_vo import (
    WarehouseAddressVO,
)
from src.modules.warehouses.domain.value_objects.warehouse_name_vo import (
    WarehouseNameVO,
)
from src.modules.warehouses.infrastructure.persistence.repositories.sqlalchemy_warehouse_repository_adapter import (
    SQLAlchemyWarehouseRepositoryAdapter,
)


class TestSQLAlchemyInventoryRepositoryAdapter:
    # --------------------------------------------------------------------------
    # find_inventory_by_user_and_warehouse
    # --------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_return_inventory_for_user_and_warehouse(
        self,
        faker: Faker,
        product_repository: SQLAlchemyProductRepositoryAdapter,
        warehouse_repository: SQLAlchemyWarehouseRepositoryAdapter,
        stock_repository: SQLAlchemyStockRepositoryAdapter,
        inventory_repository: SQLAlchemyInventoryRepositoryAdapter,
    ) -> None:
        """Must return warehouse inventory filtered by supplier and warehouse."""
        supplier_id = UUID(faker.uuid4())

        warehouse = WarehouseEntity.create(
            supplier_id=supplier_id,
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )
        await warehouse_repository.save(warehouse)

        product = ProductEntity.create(
            supplier_id=supplier_id,
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("1000")),
        )
        await product_repository.save(product)

        stock = StockEntity.create(
            product_id=product.id,
            warehouse_id=warehouse.id,
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(60),
        )
        await stock_repository.save(stock)

        result = await inventory_repository.find_inventory_by_user_and_warehouse(
            user_id=supplier_id,
            warehouse_id=warehouse.id,
            page=1,
            page_size=10,
        )

        assert result.page == 1
        assert result.page_size == 10
        assert result.elements == 1

        assert len(result.warehouse_stock) == 1

        item = result.warehouse_stock[0]

        assert item.stock_id == stock.id
        assert item.product_id == product.id
        assert item.supplier_id == supplier_id
        assert item.name == product.name
        assert item.total_stock == TotalStockVO(100)
        assert item.available_stock == AvailableStockVO(60)
        assert item.stock_disponible == 40

    @pytest.mark.asyncio
    async def test_should_return_empty_inventory_when_no_stock_exists(
        self,
        faker: Faker,
        inventory_repository: SQLAlchemyInventoryRepositoryAdapter,
    ) -> None:
        """Must return an empty WarehouseStockVO when nothing matches."""
        result = await inventory_repository.find_inventory_by_user_and_warehouse(
            user_id=UUID(faker.uuid4()),
            warehouse_id=UUID(faker.uuid4()),
            page=1,
            page_size=10,
        )

        assert result.page == 1
        assert result.page_size == 10
        assert result.elements == 0
        assert result.warehouse_stock == []

    @pytest.mark.asyncio
    async def test_should_filter_inventory_by_supplier(
        self,
        faker: Faker,
        product_repository: SQLAlchemyProductRepositoryAdapter,
        warehouse_repository: SQLAlchemyWarehouseRepositoryAdapter,
        stock_repository: SQLAlchemyStockRepositoryAdapter,
        inventory_repository: SQLAlchemyInventoryRepositoryAdapter,
    ) -> None:
        """Only inventory belonging to the supplier must be returned."""
        supplier_id = UUID(faker.uuid4())
        other_supplier_id = UUID(faker.uuid4())

        warehouse = WarehouseEntity.create(
            supplier_id=supplier_id,
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )
        await warehouse_repository.save(warehouse)

        product = ProductEntity.create(
            supplier_id=supplier_id,
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("1000")),
        )
        await product_repository.save(product)

        stock = StockEntity.create(
            product_id=product.id,
            warehouse_id=warehouse.id,
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(50),
        )
        await stock_repository.save(stock)

        result = await inventory_repository.find_inventory_by_user_and_warehouse(
            user_id=other_supplier_id,
            warehouse_id=warehouse.id,
            page=1,
            page_size=10,
        )

        assert result.elements == 0
        assert result.warehouse_stock == []

    @pytest.mark.asyncio
    async def test_should_filter_inventory_by_warehouse(
        self,
        faker: Faker,
        product_repository: SQLAlchemyProductRepositoryAdapter,
        warehouse_repository: SQLAlchemyWarehouseRepositoryAdapter,
        stock_repository: SQLAlchemyStockRepositoryAdapter,
        inventory_repository: SQLAlchemyInventoryRepositoryAdapter,
    ) -> None:
        """Only inventory from the requested warehouse must be returned."""
        supplier_id = UUID(faker.uuid4())

        warehouse_1 = WarehouseEntity.create(
            supplier_id=supplier_id,
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )
        await warehouse_repository.save(warehouse_1)

        warehouse_2 = WarehouseEntity.create(
            supplier_id=supplier_id,
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )
        await warehouse_repository.save(warehouse_2)

        product = ProductEntity.create(
            supplier_id=supplier_id,
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("1000")),
        )
        await product_repository.save(product)

        stock_1 = StockEntity.create(
            product_id=product.id,
            warehouse_id=warehouse_1.id,
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(80),
        )
        await stock_repository.save(stock_1)

        stock_2 = StockEntity.create(
            product_id=product.id,
            warehouse_id=warehouse_2.id,
            total_stock=TotalStockVO(200),
            available_stock=AvailableStockVO(100),
        )
        await stock_repository.save(stock_2)

        result = await inventory_repository.find_inventory_by_user_and_warehouse(
            user_id=supplier_id,
            warehouse_id=warehouse_1.id,
            page=1,
            page_size=10,
        )

        assert result.elements == 1
        assert len(result.warehouse_stock) == 1
        assert result.warehouse_stock[0].stock_id == stock_1.id

    @pytest.mark.asyncio
    async def test_should_paginate_inventory_results(
        self,
        faker: Faker,
        product_repository: SQLAlchemyProductRepositoryAdapter,
        warehouse_repository: SQLAlchemyWarehouseRepositoryAdapter,
        stock_repository: SQLAlchemyStockRepositoryAdapter,
        inventory_repository: SQLAlchemyInventoryRepositoryAdapter,
    ) -> None:
        """Pagination must return only the requested slice."""
        supplier_id = UUID(faker.uuid4())

        warehouse = WarehouseEntity.create(
            supplier_id=supplier_id,
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )
        await warehouse_repository.save(warehouse)

        for index in range(3):
            product = ProductEntity.create(
                supplier_id=supplier_id,
                name=ProductNameVO(f"{faker.company()}-{index}"),
                description=faker.text(),
                unit_of_measure=UnitOfMeasureEnum.UNIT,
                unit_price=UnitPriceVO(Decimal("1000")),
            )
            await product_repository.save(product)

            stock = StockEntity.create(
                product_id=product.id,
                warehouse_id=warehouse.id,
                total_stock=TotalStockVO(100),
                available_stock=AvailableStockVO(50),
            )
            await stock_repository.save(stock)

        result = await inventory_repository.find_inventory_by_user_and_warehouse(
            user_id=supplier_id,
            warehouse_id=warehouse.id,
            page=1,
            page_size=1,
        )

        assert result.page == 1
        assert result.page_size == 1
        assert result.elements == 3
        assert len(result.warehouse_stock) == 1

    @pytest.mark.asyncio
    async def test_should_return_total_elements_independent_of_page_size(
        self,
        faker: Faker,
        product_repository: SQLAlchemyProductRepositoryAdapter,
        warehouse_repository: SQLAlchemyWarehouseRepositoryAdapter,
        stock_repository: SQLAlchemyStockRepositoryAdapter,
        inventory_repository: SQLAlchemyInventoryRepositoryAdapter,
    ) -> None:
        """Elements must contain the total matching rows."""
        supplier_id = UUID(faker.uuid4())

        warehouse = WarehouseEntity.create(
            supplier_id=supplier_id,
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )
        await warehouse_repository.save(warehouse)

        for _ in range(5):
            product = ProductEntity.create(
                supplier_id=supplier_id,
                name=ProductNameVO(faker.company()),
                description=faker.text(),
                unit_of_measure=UnitOfMeasureEnum.UNIT,
                unit_price=UnitPriceVO(Decimal("1000")),
            )
            await product_repository.save(product)

            stock = StockEntity.create(
                product_id=product.id,
                warehouse_id=warehouse.id,
                total_stock=TotalStockVO(100),
                available_stock=AvailableStockVO(50),
            )
            await stock_repository.save(stock)

        result = await inventory_repository.find_inventory_by_user_and_warehouse(
            user_id=supplier_id,
            warehouse_id=warehouse.id,
            page=1,
            page_size=2,
        )

        assert result.elements == 5
        assert len(result.warehouse_stock) == 2

    @pytest.mark.asyncio
    async def test_should_raise_inventory_repository_exception_when_execute_fails(
        self,
        faker: Faker,
        inventory_repository: SQLAlchemyInventoryRepositoryAdapter,
    ) -> None:
        """InventoryRepositoryException must be raised when session.execute fails."""
        with patch.object(
            inventory_repository.session,
            "execute",
            new=AsyncMock(side_effect=SQLAlchemyError("boom")),
        ):
            with pytest.raises(
                InventoryRepositoryException,
                match="Inventory repository error.",
            ):
                await inventory_repository.find_inventory_by_user_and_warehouse(
                    user_id=UUID(faker.uuid4()),
                    warehouse_id=UUID(faker.uuid4()),
                    page=1,
                    page_size=10,
                )

    @pytest.mark.asyncio
    async def test_should_never_call_commit(
        self,
        faker: Faker,
        inventory_repository: SQLAlchemyInventoryRepositoryAdapter,
    ) -> None:
        """Repository must never call commit()."""
        with patch.object(
            inventory_repository.session,
            "commit",
            new=AsyncMock(),
        ) as mock_commit:
            await inventory_repository.find_inventory_by_user_and_warehouse(
                user_id=UUID(faker.uuid4()),
                warehouse_id=UUID(faker.uuid4()),
                page=1,
                page_size=10,
            )

        mock_commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_never_call_rollback(
        self,
        faker: Faker,
        inventory_repository: SQLAlchemyInventoryRepositoryAdapter,
    ) -> None:
        """Repository must never call rollback()."""
        with patch.object(
            inventory_repository.session,
            "rollback",
            new=AsyncMock(),
        ) as mock_rollback:
            await inventory_repository.find_inventory_by_user_and_warehouse(
                user_id=UUID(faker.uuid4()),
                warehouse_id=UUID(faker.uuid4()),
                page=1,
                page_size=10,
            )

        mock_rollback.assert_not_awaited()
