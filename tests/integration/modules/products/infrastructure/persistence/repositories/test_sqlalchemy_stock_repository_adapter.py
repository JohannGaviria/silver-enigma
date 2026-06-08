from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
from faker import Faker
from sqlalchemy.exc import SQLAlchemyError

from src.modules.products.domain.entities.stock_entity import StockEntity
from src.modules.products.domain.exceptions.stock_exception import (
    StockRepositoryException,
)
from src.modules.products.domain.value_objects.available_stock_vo import (
    AvailableStockVO,
)
from src.modules.products.domain.value_objects.total_stock_vo import (
    TotalStockVO,
)
from src.modules.products.infrastructure.persistence.repositories.sqlalchemy_stock_repository_adapter import (
    SQLAlchemyStockRepositoryAdapter,
)


class TestSQLAlchemyStockRepositoryAdapter:
    # --------------------------------------------------------------------------
    # find_by_id
    # --------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_find_stock_by_id(
        self,
        faker: Faker,
        stock_repository: SQLAlchemyStockRepositoryAdapter,
    ) -> None:
        """find_by_id() must return the stock with the given ID."""
        stock = StockEntity.create(
            product_id=UUID(faker.uuid4()),
            warehouse_id=UUID(faker.uuid4()),
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(50),
        )
        await stock_repository.save(stock)

        result = await stock_repository.find_by_id(stock.id)

        assert result
        assert result.id == stock.id
        assert result.product_id == stock.product_id
        assert result.warehouse_id == stock.warehouse_id
        assert result.total_stock == stock.total_stock
        assert result.available_stock == stock.available_stock

    @pytest.mark.asyncio
    async def test_should_return_none_when_stock_not_found(
        self,
        faker: Faker,
        stock_repository: SQLAlchemyStockRepositoryAdapter,
    ) -> None:
        """find_by_id() must return None when the stock is not found."""
        result = await stock_repository.find_by_id(UUID(faker.uuid4()))

        assert result is None

    @pytest.mark.asyncio
    async def test_should_raise_stock_repository_exception_when_execute_fails_in_find_by_id(
        self,
        faker: Faker,
        stock_repository: SQLAlchemyStockRepositoryAdapter,
    ) -> None:
        """StockRepositoryException must be raised when session.execute fails."""
        with patch.object(
            stock_repository.session,
            "execute",
            new=AsyncMock(side_effect=SQLAlchemyError("boom")),
        ):
            with pytest.raises(StockRepositoryException):
                await stock_repository.find_by_id(UUID(faker.uuid4()))

    # --------------------------------------------------------------------------
    # find_by_product_and_warehouse
    # --------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_find_stock_by_product_and_warehouse(
        self,
        faker: Faker,
        stock_repository: SQLAlchemyStockRepositoryAdapter,
    ) -> None:
        """find_by_product_and_warehouse() must return the matching stock."""
        product_id = UUID(faker.uuid4())
        warehouse_id = UUID(faker.uuid4())

        stock = StockEntity.create(
            product_id=product_id,
            warehouse_id=warehouse_id,
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(50),
        )

        await stock_repository.save(stock)

        result = await stock_repository.find_by_product_and_warehouse(
            product_id,
            warehouse_id,
        )

        assert result
        assert result.id == stock.id
        assert result.product_id == product_id
        assert result.warehouse_id == warehouse_id

    @pytest.mark.asyncio
    async def test_should_return_none_when_stock_by_product_and_warehouse_not_found(
        self,
        faker: Faker,
        stock_repository: SQLAlchemyStockRepositoryAdapter,
    ) -> None:
        """find_by_product_and_warehouse() must return None when stock does not exist."""
        result = await stock_repository.find_by_product_and_warehouse(
            UUID(faker.uuid4()),
            UUID(faker.uuid4()),
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_should_raise_stock_repository_exception_when_execute_fails_in_find_by_product_and_warehouse(
        self,
        faker: Faker,
        stock_repository: SQLAlchemyStockRepositoryAdapter,
    ) -> None:
        """StockRepositoryException must be raised when session.execute fails."""
        with patch.object(
            stock_repository.session,
            "execute",
            new=AsyncMock(side_effect=SQLAlchemyError("boom")),
        ):
            with pytest.raises(StockRepositoryException):
                await stock_repository.find_by_product_and_warehouse(
                    UUID(faker.uuid4()),
                    UUID(faker.uuid4()),
                )

    # --------------------------------------------------------------------------
    # update
    # --------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_update_stock_and_return_entity(
        self,
        faker: Faker,
        stock_repository: SQLAlchemyStockRepositoryAdapter,
    ) -> None:
        """update() must flush the entity and return the updated stock."""
        stock = StockEntity.create(
            product_id=UUID(faker.uuid4()),
            warehouse_id=UUID(faker.uuid4()),
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(50),
        )

        await stock_repository.save(stock)

        entity = stock.update_total_stock(
            total_stock=TotalStockVO(200),
        )

        result = await stock_repository.update(entity)

        assert result.id == entity.id
        assert result.product_id == entity.product_id
        assert result.warehouse_id == entity.warehouse_id
        assert result.total_stock == TotalStockVO(200)
        assert result.available_stock == entity.available_stock

    @pytest.mark.asyncio
    async def test_should_raise_stock_repository_exception_when_flush_fails_in_update(
        self,
        faker: Faker,
        stock_repository: SQLAlchemyStockRepositoryAdapter,
    ) -> None:
        """StockRepositoryException must be raised when session.flush fails."""
        stock = StockEntity.create(
            product_id=UUID(faker.uuid4()),
            warehouse_id=UUID(faker.uuid4()),
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(50),
        )

        await stock_repository.save(stock)

        with patch.object(
            stock_repository.session,
            "flush",
            new=AsyncMock(side_effect=SQLAlchemyError("boom")),
        ):
            with pytest.raises(StockRepositoryException):
                await stock_repository.update(stock)

    @pytest.mark.asyncio
    async def test_should_never_call_commit_on_update(
        self,
        faker: Faker,
        stock_repository: SQLAlchemyStockRepositoryAdapter,
    ) -> None:
        """The repository must NEVER call session.commit()."""
        stock = StockEntity.create(
            product_id=UUID(faker.uuid4()),
            warehouse_id=UUID(faker.uuid4()),
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(50),
        )

        await stock_repository.save(stock)

        with patch.object(
            stock_repository.session,
            "commit",
            new=AsyncMock(),
        ) as mock_commit:
            await stock_repository.update(stock)

        mock_commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_never_call_rollback_on_update(
        self,
        faker: Faker,
        stock_repository: SQLAlchemyStockRepositoryAdapter,
    ) -> None:
        """The repository must NEVER call session.rollback()."""
        stock = StockEntity.create(
            product_id=UUID(faker.uuid4()),
            warehouse_id=UUID(faker.uuid4()),
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(50),
        )

        await stock_repository.save(stock)

        with patch.object(
            stock_repository.session,
            "rollback",
            new=AsyncMock(),
        ) as mock_rollback:
            await stock_repository.update(stock)

        mock_rollback.assert_not_awaited()

    # ---------------------------------------------------------------------------
    # save
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_save_stock_and_return_stock_entity(
        self,
        faker: Faker,
        stock_repository: SQLAlchemyStockRepositoryAdapter,
    ) -> None:
        """save() must flush the entity and return it with all fields intact."""
        entity = StockEntity.create(
            product_id=UUID(faker.uuid4()),
            warehouse_id=UUID(faker.uuid4()),
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(50),
        )

        result = await stock_repository.save(entity)

        assert result.id == entity.id
        assert result.product_id == entity.product_id
        assert result.warehouse_id == entity.warehouse_id
        assert result.total_stock == entity.total_stock
        assert result.available_stock == entity.available_stock

    @pytest.mark.asyncio
    async def test_should_persist_multiple_stocks_independently(
        self,
        faker: Faker,
        stock_repository: SQLAlchemyStockRepositoryAdapter,
    ) -> None:
        """Two different stock entities can be saved without conflict."""
        product_id = UUID(faker.uuid4())

        entity1 = StockEntity.create(
            product_id=product_id,
            warehouse_id=UUID(faker.uuid4()),
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(50),
        )

        entity2 = StockEntity.create(
            product_id=product_id,
            warehouse_id=UUID(faker.uuid4()),
            total_stock=TotalStockVO(200),
            available_stock=AvailableStockVO(100),
        )

        result1 = await stock_repository.save(entity1)
        result2 = await stock_repository.save(entity2)

        assert result1.id != result2.id

    @pytest.mark.asyncio
    async def test_should_raise_stock_repository_exception_when_flush_fails_in_save(
        self,
        faker: Faker,
        stock_repository: SQLAlchemyStockRepositoryAdapter,
    ) -> None:
        """StockRepositoryException must be raised when session.flush fails."""
        entity = StockEntity.create(
            product_id=UUID(faker.uuid4()),
            warehouse_id=UUID(faker.uuid4()),
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(50),
        )

        with patch.object(
            stock_repository.session,
            "flush",
            new=AsyncMock(side_effect=SQLAlchemyError("boom")),
        ):
            with pytest.raises(StockRepositoryException):
                await stock_repository.save(entity)

    @pytest.mark.asyncio
    async def test_should_never_call_commit_on_save(
        self,
        faker: Faker,
        stock_repository: SQLAlchemyStockRepositoryAdapter,
    ) -> None:
        """The repository must NEVER call session.commit()."""
        entity = StockEntity.create(
            product_id=UUID(faker.uuid4()),
            warehouse_id=UUID(faker.uuid4()),
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(50),
        )

        with patch.object(
            stock_repository.session,
            "commit",
            new=AsyncMock(),
        ) as mock_commit:
            await stock_repository.save(entity)

        mock_commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_never_call_rollback_on_save(
        self,
        faker: Faker,
        stock_repository: SQLAlchemyStockRepositoryAdapter,
    ) -> None:
        """The repository must NEVER call session.rollback()."""
        entity = StockEntity.create(
            product_id=UUID(faker.uuid4()),
            warehouse_id=UUID(faker.uuid4()),
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(50),
        )

        with patch.object(
            stock_repository.session,
            "rollback",
            new=AsyncMock(),
        ) as mock_rollback:
            await stock_repository.save(entity)

        mock_rollback.assert_not_awaited()
