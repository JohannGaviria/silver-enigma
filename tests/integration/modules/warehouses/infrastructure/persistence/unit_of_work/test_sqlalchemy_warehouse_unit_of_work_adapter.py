from uuid import UUID, uuid4

import pytest
from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.warehouses.domain.entities.warehouse_entity import WarehouseEntity
from src.modules.warehouses.domain.value_objects.warehouse_address_vo import (
    WarehouseAddressVO,
)
from src.modules.warehouses.domain.value_objects.warehouse_name_vo import (
    WarehouseNameVO,
)
from src.modules.warehouses.infrastructure.persistence.models.warehouse_model import (
    WarehouseModel,
)
from src.modules.warehouses.infrastructure.persistence.unit_of_work.sqlalchemy_warehouse_unit_of_work_adapter import (
    SQLAlchemyWarehouseUnitOfWorkAdapter,
)


class TestSQLAlchemyWarehouseUnitOfWorkAdapter:
    # ------------------------------------------------
    # Commit path
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_commit_persists_warehouse_to_database(
        self,
        faker: Faker,
        db_session: AsyncSession,
        pinned_warehouse_uow: SQLAlchemyWarehouseUnitOfWorkAdapter,
    ) -> None:
        """A warehouse saved and committed inside the UoW must be visible in the session."""
        supplier_id = UUID(faker.uuid4())
        name = faker.company()
        entity = WarehouseEntity.create(
            supplier_id=supplier_id,
            name=WarehouseNameVO(name),
            address=WarehouseAddressVO(faker.address()),
        )

        async with pinned_warehouse_uow as u:
            await u.warehouses.save(entity)
            await u.commit()

        result = await db_session.execute(
            select(WarehouseModel).where(WarehouseModel.supplier_id == supplier_id)
        )
        row = result.scalar_one_or_none()

        assert row is not None
        assert str(row.name) == name
        assert row.supplier_id == supplier_id

    @pytest.mark.asyncio
    async def test_committed_warehouse_has_is_active_true(
        self,
        faker: Faker,
        db_session: AsyncSession,
        pinned_warehouse_uow: SQLAlchemyWarehouseUnitOfWorkAdapter,
    ) -> None:
        """A committed warehouse must have is_active set to True in the database."""
        supplier_id = UUID(faker.uuid4())
        entity = WarehouseEntity.create(
            supplier_id=supplier_id,
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )

        async with pinned_warehouse_uow as u:
            await u.warehouses.save(entity)
            await u.commit()

        result = await db_session.execute(
            select(WarehouseModel).where(WarehouseModel.supplier_id == supplier_id)
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
        pinned_warehouse_uow: SQLAlchemyWarehouseUnitOfWorkAdapter,
    ) -> None:
        """A warehouse saved but rolled back must NOT appear in the database."""
        supplier_id = UUID(faker.uuid4())
        entity = WarehouseEntity.create(
            supplier_id=supplier_id,
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )

        async with pinned_warehouse_uow as u:
            await u.warehouses.save(entity)
            await u.rollback()

        result = await db_session.execute(
            select(WarehouseModel).where(WarehouseModel.supplier_id == supplier_id)
        )
        assert result.scalar_one_or_none() is None

    @pytest.mark.asyncio
    async def test_unhandled_exception_triggers_automatic_rollback(
        self,
        faker: Faker,
        db_session: AsyncSession,
        pinned_warehouse_uow: SQLAlchemyWarehouseUnitOfWorkAdapter,
    ) -> None:
        """An unhandled exception inside the UoW block must roll back automatically."""
        supplier_id = UUID(faker.uuid4())
        entity = WarehouseEntity.create(
            supplier_id=supplier_id,
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )

        with pytest.raises(RuntimeError):
            async with pinned_warehouse_uow as u:
                await u.warehouses.save(entity)
                raise RuntimeError("something went wrong")

        result = await db_session.execute(
            select(WarehouseModel).where(WarehouseModel.supplier_id == supplier_id)
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
        pinned_warehouse_uow: SQLAlchemyWarehouseUnitOfWorkAdapter,
    ) -> None:
        """The same UoW instance must work correctly when used more than once."""
        supplier_id_1 = uuid4()
        supplier_id_2 = uuid4()

        entity1 = WarehouseEntity.create(
            supplier_id=supplier_id_1,
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )
        entity2 = WarehouseEntity.create(
            supplier_id=supplier_id_2,
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )

        async with pinned_warehouse_uow as u:
            await u.warehouses.save(entity1)
            await u.commit()

        async with pinned_warehouse_uow as u:
            await u.warehouses.save(entity2)
            await u.commit()

        result = await db_session.execute(select(WarehouseModel))
        supplier_ids = {r.supplier_id for r in result.scalars().all()}

        assert supplier_id_1 in supplier_ids
        assert supplier_id_2 in supplier_ids
