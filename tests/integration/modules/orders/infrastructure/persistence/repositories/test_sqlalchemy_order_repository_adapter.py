from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
from faker import Faker
from sqlalchemy.exc import SQLAlchemyError

from src.modules.orders.domain.entities.order_entity import OrderEntity
from src.modules.orders.domain.exceptions.order_exception import (
    OrderRepositoryException,
)
from src.modules.orders.infrastructure.persistence.repositories.sqlalchemy_order_repository_adapter import (
    SQLAlchemyOrderRepositoryAdapter,
)
from src.shared.domain.enums.order_status_enum import OrderStatusEnum


class TestSQLAlchemyOrderRepositoryAdapter:
    # ---------------------------------------------------------------------------
    # save
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_save_order_and_return_order_entity(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
    ) -> None:
        """save() must flush the entity and return it with all fields intact."""
        entity = OrderEntity.create(
            buyer_id=UUID(faker.uuid4()),
            supplier_id=UUID(faker.uuid4()),
            status_order=OrderStatusEnum.DRAFT,
        )

        result = await order_repository.save(entity)

        assert result.id == entity.id
        assert result.buyer_id == entity.buyer_id
        assert result.supplier_id == entity.supplier_id
        assert result.status_order == OrderStatusEnum.DRAFT

    @pytest.mark.asyncio
    async def test_should_persist_multiple_orders_independently(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
    ) -> None:
        """Two different order entities can be saved without conflict."""
        supplier_id = UUID(faker.uuid4())

        entity1 = OrderEntity.create(
            buyer_id=UUID(faker.uuid4()),
            supplier_id=supplier_id,
            status_order=OrderStatusEnum.DRAFT,
        )
        entity2 = OrderEntity.create(
            buyer_id=UUID(faker.uuid4()),
            supplier_id=supplier_id,
            status_order=OrderStatusEnum.DRAFT,
        )

        result1 = await order_repository.save(entity1)
        result2 = await order_repository.save(entity2)

        assert result1.id != result2.id
        assert result1.supplier_id == result2.supplier_id

    @pytest.mark.asyncio
    async def test_should_raise_order_repository_exception_when_flush_fails_in_save(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
    ) -> None:
        """OrderRepositoryException must be raised when session.flush fails."""
        entity = OrderEntity.create(
            buyer_id=UUID(faker.uuid4()),
            supplier_id=UUID(faker.uuid4()),
            status_order=OrderStatusEnum.DRAFT,
        )

        with patch.object(
            order_repository.session,
            "flush",
            new=AsyncMock(side_effect=SQLAlchemyError("boom")),
        ):
            with pytest.raises(OrderRepositoryException):
                await order_repository.save(entity)

    @pytest.mark.asyncio
    async def test_should_never_call_commit_on_save(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
    ) -> None:
        """The repository must NEVER call session.commit()."""
        entity = OrderEntity.create(
            buyer_id=UUID(faker.uuid4()),
            supplier_id=UUID(faker.uuid4()),
            status_order=OrderStatusEnum.DRAFT,
        )

        with patch.object(
            order_repository.session,
            "commit",
            new=AsyncMock(),
        ) as mock_commit:
            await order_repository.save(entity)

        mock_commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_never_call_rollback_on_save(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
    ) -> None:
        """The repository must NEVER call session.rollback()."""
        entity = OrderEntity.create(
            buyer_id=UUID(faker.uuid4()),
            supplier_id=UUID(faker.uuid4()),
            status_order=OrderStatusEnum.DRAFT,
        )

        with patch.object(
            order_repository.session,
            "rollback",
            new=AsyncMock(),
        ) as mock_rollback:
            await order_repository.save(entity)

        mock_rollback.assert_not_awaited()

    # ---------------------------------------------------------------------------
    # find_by_id
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_find_order_by_id(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
    ) -> None:
        """find_by_id() must return the order with the given ID."""
        entity = OrderEntity.create(
            buyer_id=UUID(faker.uuid4()),
            supplier_id=UUID(faker.uuid4()),
            status_order=OrderStatusEnum.DRAFT,
        )
        await order_repository.save(entity)

        result = await order_repository.find_by_id(entity.id)

        assert result is not None
        assert result.id == entity.id
        assert result.buyer_id == entity.buyer_id
        assert result.supplier_id == entity.supplier_id

    @pytest.mark.asyncio
    async def test_should_return_none_when_order_not_found(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
    ) -> None:
        """find_by_id() must return None when the order does not exist."""
        result = await order_repository.find_by_id(UUID(faker.uuid4()))

        assert result is None

    @pytest.mark.asyncio
    async def test_should_raise_order_repository_exception_when_execute_fails_in_find_by_id(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
    ) -> None:
        """OrderRepositoryException must be raised when session.execute fails."""
        with patch.object(
            order_repository.session,
            "execute",
            new=AsyncMock(side_effect=SQLAlchemyError("boom")),
        ):
            with pytest.raises(OrderRepositoryException):
                await order_repository.find_by_id(UUID(faker.uuid4()))

    # ---------------------------------------------------------------------------
    # update
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_update_order_and_return_entity(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
    ) -> None:
        """update() must flush the entity and return it with updated fields."""
        entity = OrderEntity.create(
            buyer_id=UUID(faker.uuid4()),
            supplier_id=UUID(faker.uuid4()),
            status_order=OrderStatusEnum.DRAFT,
        )
        await order_repository.save(entity)

        # TODO: Uncomment when update() is implemented
        # updated = entity.update()
        # result = await order_repository.update(updated)

        # assert result.id == entity.id
        # assert result.status_order == OrderStatusEnum.CONFIRMED

    @pytest.mark.asyncio
    async def test_should_raise_order_repository_exception_when_flush_fails_in_update(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
    ) -> None:
        """OrderRepositoryException must be raised when session.flush fails."""
        entity = OrderEntity.create(
            buyer_id=UUID(faker.uuid4()),
            supplier_id=UUID(faker.uuid4()),
            status_order=OrderStatusEnum.DRAFT,
        )
        await order_repository.save(entity)

        with patch.object(
            order_repository.session,
            "flush",
            new=AsyncMock(side_effect=SQLAlchemyError("boom")),
        ):
            with pytest.raises(OrderRepositoryException):
                await order_repository.update(entity)

    @pytest.mark.asyncio
    async def test_should_never_call_commit_on_update(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
    ) -> None:
        """The repository must NEVER call session.commit()."""
        entity = OrderEntity.create(
            buyer_id=UUID(faker.uuid4()),
            supplier_id=UUID(faker.uuid4()),
            status_order=OrderStatusEnum.DRAFT,
        )
        await order_repository.save(entity)

        with patch.object(
            order_repository.session,
            "commit",
            new=AsyncMock(),
        ) as mock_commit:
            await order_repository.update(entity)

        mock_commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_never_call_rollback_on_update(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
    ) -> None:
        """The repository must NEVER call session.rollback()."""
        entity = OrderEntity.create(
            buyer_id=UUID(faker.uuid4()),
            supplier_id=UUID(faker.uuid4()),
            status_order=OrderStatusEnum.DRAFT,
        )
        await order_repository.save(entity)

        with patch.object(
            order_repository.session,
            "rollback",
            new=AsyncMock(),
        ) as mock_rollback:
            await order_repository.update(entity)

        mock_rollback.assert_not_awaited()
