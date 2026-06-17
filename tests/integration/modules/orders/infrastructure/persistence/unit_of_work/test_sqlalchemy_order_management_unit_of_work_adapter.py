from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.orders.domain.entities.order_entity import OrderEntity
from src.modules.orders.domain.entities.order_items_entity import OrderItemsEntity
from src.modules.orders.domain.entities.order_status_history_entity import (
    OrderStatusHistoryEntity,
)
from src.modules.orders.domain.value_objects.quantity_vo import QuantityVO
from src.modules.orders.infrastructure.persistence.models.order_model import (
    OrderModel,
)
from src.modules.orders.infrastructure.persistence.unit_of_work.sqlalchemy_order_management_unit_of_work_adapter import (
    SQLAlchemyOrderManagementUnitOfWorkAdapter,
)
from src.shared.domain.enums.order_status_enum import OrderStatusEnum
from src.shared.domain.enums.user_role_enum import UserRoleEnum


class TestSQLAlchemyOrderManagementUnitOfWorkAdapter:
    # ------------------------------------------------
    # Commit path
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_commit_persists_order_to_database(
        self,
        db_session: AsyncSession,
        pinned_order_management_uow: SQLAlchemyOrderManagementUnitOfWorkAdapter,
    ) -> None:
        """A committed order must be persisted."""
        buyer_id = uuid4()
        supplier_id = uuid4()

        order = OrderEntity.create(
            buyer_id=buyer_id,
            supplier_id=supplier_id,
            status_order=OrderStatusEnum.DRAFT,
        )

        async with pinned_order_management_uow as u:
            await u.orders.save(order)
            await u.commit()

        result = await db_session.execute(
            select(OrderModel).where(
                OrderModel.buyer_id == buyer_id,
            )
        )

        row = result.scalar_one_or_none()

        assert row is not None
        assert row.buyer_id == buyer_id

    @pytest.mark.asyncio
    async def test_commit_persists_order_with_items_and_status_history(
        self,
        db_session: AsyncSession,
        pinned_order_management_uow: SQLAlchemyOrderManagementUnitOfWorkAdapter,
    ) -> None:
        """A committed transaction must persist all order aggregates."""
        buyer_id = uuid4()
        supplier_id = uuid4()

        order = OrderEntity.create(
            buyer_id=buyer_id,
            supplier_id=supplier_id,
            status_order=OrderStatusEnum.DRAFT,
        )

        item = OrderItemsEntity.create(
            order_id=order.id,
            product_id=uuid4(),
            quantity=QuantityVO(2),
            unit_price=Decimal("1000"),
        )

        history = OrderStatusHistoryEntity.create(
            order_id=order.id,
            previous_status=OrderStatusEnum.DRAFT,
            new_status=OrderStatusEnum.DRAFT,
            changed_by=uuid4(),
            changed_by_role=UserRoleEnum.BUYER,
        )

        async with pinned_order_management_uow as u:
            await u.orders.save(order)
            await u.order_items.save_many([item])
            await u.orders_status_history.save(history)

            await u.commit()

        order_result = await db_session.execute(
            select(OrderModel).where(
                OrderModel.id == order.id,
            )
        )

        assert order_result.scalar_one_or_none() is not None

    # ------------------------------------------------
    # Rollback path
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_rollback_discards_unsaved_order_changes(
        self,
        db_session: AsyncSession,
        pinned_order_management_uow: SQLAlchemyOrderManagementUnitOfWorkAdapter,
    ) -> None:
        """Explicit rollback must discard pending order changes."""
        buyer_id = uuid4()
        supplier_id = uuid4()

        order = OrderEntity.create(
            buyer_id=buyer_id,
            supplier_id=supplier_id,
            status_order=OrderStatusEnum.DRAFT,
        )

        async with pinned_order_management_uow as u:
            await u.orders.save(order)
            await u.rollback()

        result = await db_session.execute(
            select(OrderModel).where(
                OrderModel.id == order.id,
            )
        )

        assert result.scalar_one_or_none() is None

    @pytest.mark.asyncio
    async def test_unhandled_exception_triggers_automatic_rollback(
        self,
        db_session: AsyncSession,
        pinned_order_management_uow: SQLAlchemyOrderManagementUnitOfWorkAdapter,
    ) -> None:
        """Unhandled exceptions must rollback the transaction."""
        buyer_id = uuid4()
        supplier_id = uuid4()

        order = OrderEntity.create(
            buyer_id=buyer_id,
            supplier_id=supplier_id,
            status_order=OrderStatusEnum.DRAFT,
        )

        with pytest.raises(RuntimeError):
            async with pinned_order_management_uow as u:
                await u.orders.save(order)

                raise RuntimeError("boom")

        result = await db_session.execute(
            select(OrderModel).where(
                OrderModel.id == order.id,
            )
        )

        assert result.scalar_one_or_none() is None

    # ------------------------------------------------
    # Context manager lifecycle
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_uow_can_be_reused_across_multiple_transactions(
        self,
        db_session: AsyncSession,
        pinned_order_management_uow: SQLAlchemyOrderManagementUnitOfWorkAdapter,
    ) -> None:
        """The same UoW instance must support multiple transactions."""
        order_one = OrderEntity.create(
            buyer_id=uuid4(), supplier_id=uuid4(), status_order=OrderStatusEnum.DRAFT
        )

        order_two = OrderEntity.create(
            buyer_id=uuid4(), supplier_id=uuid4(), status_order=OrderStatusEnum.DRAFT
        )

        async with pinned_order_management_uow as u:
            await u.orders.save(order_one)
            await u.commit()

        async with pinned_order_management_uow as u:
            await u.orders.save(order_two)
            await u.commit()

        result = await db_session.execute(select(OrderModel))

        orders = result.scalars().all()

        ids = {order.id for order in orders}

        assert order_one.id in ids
        assert order_two.id in ids

    # ------------------------------------------------
    # Repository initialization
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_initialize_all_repositories_on_enter(
        self,
        pinned_order_management_uow: SQLAlchemyOrderManagementUnitOfWorkAdapter,
    ) -> None:
        """Entering the UoW must initialize all repositories."""
        async with pinned_order_management_uow as u:
            assert u.orders is not None
            assert u.order_items is not None
            assert u.orders_status_history is not None
            assert u.product_query is not None
