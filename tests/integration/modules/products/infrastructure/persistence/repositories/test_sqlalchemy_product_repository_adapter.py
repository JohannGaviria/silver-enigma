from decimal import Decimal
from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
from faker import Faker
from sqlalchemy.exc import SQLAlchemyError

from src.modules.products.domain.entities.product_entity import ProductEntity
from src.modules.products.domain.enums.unit_of_measure_enum import UnitOfMeasureEnum
from src.modules.products.domain.exceptions.product_exception import (
    ProductRepositoryException,
)
from src.modules.products.domain.value_objects.product_name_vo import ProductNameVO
from src.modules.products.domain.value_objects.unit_price_vo import UnitPriceVO
from src.modules.products.infrastructure.persistence.repositories.sqlalchemy_product_repository_adapter import (
    SQLAlchemyProductRepositoryAdapter,
)


class TestSQLAlchemyProductRepositoryAdapter:
    # ---------------------------------------------------------------------------
    # Method: save
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_save_product_and_return_product_entity(
        self,
        faker: Faker,
        product_repository: SQLAlchemyProductRepositoryAdapter,
    ) -> None:
        """save() must flush the entity and return it with all fields intact."""
        entity = ProductEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("1000")),
        )

        result = await product_repository.save(entity)

        assert result.id == entity.id
        assert result.supplier_id == entity.supplier_id
        assert result.name == entity.name
        assert result.description == entity.description
        assert result.unit_of_measure == entity.unit_of_measure
        assert result.unit_price == entity.unit_price
        assert result.is_active is True

    @pytest.mark.asyncio
    async def test_should_persist_multiple_products_independently(
        self,
        faker: Faker,
        product_repository: SQLAlchemyProductRepositoryAdapter,
    ) -> None:
        """Two different product entities can be saved without conflict."""
        supplier_id = UUID(faker.uuid4())

        entity1 = ProductEntity.create(
            supplier_id=supplier_id,
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("1000")),
        )

        entity2 = ProductEntity.create(
            supplier_id=supplier_id,
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("2000")),
        )

        result1 = await product_repository.save(entity1)
        result2 = await product_repository.save(entity2)

        assert result1.id != result2.id
        assert result1.supplier_id == result2.supplier_id

    @pytest.mark.asyncio
    async def test_should_return_entity_with_is_active_true_by_default(
        self,
        faker: Faker,
        product_repository: SQLAlchemyProductRepositoryAdapter,
    ) -> None:
        """Newly created products must always have is_active set to True."""
        entity = ProductEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("1000")),
        )

        result = await product_repository.save(entity)

        assert result.is_active is True

    @pytest.mark.asyncio
    async def test_should_raise_product_repository_exception_when_flush_fails_in_save(
        self,
        faker: Faker,
        product_repository: SQLAlchemyProductRepositoryAdapter,
    ) -> None:
        """ProductRepositoryException must be raised when session.flush fails."""
        entity = ProductEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("1000")),
        )

        with patch.object(
            product_repository.session,
            "flush",
            new=AsyncMock(side_effect=SQLAlchemyError("boom")),
        ):
            with pytest.raises(
                ProductRepositoryException,
                match="Product repository error.",
            ):
                await product_repository.save(entity)

    @pytest.mark.asyncio
    async def test_should_never_call_commit_on_save(
        self,
        faker: Faker,
        product_repository: SQLAlchemyProductRepositoryAdapter,
    ) -> None:
        """The repository must NEVER call session.commit()."""
        entity = ProductEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("1000")),
        )

        with patch.object(
            product_repository.session,
            "commit",
            new=AsyncMock(),
        ) as mock_commit:
            await product_repository.save(entity)

        mock_commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_never_call_rollback_on_save(
        self,
        faker: Faker,
        product_repository: SQLAlchemyProductRepositoryAdapter,
    ) -> None:
        """The repository must NEVER call session.rollback()."""
        entity = ProductEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("1000")),
        )

        with patch.object(
            product_repository.session,
            "rollback",
            new=AsyncMock(),
        ) as mock_rollback:
            await product_repository.save(entity)

        mock_rollback.assert_not_awaited()
