from decimal import Decimal
from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
from faker import Faker
from sqlalchemy.exc import SQLAlchemyError

from src.modules.orders.domain.entities.inventory_allocation_entity import (
    InventoryAllocationEntity,
)
from src.modules.orders.domain.entities.order_entity import OrderEntity
from src.modules.orders.domain.entities.order_items_entity import OrderItemsEntity
from src.modules.orders.domain.exceptions.order_exception import (
    OrderRepositoryException,
)
from src.modules.orders.domain.value_objects.quantity_vo import QuantityVO
from src.modules.orders.infrastructure.persistence.repositories.sqlalchemy_inventory_allocation_repository_adapter import (
    SQLAlchemyInventoryAllocationRepositoryAdapter,
)
from src.modules.orders.infrastructure.persistence.repositories.sqlalchemy_order_items_repository_adapter import (
    SQLAlchemyOrderItemsRepositoryAdapter,
)
from src.modules.orders.infrastructure.persistence.repositories.sqlalchemy_order_repository_adapter import (
    SQLAlchemyOrderRepositoryAdapter,
)
from src.shared.domain.enums.order_status_enum import OrderStatusEnum


class TestSQLAlchemyInventoryAllocationRepositoryAdapter:
    # ---------------------------------------------------------------------------
    # helpers
    # ---------------------------------------------------------------------------

    @staticmethod
    async def _make_order_item(
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
        order_items_repository: SQLAlchemyOrderItemsRepositoryAdapter,
    ) -> OrderItemsEntity:
        """Helper to persist an order and a single order item, returning the item."""
        order = OrderEntity.create(
            buyer_id=UUID(faker.uuid4()),
            supplier_id=UUID(faker.uuid4()),
            status_order=OrderStatusEnum.DRAFT,
        )
        await order_repository.save(order)

        item = OrderItemsEntity.create(
            order_id=order.id,
            product_id=UUID(faker.uuid4()),
            quantity=QuantityVO(faker.random_int(min=1, max=10)),
            unit_price=Decimal(str(faker.random_int(min=100, max=9999))),
        )
        await order_items_repository.save_many([item])

        return item

    # ---------------------------------------------------------------------------
    # save_many
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_save_multiple_inventory_allocations_successfully(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
        order_items_repository: SQLAlchemyOrderItemsRepositoryAdapter,
        inventory_allocation_repository: SQLAlchemyInventoryAllocationRepositoryAdapter,
    ) -> None:
        """save_many() must persist all allocations without errors."""
        item = await self._make_order_item(
            faker, order_repository, order_items_repository
        )

        allocations = [
            InventoryAllocationEntity.create(
                order_item_id=item.id,
                warehouse_id=UUID(faker.uuid4()),
                quantity=QuantityVO(faker.random_int(min=1, max=10)),
            )
            for _ in range(3)
        ]

        await inventory_allocation_repository.save_many(allocations)

    @pytest.mark.asyncio
    async def test_should_save_single_allocation_list(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
        order_items_repository: SQLAlchemyOrderItemsRepositoryAdapter,
        inventory_allocation_repository: SQLAlchemyInventoryAllocationRepositoryAdapter,
    ) -> None:
        """save_many() must work correctly with a single-element list."""
        item = await self._make_order_item(
            faker, order_repository, order_items_repository
        )

        allocation = InventoryAllocationEntity.create(
            order_item_id=item.id,
            warehouse_id=UUID(faker.uuid4()),
            quantity=QuantityVO(2),
        )

        await inventory_allocation_repository.save_many([allocation])

    @pytest.mark.asyncio
    async def test_should_assign_unique_ids_to_each_allocation(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
        order_items_repository: SQLAlchemyOrderItemsRepositoryAdapter,
        inventory_allocation_repository: SQLAlchemyInventoryAllocationRepositoryAdapter,
    ) -> None:
        """Each saved allocation must have a unique ID."""
        item = await self._make_order_item(
            faker, order_repository, order_items_repository
        )

        allocations = [
            InventoryAllocationEntity.create(
                order_item_id=item.id,
                warehouse_id=UUID(faker.uuid4()),
                quantity=QuantityVO(faker.random_int(min=1, max=5)),
            )
            for _ in range(3)
        ]

        await inventory_allocation_repository.save_many(allocations)

        ids = [allocation.id for allocation in allocations]
        assert len(set(ids)) == len(ids)

    @pytest.mark.asyncio
    async def test_should_save_multiple_allocations_for_same_order_item_across_warehouses(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
        order_items_repository: SQLAlchemyOrderItemsRepositoryAdapter,
        inventory_allocation_repository: SQLAlchemyInventoryAllocationRepositoryAdapter,
    ) -> None:
        """A single order item split across multiple warehouses must be persisted (ADR-013)."""
        item = await self._make_order_item(
            faker, order_repository, order_items_repository
        )

        allocations = [
            InventoryAllocationEntity.create(
                order_item_id=item.id,
                warehouse_id=UUID(faker.uuid4()),
                quantity=QuantityVO(2),
            )
            for _ in range(2)
        ]

        await inventory_allocation_repository.save_many(allocations)

        assert all(allocation.order_item_id == item.id for allocation in allocations)
        warehouse_ids = {allocation.warehouse_id for allocation in allocations}
        assert len(warehouse_ids) == 2

    @pytest.mark.asyncio
    async def test_should_raise_order_repository_exception_when_flush_fails_in_save_many(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
        order_items_repository: SQLAlchemyOrderItemsRepositoryAdapter,
        inventory_allocation_repository: SQLAlchemyInventoryAllocationRepositoryAdapter,
    ) -> None:
        """OrderRepositoryException must be raised when session.flush fails."""
        item = await self._make_order_item(
            faker, order_repository, order_items_repository
        )

        allocations = [
            InventoryAllocationEntity.create(
                order_item_id=item.id,
                warehouse_id=UUID(faker.uuid4()),
                quantity=QuantityVO(1),
            )
        ]

        with patch.object(
            inventory_allocation_repository.session,
            "flush",
            new=AsyncMock(side_effect=SQLAlchemyError("boom")),
        ):
            with pytest.raises(OrderRepositoryException):
                await inventory_allocation_repository.save_many(allocations)

    @pytest.mark.asyncio
    async def test_should_never_call_commit_on_save_many(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
        order_items_repository: SQLAlchemyOrderItemsRepositoryAdapter,
        inventory_allocation_repository: SQLAlchemyInventoryAllocationRepositoryAdapter,
    ) -> None:
        """The repository must NEVER call session.commit()."""
        item = await self._make_order_item(
            faker, order_repository, order_items_repository
        )

        allocations = [
            InventoryAllocationEntity.create(
                order_item_id=item.id,
                warehouse_id=UUID(faker.uuid4()),
                quantity=QuantityVO(1),
            )
        ]

        with patch.object(
            inventory_allocation_repository.session,
            "commit",
            new=AsyncMock(),
        ) as mock_commit:
            await inventory_allocation_repository.save_many(allocations)

        mock_commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_never_call_rollback_on_save_many(
        self,
        faker: Faker,
        order_repository: SQLAlchemyOrderRepositoryAdapter,
        order_items_repository: SQLAlchemyOrderItemsRepositoryAdapter,
        inventory_allocation_repository: SQLAlchemyInventoryAllocationRepositoryAdapter,
    ) -> None:
        """The repository must NEVER call session.rollback()."""
        item = await self._make_order_item(
            faker, order_repository, order_items_repository
        )

        allocations = [
            InventoryAllocationEntity.create(
                order_item_id=item.id,
                warehouse_id=UUID(faker.uuid4()),
                quantity=QuantityVO(1),
            )
        ]

        with patch.object(
            inventory_allocation_repository.session,
            "rollback",
            new=AsyncMock(),
        ) as mock_rollback:
            await inventory_allocation_repository.save_many(allocations)

        mock_rollback.assert_not_awaited()
