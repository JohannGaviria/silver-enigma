from uuid import uuid4

import pytest
from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.warehouses.infrastructure.persistence.models.warehouse_model import (
    WarehouseModel,
)
from src.modules.warehouses.infrastructure.persistence.unit_of_work.sqlalchemy_warehouse_lifecycle_unit_of_work_adapter import (
    SQLAlchemyWarehouseLifecycleUnitOfWorkAdapter,
)
from tests.integration.conftest import _make_warehouse_entity


class TestSQLAlchemyWarehouseLifecycleUnitOfWorkAdapter:
    # ------------------------------------------------
    # Commit path
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_commit_persists_warehouse_to_database(
        self,
        faker: Faker,
        db_session: AsyncSession,
        pinned_warehouse_lifecycle_uow: SQLAlchemyWarehouseLifecycleUnitOfWorkAdapter,
    ) -> None:
        """A committed warehouse must be persisted."""
        supplier_id = uuid4()

        warehouse = _make_warehouse_entity(
            faker=faker,
            supplier_id=supplier_id,
        )

        async with pinned_warehouse_lifecycle_uow as u:
            await u.warehouses.save(warehouse)
            await u.commit()

        result = await db_session.execute(
            select(WarehouseModel).where(
                WarehouseModel.supplier_id == supplier_id,
            )
        )

        row = result.scalar_one_or_none()

        assert row is not None
        assert row.supplier_id == supplier_id
        assert row.name == str(warehouse.name)

    @pytest.mark.asyncio
    async def test_committed_warehouse_has_is_active_true(
        self,
        faker: Faker,
        db_session: AsyncSession,
        pinned_warehouse_lifecycle_uow: SQLAlchemyWarehouseLifecycleUnitOfWorkAdapter,
    ) -> None:
        """Committed warehouses must keep is_active=True."""
        supplier_id = uuid4()

        warehouse = _make_warehouse_entity(
            faker=faker,
            supplier_id=supplier_id,
        )

        async with pinned_warehouse_lifecycle_uow as u:
            await u.warehouses.save(warehouse)
            await u.commit()

        result = await db_session.execute(
            select(WarehouseModel).where(
                WarehouseModel.supplier_id == supplier_id,
            )
        )

        row = result.scalar_one_or_none()

        assert row is not None
        assert row.is_active is True

    # ------------------------------------------------
    # Rollback path
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_rollback_discards_unsaved_changes(
        self,
        faker: Faker,
        db_session: AsyncSession,
        pinned_warehouse_lifecycle_uow: SQLAlchemyWarehouseLifecycleUnitOfWorkAdapter,
    ) -> None:
        """Explicit rollback must discard pending changes."""
        supplier_id = uuid4()

        warehouse = _make_warehouse_entity(
            faker=faker,
            supplier_id=supplier_id,
        )

        async with pinned_warehouse_lifecycle_uow as u:
            await u.warehouses.save(warehouse)
            await u.rollback()

        result = await db_session.execute(
            select(WarehouseModel).where(
                WarehouseModel.supplier_id == supplier_id,
            )
        )

        assert result.scalar_one_or_none() is None

    @pytest.mark.asyncio
    async def test_unhandled_exception_triggers_automatic_rollback(
        self,
        faker: Faker,
        db_session: AsyncSession,
        pinned_warehouse_lifecycle_uow: SQLAlchemyWarehouseLifecycleUnitOfWorkAdapter,
    ) -> None:
        """Unhandled exceptions must trigger automatic rollback."""
        supplier_id = uuid4()

        warehouse = _make_warehouse_entity(
            faker=faker,
            supplier_id=supplier_id,
        )

        with pytest.raises(RuntimeError):
            async with pinned_warehouse_lifecycle_uow as u:
                await u.warehouses.save(warehouse)
                raise RuntimeError("boom")

        result = await db_session.execute(
            select(WarehouseModel).where(
                WarehouseModel.supplier_id == supplier_id,
            )
        )

        assert result.scalar_one_or_none() is None

    # ------------------------------------------------
    # Context manager re-use
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_uow_can_be_reused_across_multiple_transactions(
        self,
        faker: Faker,
        db_session: AsyncSession,
        pinned_warehouse_lifecycle_uow: SQLAlchemyWarehouseLifecycleUnitOfWorkAdapter,
    ) -> None:
        """The same UoW instance must support multiple transactions."""
        supplier_id_1 = uuid4()
        supplier_id_2 = uuid4()

        warehouse_1 = _make_warehouse_entity(
            faker=faker,
            supplier_id=supplier_id_1,
        )

        warehouse_2 = _make_warehouse_entity(
            faker=faker,
            supplier_id=supplier_id_2,
        )

        async with pinned_warehouse_lifecycle_uow as u:
            await u.warehouses.save(warehouse_1)
            await u.commit()

        async with pinned_warehouse_lifecycle_uow as u:
            await u.warehouses.save(warehouse_2)
            await u.commit()

        result = await db_session.execute(select(WarehouseModel))

        supplier_ids = {row.supplier_id for row in result.scalars().all()}

        assert supplier_id_1 in supplier_ids
        assert supplier_id_2 in supplier_ids

    # ------------------------------------------------
    # Repository initialization
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_initialize_all_repositories_on_enter(
        self,
        pinned_warehouse_lifecycle_uow: SQLAlchemyWarehouseLifecycleUnitOfWorkAdapter,
    ) -> None:
        """Entering the UoW must initialize all repositories."""
        async with pinned_warehouse_lifecycle_uow as u:
            assert u.warehouses is not None
            assert u.orders_query is not None

    # ------------------------------------------------
    # Guard clauses
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_commit_outside_context_manager_should_raise_runtime_error(
        self,
        pinned_warehouse_lifecycle_uow: SQLAlchemyWarehouseLifecycleUnitOfWorkAdapter,
    ) -> None:
        """Commit outside async-with must fail."""
        with pytest.raises(RuntimeError):
            await pinned_warehouse_lifecycle_uow.commit()

    @pytest.mark.asyncio
    async def test_rollback_outside_context_manager_should_raise_runtime_error(
        self,
        pinned_warehouse_lifecycle_uow: SQLAlchemyWarehouseLifecycleUnitOfWorkAdapter,
    ) -> None:
        """Rollback outside async-with must fail."""
        with pytest.raises(RuntimeError):
            await pinned_warehouse_lifecycle_uow.rollback()
