"""Integration tests for SQLAlchemyProductQueryRepositoryAdapter."""

from decimal import Decimal
from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
from faker import Faker
from sqlalchemy.exc import SQLAlchemyError

from src.modules.orders.domain.exceptions.order_exception import (
    OrderRepositoryException,
)
from src.modules.orders.domain.value_objects.referenced_product_vo import (
    ReferencedProductVO,
)
from src.modules.products.domain.entities.product_entity import ProductEntity
from src.modules.products.domain.enums.unit_of_measure_enum import UnitOfMeasureEnum
from src.modules.products.domain.value_objects.product_name_vo import ProductNameVO
from src.modules.products.domain.value_objects.unit_price_vo import UnitPriceVO
from src.modules.products.infrastructure.persistence.repositories.sqlalchemy_product_query_repository_adapter import (
    SQLAlchemyProductQueryRepositoryAdapter,
)
from src.modules.products.infrastructure.persistence.repositories.sqlalchemy_product_repository_adapter import (
    SQLAlchemyProductRepositoryAdapter,
)


class TestSQLAlchemyProductQueryRepositoryAdapter:
    # ---------------------------------------------------------------------------
    # find_by_ids — happy paths
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_return_referenced_product_vo_for_existing_product(
        self,
        faker: Faker,
        product_repository: SQLAlchemyProductRepositoryAdapter,
        product_query_repository: SQLAlchemyProductQueryRepositoryAdapter,
    ) -> None:
        """find_by_ids() must return a ReferencedProductVO for each existing product."""
        product = ProductEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("750.00")),
        )
        await product_repository.save(product)

        result = await product_query_repository.find_by_ids([product.id])

        assert len(result) == 1
        vo = result[0]
        assert isinstance(vo, ReferencedProductVO)
        assert vo.product_id == product.id
        assert vo.supplier_id == product.supplier_id
        assert vo.name == str(product.name)
        assert vo.unit_price == product.unit_price.value()
        assert vo.is_active is True

    @pytest.mark.asyncio
    async def test_should_return_multiple_vos_for_multiple_existing_products(
        self,
        faker: Faker,
        product_repository: SQLAlchemyProductRepositoryAdapter,
        product_query_repository: SQLAlchemyProductQueryRepositoryAdapter,
    ) -> None:
        """find_by_ids() must return one VO per requested product that exists."""
        supplier_id = UUID(faker.uuid4())

        products = [
            ProductEntity.create(
                supplier_id=supplier_id,
                name=ProductNameVO(faker.company()),
                description=faker.text(),
                unit_of_measure=UnitOfMeasureEnum.UNIT,
                unit_price=UnitPriceVO(Decimal(str(faker.random_int(100, 9999)))),
            )
            for _ in range(3)
        ]
        for p in products:
            await product_repository.save(p)

        ids = [p.id for p in products]
        result = await product_query_repository.find_by_ids(ids)

        assert len(result) == 3
        returned_ids = {vo.product_id for vo in result}
        assert returned_ids == set(ids)

    @pytest.mark.asyncio
    async def test_should_omit_products_that_do_not_exist(
        self,
        faker: Faker,
        product_repository: SQLAlchemyProductRepositoryAdapter,
        product_query_repository: SQLAlchemyProductQueryRepositoryAdapter,
    ) -> None:
        """Products not found in DB must be silently omitted from the result."""
        product = ProductEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("100.00")),
        )
        await product_repository.save(product)

        ghost_id = UUID(faker.uuid4())
        result = await product_query_repository.find_by_ids([product.id, ghost_id])

        assert len(result) == 1
        assert result[0].product_id == product.id

    @pytest.mark.asyncio
    async def test_should_return_empty_list_when_no_ids_provided(
        self,
        product_query_repository: SQLAlchemyProductQueryRepositoryAdapter,
    ) -> None:
        """find_by_ids() must return an empty list without hitting the database."""
        result = await product_query_repository.find_by_ids([])

        assert result == []

    @pytest.mark.asyncio
    async def test_should_return_empty_list_when_no_products_match(
        self,
        faker: Faker,
        product_query_repository: SQLAlchemyProductQueryRepositoryAdapter,
    ) -> None:
        """find_by_ids() must return an empty list when none of the IDs exist."""
        result = await product_query_repository.find_by_ids(
            [UUID(faker.uuid4()), UUID(faker.uuid4())]
        )

        assert result == []

    # ---------------------------------------------------------------------------
    # ReferencedProductVO contract
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_returned_vo_quantity_defaults_to_one(
        self,
        faker: Faker,
        product_repository: SQLAlchemyProductRepositoryAdapter,
        product_query_repository: SQLAlchemyProductQueryRepositoryAdapter,
    ) -> None:
        """The VO quantity must default to 1 — actual order quantity is set by the use case."""
        product = ProductEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("200.00")),
        )
        await product_repository.save(product)

        result = await product_query_repository.find_by_ids([product.id])

        assert result[0].quantity.value() == 1

    @pytest.mark.asyncio
    async def test_returned_vo_exposes_is_active_flag(
        self,
        faker: Faker,
        product_repository: SQLAlchemyProductRepositoryAdapter,
        product_query_repository: SQLAlchemyProductQueryRepositoryAdapter,
    ) -> None:
        """is_active must be surfaced so use cases can reject inactive products."""
        product = ProductEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("500.00")),
        )
        await product_repository.save(product)

        result = await product_query_repository.find_by_ids([product.id])

        assert result[0].is_active is True

    # ---------------------------------------------------------------------------
    # Boundary — no commit / rollback
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_never_call_commit_on_find_by_ids(
        self,
        faker: Faker,
        product_query_repository: SQLAlchemyProductQueryRepositoryAdapter,
    ) -> None:
        """The adapter must NEVER call session.commit()."""
        with patch.object(
            product_query_repository.session,
            "commit",
            new=AsyncMock(),
        ) as mock_commit:
            await product_query_repository.find_by_ids([UUID(faker.uuid4())])

        mock_commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_never_call_rollback_on_find_by_ids(
        self,
        faker: Faker,
        product_query_repository: SQLAlchemyProductQueryRepositoryAdapter,
    ) -> None:
        """The adapter must NEVER call session.rollback()."""
        with patch.object(
            product_query_repository.session,
            "rollback",
            new=AsyncMock(),
        ) as mock_rollback:
            await product_query_repository.find_by_ids([UUID(faker.uuid4())])

        mock_rollback.assert_not_awaited()

    # ---------------------------------------------------------------------------
    # Error handling
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_raise_order_repository_exception_when_execute_fails(
        self,
        faker: Faker,
        product_query_repository: SQLAlchemyProductQueryRepositoryAdapter,
    ) -> None:
        """OrderRepositoryException must be raised when session.execute fails."""
        with patch.object(
            product_query_repository.session,
            "execute",
            new=AsyncMock(side_effect=SQLAlchemyError("boom")),
        ):
            with pytest.raises(OrderRepositoryException):
                await product_query_repository.find_by_ids([UUID(faker.uuid4())])
