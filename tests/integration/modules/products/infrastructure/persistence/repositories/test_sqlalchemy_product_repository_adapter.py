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
    # --------------------------------------------------------------------------
    # find_by_id
    # --------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_find_product_by_id(
        self,
        faker: Faker,
        product_repository: SQLAlchemyProductRepositoryAdapter,
    ) -> None:
        """find_by_id() must return the product with the given ID."""
        product = ProductEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("1000")),
        )
        await product_repository.save(product)

        result = await product_repository.find_by_id(product.id)

        assert result
        assert result.id == product.id
        assert result.supplier_id == product.supplier_id
        assert result.name == product.name
        assert result.description == product.description
        assert result.unit_of_measure == product.unit_of_measure
        assert result.unit_price == product.unit_price
        assert result.is_active is True

    @pytest.mark.asyncio
    async def test_should_return_none_when_product_not_found(
        self,
        faker: Faker,
        product_repository: SQLAlchemyProductRepositoryAdapter,
    ) -> None:
        """find_by_id() must return None when the product is not found."""
        result = await product_repository.find_by_id(UUID(faker.uuid4()))

        assert result is None

    @pytest.mark.asyncio
    async def test_should_raise_product_repository_exception_when_execute_fails_in_find_by_id(
        self,
        faker: Faker,
        product_repository: SQLAlchemyProductRepositoryAdapter,
    ) -> None:
        """ProductRepositoryException must be raised when session.execute fails."""
        with patch.object(
            product_repository.session,
            "execute",
            new=AsyncMock(side_effect=SQLAlchemyError("boom")),
        ):
            with pytest.raises(ProductRepositoryException):
                await product_repository.find_by_id(UUID(faker.uuid4()))

    # --------------------------------------------------------------------------
    # update
    # --------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_update_product_and_return_entity(
        self,
        faker: Faker,
        product_repository: SQLAlchemyProductRepositoryAdapter,
    ) -> None:
        """update() must flush the entity and return it with all updated fields."""
        product = ProductEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("1000")),
        )
        await product_repository.save(product)

        new_name = ProductNameVO(faker.company())
        new_description = faker.text()
        new_unit_price = UnitPriceVO(Decimal("2500"))

        entity = product.update(
            name=new_name,
            description=new_description,
            unit_price=new_unit_price,
        )

        result = await product_repository.update(entity)

        assert result.id == entity.id
        assert result.supplier_id == entity.supplier_id
        assert result.name == new_name
        assert result.description == new_description
        assert result.unit_price == new_unit_price
        assert result.unit_of_measure == entity.unit_of_measure
        assert result.is_active is True

    @pytest.mark.asyncio
    async def test_should_raise_product_repository_exception_when_flush_fails_in_update(
        self,
        faker: Faker,
        product_repository: SQLAlchemyProductRepositoryAdapter,
    ) -> None:
        """ProductRepositoryException must be raised when session.flush fails."""
        product = ProductEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("1000")),
        )
        await product_repository.save(product)

        with patch.object(
            product_repository.session,
            "flush",
            new=AsyncMock(side_effect=SQLAlchemyError("boom")),
        ):
            with pytest.raises(ProductRepositoryException):
                await product_repository.update(product)

    @pytest.mark.asyncio
    async def test_should_never_call_commit_on_update(
        self,
        faker: Faker,
        product_repository: SQLAlchemyProductRepositoryAdapter,
    ) -> None:
        """The repository must NEVER call session.commit()."""
        product = ProductEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("1000")),
        )
        await product_repository.save(product)

        with patch.object(
            product_repository.session,
            "commit",
            new=AsyncMock(),
        ) as mock_commit:
            await product_repository.update(product)

        mock_commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_never_call_rollback_on_update(
        self,
        faker: Faker,
        product_repository: SQLAlchemyProductRepositoryAdapter,
    ) -> None:
        """The repository must NEVER call session.rollback()."""
        product = ProductEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=ProductNameVO(faker.company()),
            description=faker.text(),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("1000")),
        )
        await product_repository.save(product)

        with patch.object(
            product_repository.session,
            "rollback",
            new=AsyncMock(),
        ) as mock_rollback:
            await product_repository.update(product)

        mock_rollback.assert_not_awaited()

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
