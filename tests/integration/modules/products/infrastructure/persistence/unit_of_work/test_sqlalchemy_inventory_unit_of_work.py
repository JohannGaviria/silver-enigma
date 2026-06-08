from decimal import Decimal
from uuid import uuid4

import pytest
from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.products.domain.entities.product_entity import ProductEntity
from src.modules.products.domain.enums.unit_of_measure_enum import (
    UnitOfMeasureEnum,
)
from src.modules.products.domain.value_objects.product_name_vo import (
    ProductNameVO,
)
from src.modules.products.domain.value_objects.unit_price_vo import (
    UnitPriceVO,
)
from src.modules.products.infrastructure.persistence.models.product_model import (
    ProductModel,
)
from src.modules.products.infrastructure.persistence.unit_of_work.sqlalchemy_inventory_unit_of_work_adapter import (
    SQLAlchemyInventoryUnitOfWorkAdapter,
)


class TestSQLAlchemyInventoryUnitOfWorkAdapter:
    # ------------------------------------------------
    # Commit path
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_commit_persists_product_to_database(
        self,
        faker: Faker,
        db_session: AsyncSession,
        pinned_inventory_uow: SQLAlchemyInventoryUnitOfWorkAdapter,
    ) -> None:
        """A committed product must be persisted."""
        supplier_id = uuid4()

        product = ProductEntity.create(
            supplier_id=supplier_id,
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("1000")),
        )

        async with pinned_inventory_uow as u:
            await u.products.save(product)
            await u.commit()

        result = await db_session.execute(
            select(ProductModel).where(
                ProductModel.supplier_id == supplier_id,
            )
        )

        row = result.scalar_one_or_none()

        assert row is not None
        assert row.supplier_id == supplier_id
        assert row.name == str(product.name)

    @pytest.mark.asyncio
    async def test_committed_product_has_is_active_true(
        self,
        faker: Faker,
        db_session: AsyncSession,
        pinned_inventory_uow: SQLAlchemyInventoryUnitOfWorkAdapter,
    ) -> None:
        """Committed products must keep is_active=True."""
        supplier_id = uuid4()

        product = ProductEntity.create(
            supplier_id=supplier_id,
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("1000")),
        )

        async with pinned_inventory_uow as u:
            await u.products.save(product)
            await u.commit()

        result = await db_session.execute(
            select(ProductModel).where(
                ProductModel.supplier_id == supplier_id,
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
        pinned_inventory_uow: SQLAlchemyInventoryUnitOfWorkAdapter,
    ) -> None:
        """Explicit rollback must discard pending changes."""
        supplier_id = uuid4()

        product = ProductEntity.create(
            supplier_id=supplier_id,
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("1000")),
        )

        async with pinned_inventory_uow as u:
            await u.products.save(product)
            await u.rollback()

        result = await db_session.execute(
            select(ProductModel).where(
                ProductModel.supplier_id == supplier_id,
            )
        )

        assert result.scalar_one_or_none() is None

    @pytest.mark.asyncio
    async def test_unhandled_exception_triggers_automatic_rollback(
        self,
        faker: Faker,
        db_session: AsyncSession,
        pinned_inventory_uow: SQLAlchemyInventoryUnitOfWorkAdapter,
    ) -> None:
        """Unhandled exceptions must trigger automatic rollback."""
        supplier_id = uuid4()

        product = ProductEntity.create(
            supplier_id=supplier_id,
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("1000")),
        )

        with pytest.raises(RuntimeError):
            async with pinned_inventory_uow as u:
                await u.products.save(product)
                raise RuntimeError("boom")

        result = await db_session.execute(
            select(ProductModel).where(
                ProductModel.supplier_id == supplier_id,
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
        pinned_inventory_uow: SQLAlchemyInventoryUnitOfWorkAdapter,
    ) -> None:
        """The same Inventory UoW instance must support multiple transactions."""
        supplier_id_1 = uuid4()
        supplier_id_2 = uuid4()

        product1 = ProductEntity.create(
            supplier_id=supplier_id_1,
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("1000")),
        )

        product2 = ProductEntity.create(
            supplier_id=supplier_id_2,
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("2000")),
        )

        async with pinned_inventory_uow as u:
            await u.products.save(product1)
            await u.commit()

        async with pinned_inventory_uow as u:
            await u.products.save(product2)
            await u.commit()

        result = await db_session.execute(select(ProductModel))

        supplier_ids = {row.supplier_id for row in result.scalars().all()}

        assert supplier_id_1 in supplier_ids
        assert supplier_id_2 in supplier_ids

    # ------------------------------------------------
    # Repository initialization
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_initialize_all_repositories_on_enter(
        self,
        pinned_inventory_uow: SQLAlchemyInventoryUnitOfWorkAdapter,
    ) -> None:
        """Entering the UoW must initialize all repositories."""
        async with pinned_inventory_uow as u:
            assert u.products is not None
            assert u.warehouses is not None
            assert u.stocks is not None
            assert u.inventory_movements is not None
