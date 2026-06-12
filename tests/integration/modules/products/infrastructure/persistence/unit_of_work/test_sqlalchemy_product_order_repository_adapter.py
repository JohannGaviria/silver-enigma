from decimal import Decimal
from uuid import uuid4

import pytest
from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.products.domain.entities.product_entity import ProductEntity
from src.modules.products.domain.enums.unit_of_measure_enum import UnitOfMeasureEnum
from src.modules.products.domain.value_objects.product_name_vo import ProductNameVO
from src.modules.products.domain.value_objects.unit_price_vo import UnitPriceVO
from src.modules.products.infrastructure.persistence.models.product_model import (
    ProductModel,
)
from src.modules.products.infrastructure.persistence.unit_of_work.sqlalchemy_product_lifecycle_unit_of_work_adapter import (
    SQLAlchemyProductLifecycleUnitOfWorkAdapter,
)


class TestSQLAlchemyProductLifecycleUnitOfWorkAdapter:
    # ------------------------------------------------
    # Commit path
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_commit_persists_product_and_order_query_is_available(
        self,
        faker: Faker,
        db_session: AsyncSession,
        pinned_product_lifecycle_uow: SQLAlchemyProductLifecycleUnitOfWorkAdapter,
    ) -> None:
        supplier_id = uuid4()

        product = ProductEntity.create(
            supplier_id=supplier_id,
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("1000")),
        )

        async with pinned_product_lifecycle_uow as u:
            await u.products.save(product)
            await u.commit()

            # repos must be initialized
            assert u.products is not None
            assert u.orders_query is not None

        result = await db_session.execute(
            select(ProductModel).where(ProductModel.supplier_id == supplier_id)
        )

        row = result.scalar_one_or_none()

        assert row is not None
        assert row.supplier_id == supplier_id
        assert row.name == str(product.name)
        assert row.is_active is True

    # ------------------------------------------------
    # Rollback path (explicit)
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_explicit_rollback_discards_changes(
        self,
        faker: Faker,
        db_session: AsyncSession,
        pinned_product_lifecycle_uow: SQLAlchemyProductLifecycleUnitOfWorkAdapter,
    ) -> None:
        supplier_id = uuid4()

        product = ProductEntity.create(
            supplier_id=supplier_id,
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("1000")),
        )

        async with pinned_product_lifecycle_uow as u:
            await u.products.save(product)
            await u.rollback()

        result = await db_session.execute(
            select(ProductModel).where(ProductModel.supplier_id == supplier_id)
        )

        assert result.scalar_one_or_none() is None

    # ------------------------------------------------
    # Rollback path (exception)
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_unhandled_exception_triggers_rollback(
        self,
        faker: Faker,
        db_session: AsyncSession,
        pinned_product_lifecycle_uow: SQLAlchemyProductLifecycleUnitOfWorkAdapter,
    ) -> None:
        supplier_id = uuid4()

        product = ProductEntity.create(
            supplier_id=supplier_id,
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("1000")),
        )

        with pytest.raises(RuntimeError):
            async with pinned_product_lifecycle_uow as u:
                await u.products.save(product)
                raise RuntimeError("boom")

        result = await db_session.execute(
            select(ProductModel).where(ProductModel.supplier_id == supplier_id)
        )

        assert result.scalar_one_or_none() is None

    # ------------------------------------------------
    # Reusability
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_uow_can_be_reused_multiple_times(
        self,
        faker: Faker,
        db_session: AsyncSession,
        pinned_product_lifecycle_uow: SQLAlchemyProductLifecycleUnitOfWorkAdapter,
    ) -> None:
        supplier_id_1 = uuid4()
        supplier_id_2 = uuid4()

        product_1 = ProductEntity.create(
            supplier_id=supplier_id_1,
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("1000")),
        )

        product_2 = ProductEntity.create(
            supplier_id=supplier_id_2,
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("2000")),
        )

        async with pinned_product_lifecycle_uow as u:
            await u.products.save(product_1)
            await u.commit()

        async with pinned_product_lifecycle_uow as u:
            await u.products.save(product_2)
            await u.commit()

        result = await db_session.execute(select(ProductModel))
        supplier_ids = {row.supplier_id for row in result.scalars().all()}

        assert supplier_id_1 in supplier_ids
        assert supplier_id_2 in supplier_ids

    # ------------------------------------------------
    # Repository initialization
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_repositories_are_initialized_on_enter(
        self,
        pinned_product_lifecycle_uow: SQLAlchemyProductLifecycleUnitOfWorkAdapter,
    ) -> None:
        async with pinned_product_lifecycle_uow as u:
            assert u.products is not None
            assert u.orders_query is not None

    # ------------------------------------------------
    # Guard clauses
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_commit_outside_context_raises(
        self,
        pinned_product_lifecycle_uow: SQLAlchemyProductLifecycleUnitOfWorkAdapter,
    ) -> None:
        with pytest.raises(RuntimeError):
            await pinned_product_lifecycle_uow.commit()

    @pytest.mark.asyncio
    async def test_rollback_outside_context_raises(
        self,
        pinned_product_lifecycle_uow: SQLAlchemyProductLifecycleUnitOfWorkAdapter,
    ) -> None:
        with pytest.raises(RuntimeError):
            await pinned_product_lifecycle_uow.rollback()
