from decimal import Decimal
from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
from faker import Faker
from sqlalchemy.exc import SQLAlchemyError

from src.modules.orders.domain.entities.order_entity import OrderEntity
from src.modules.orders.domain.entities.order_items_entity import OrderItemsEntity
from src.modules.orders.domain.exceptions.order_exception import (
    OrderRepositoryException,
)
from src.modules.orders.domain.value_objects.quantity_vo import QuantityVO
from src.modules.orders.infrastructure.persistence.repositories.sqlalchemy_order_items_repository_adapter import (
    SQLAlchemyOrderItemsRepositoryAdapter,
)
from src.modules.orders.infrastructure.persistence.repositories.sqlalchemy_order_repository_adapter import (
    SQLAlchemyOrderRepositoryAdapter,
)
from src.shared.domain.enums.order_status_enum import OrderStatusEnum


class TestSQLAlchemyOrderItemsRepositoryAdapter:
    # ---------------------------------------------------------------------------
    # save_many
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_save_multiple_order_items_successfully(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
        order_items_repository: SQLAlchemyOrderItemsRepositoryAdapter,
    ) -> None:
        """save_many() must persist all items without errors."""
        order = OrderEntity.create(
            buyer_id=UUID(faker.uuid4()),
            supplier_id=UUID(faker.uuid4()),
            status_order=OrderStatusEnum.DRAFT,
        )
        await order_repository.save(order)

        items = [
            OrderItemsEntity.create(
                order_id=order.id,
                product_id=UUID(faker.uuid4()),
                quantity=QuantityVO(faker.random_int(min=1, max=10)),
                unit_price=Decimal(str(faker.random_int(min=100, max=9999))),
            )
            for _ in range(3)
        ]

        await order_items_repository.save_many(items)

    @pytest.mark.asyncio
    async def test_should_save_single_item_list(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
        order_items_repository: SQLAlchemyOrderItemsRepositoryAdapter,
    ) -> None:
        """save_many() must work correctly with a single-element list."""
        order = OrderEntity.create(
            buyer_id=UUID(faker.uuid4()),
            supplier_id=UUID(faker.uuid4()),
            status_order=OrderStatusEnum.DRAFT,
        )
        await order_repository.save(order)

        item = OrderItemsEntity.create(
            order_id=order.id,
            product_id=UUID(faker.uuid4()),
            quantity=QuantityVO(2),
            unit_price=Decimal("500.00"),
        )

        await order_items_repository.save_many([item])

    @pytest.mark.asyncio
    async def test_should_assign_unique_ids_to_each_item(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
        order_items_repository: SQLAlchemyOrderItemsRepositoryAdapter,
    ) -> None:
        """Each saved item must have a unique ID."""
        order = OrderEntity.create(
            buyer_id=UUID(faker.uuid4()),
            supplier_id=UUID(faker.uuid4()),
            status_order=OrderStatusEnum.DRAFT,
        )
        await order_repository.save(order)

        items = [
            OrderItemsEntity.create(
                order_id=order.id,
                product_id=UUID(faker.uuid4()),
                quantity=QuantityVO(faker.random_int(min=1, max=5)),
                unit_price=Decimal("100.00"),
            )
            for _ in range(3)
        ]

        await order_items_repository.save_many(items)

        ids = [item.id for item in items]
        assert len(set(ids)) == len(ids)

    @pytest.mark.asyncio
    async def test_should_raise_order_repository_exception_when_flush_fails_in_save_many(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
        order_items_repository: SQLAlchemyOrderItemsRepositoryAdapter,
    ) -> None:
        """OrderRepositoryException must be raised when session.flush fails."""
        order = OrderEntity.create(
            buyer_id=UUID(faker.uuid4()),
            supplier_id=UUID(faker.uuid4()),
            status_order=OrderStatusEnum.DRAFT,
        )
        await order_repository.save(order)

        items = [
            OrderItemsEntity.create(
                order_id=order.id,
                product_id=UUID(faker.uuid4()),
                quantity=QuantityVO(1),
                unit_price=Decimal("100.00"),
            )
        ]

        with patch.object(
            order_items_repository.session,
            "flush",
            new=AsyncMock(side_effect=SQLAlchemyError("boom")),
        ):
            with pytest.raises(OrderRepositoryException):
                await order_items_repository.save_many(items)

    @pytest.mark.asyncio
    async def test_should_never_call_commit_on_save_many(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
        order_items_repository: SQLAlchemyOrderItemsRepositoryAdapter,
    ) -> None:
        """The repository must NEVER call session.commit()."""
        order = OrderEntity.create(
            buyer_id=UUID(faker.uuid4()),
            supplier_id=UUID(faker.uuid4()),
            status_order=OrderStatusEnum.DRAFT,
        )
        await order_repository.save(order)

        items = [
            OrderItemsEntity.create(
                order_id=order.id,
                product_id=UUID(faker.uuid4()),
                quantity=QuantityVO(1),
                unit_price=Decimal("100.00"),
            )
        ]

        with patch.object(
            order_items_repository.session,
            "commit",
            new=AsyncMock(),
        ) as mock_commit:
            await order_items_repository.save_many(items)

        mock_commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_never_call_rollback_on_save_many(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
        order_items_repository: SQLAlchemyOrderItemsRepositoryAdapter,
    ) -> None:
        """The repository must NEVER call session.rollback()."""
        order = OrderEntity.create(
            buyer_id=UUID(faker.uuid4()),
            supplier_id=UUID(faker.uuid4()),
            status_order=OrderStatusEnum.DRAFT,
        )
        await order_repository.save(order)

        items = [
            OrderItemsEntity.create(
                order_id=order.id,
                product_id=UUID(faker.uuid4()),
                quantity=QuantityVO(1),
                unit_price=Decimal("100.00"),
            )
        ]

        with patch.object(
            order_items_repository.session,
            "rollback",
            new=AsyncMock(),
        ) as mock_rollback:
            await order_items_repository.save_many(items)

        mock_rollback.assert_not_awaited()
