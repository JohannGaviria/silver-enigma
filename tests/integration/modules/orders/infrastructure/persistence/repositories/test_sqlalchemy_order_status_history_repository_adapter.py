from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
from faker import Faker
from sqlalchemy.exc import SQLAlchemyError

from src.modules.orders.domain.entities.order_entity import OrderEntity
from src.modules.orders.domain.entities.order_status_history_entity import (
    OrderStatusHistoryEntity,
)
from src.modules.orders.domain.exceptions.order_exception import (
    OrderRepositoryException,
)
from src.modules.orders.infrastructure.persistence.repositories.sqlalchemy_order_repository_adapter import (
    SQLAlchemyOrderRepositoryAdapter,
)
from src.modules.orders.infrastructure.persistence.repositories.sqlalchemy_order_status_history_repository_adapter import (
    SQLAlchemyOrderStatusHistoryRepositoryAdapter,
)
from src.shared.domain.enums.order_status_enum import OrderStatusEnum
from src.shared.domain.enums.user_role_enum import UserRoleEnum


class TestSQLAlchemyOrderStatusHistoryRepositoryAdapter:
    # ---------------------------------------------------------------------------
    # save
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_save_status_history_successfully(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
        order_status_history_repository: SQLAlchemyOrderStatusHistoryRepositoryAdapter,
    ) -> None:
        """save() must persist the status history record without errors."""
        order = OrderEntity.create(
            buyer_id=UUID(faker.uuid4()),
            supplier_id=UUID(faker.uuid4()),
            status_order=OrderStatusEnum.DRAFT,
        )
        await order_repository.save(order)

        history = OrderStatusHistoryEntity.create(
            order_id=order.id,
            previous_status=OrderStatusEnum.DRAFT,
            new_status=OrderStatusEnum.CONFIRMED,
            changed_by=UUID(faker.uuid4()),
            changed_by_role=UserRoleEnum.SUPPLIER,
        )

        await order_status_history_repository.save(history)

    @pytest.mark.asyncio
    async def test_should_save_multiple_history_records_for_same_order(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
        order_status_history_repository: SQLAlchemyOrderStatusHistoryRepositoryAdapter,
    ) -> None:
        """Multiple status transitions must be recorded independently for the same order."""
        order = OrderEntity.create(
            buyer_id=UUID(faker.uuid4()),
            supplier_id=UUID(faker.uuid4()),
            status_order=OrderStatusEnum.DRAFT,
        )
        await order_repository.save(order)

        actor_id = UUID(faker.uuid4())

        history1 = OrderStatusHistoryEntity.create(
            order_id=order.id,
            previous_status=OrderStatusEnum.DRAFT,
            new_status=OrderStatusEnum.CONFIRMED,
            changed_by=actor_id,
            changed_by_role=UserRoleEnum.SUPPLIER,
        )
        history2 = OrderStatusHistoryEntity.create(
            order_id=order.id,
            previous_status=OrderStatusEnum.CONFIRMED,
            new_status=OrderStatusEnum.SHIPPED,
            changed_by=actor_id,
            changed_by_role=UserRoleEnum.SUPPLIER,
        )

        await order_status_history_repository.save(history1)
        await order_status_history_repository.save(history2)

        assert history1.id != history2.id

    @pytest.mark.asyncio
    async def test_should_persist_all_transition_fields(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
        order_status_history_repository: SQLAlchemyOrderStatusHistoryRepositoryAdapter,
    ) -> None:
        """All fields of the history record must be persisted correctly."""
        order = OrderEntity.create(
            buyer_id=UUID(faker.uuid4()),
            supplier_id=UUID(faker.uuid4()),
            status_order=OrderStatusEnum.DRAFT,
        )
        await order_repository.save(order)

        actor_id = UUID(faker.uuid4())
        history = OrderStatusHistoryEntity.create(
            order_id=order.id,
            previous_status=OrderStatusEnum.DRAFT,
            new_status=OrderStatusEnum.CANCELLED,
            changed_by=actor_id,
            changed_by_role=UserRoleEnum.BUYER,
        )

        await order_status_history_repository.save(history)

        assert history.order_id == order.id
        assert history.previous_status == OrderStatusEnum.DRAFT
        assert history.new_status == OrderStatusEnum.CANCELLED
        assert history.changed_by == actor_id
        assert history.changed_by_role == UserRoleEnum.BUYER

    @pytest.mark.asyncio
    async def test_should_raise_order_repository_exception_when_flush_fails_in_save(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
        order_status_history_repository: SQLAlchemyOrderStatusHistoryRepositoryAdapter,
    ) -> None:
        """OrderRepositoryException must be raised when session.flush fails."""
        order = OrderEntity.create(
            buyer_id=UUID(faker.uuid4()),
            supplier_id=UUID(faker.uuid4()),
            status_order=OrderStatusEnum.DRAFT,
        )
        await order_repository.save(order)

        history = OrderStatusHistoryEntity.create(
            order_id=order.id,
            previous_status=OrderStatusEnum.DRAFT,
            new_status=OrderStatusEnum.CONFIRMED,
            changed_by=UUID(faker.uuid4()),
            changed_by_role=UserRoleEnum.SUPPLIER,
        )

        with patch.object(
            order_status_history_repository.session,
            "flush",
            new=AsyncMock(side_effect=SQLAlchemyError("boom")),
        ):
            with pytest.raises(OrderRepositoryException):
                await order_status_history_repository.save(history)

    @pytest.mark.asyncio
    async def test_should_never_call_commit_on_save(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
        order_status_history_repository: SQLAlchemyOrderStatusHistoryRepositoryAdapter,
    ) -> None:
        """The repository must NEVER call session.commit()."""
        order = OrderEntity.create(
            buyer_id=UUID(faker.uuid4()),
            supplier_id=UUID(faker.uuid4()),
            status_order=OrderStatusEnum.DRAFT,
        )
        await order_repository.save(order)

        history = OrderStatusHistoryEntity.create(
            order_id=order.id,
            previous_status=OrderStatusEnum.DRAFT,
            new_status=OrderStatusEnum.CONFIRMED,
            changed_by=UUID(faker.uuid4()),
            changed_by_role=UserRoleEnum.SUPPLIER,
        )

        with patch.object(
            order_status_history_repository.session,
            "commit",
            new=AsyncMock(),
        ) as mock_commit:
            await order_status_history_repository.save(history)

        mock_commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_never_call_rollback_on_save(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
        order_status_history_repository: SQLAlchemyOrderStatusHistoryRepositoryAdapter,
    ) -> None:
        """The repository must NEVER call session.rollback()."""
        order = OrderEntity.create(
            buyer_id=UUID(faker.uuid4()),
            supplier_id=UUID(faker.uuid4()),
            status_order=OrderStatusEnum.DRAFT,
        )
        await order_repository.save(order)

        history = OrderStatusHistoryEntity.create(
            order_id=order.id,
            previous_status=OrderStatusEnum.DRAFT,
            new_status=OrderStatusEnum.CONFIRMED,
            changed_by=UUID(faker.uuid4()),
            changed_by_role=UserRoleEnum.SUPPLIER,
        )

        with patch.object(
            order_status_history_repository.session,
            "rollback",
            new=AsyncMock(),
        ) as mock_rollback:
            await order_status_history_repository.save(history)

        mock_rollback.assert_not_awaited()
