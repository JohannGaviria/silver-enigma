from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
from faker import Faker
from sqlalchemy.exc import SQLAlchemyError

from src.modules.warehouses.domain.entities.warehouse_entity import WarehouseEntity
from src.modules.warehouses.domain.exceptions.warehouse_exception import (
    WarehouseRepositoryException,
)
from src.modules.warehouses.domain.value_objects.warehouse_address_vo import (
    WarehouseAddressVO,
)
from src.modules.warehouses.domain.value_objects.warehouse_name_vo import (
    WarehouseNameVO,
)
from src.modules.warehouses.infrastructure.persistence.repositories.sqlalchemy_warehouse_query_repository_adapter import (
    SQLAlchemyWarehouseQueryRepositoryAdapter,
)
from src.modules.warehouses.infrastructure.persistence.repositories.sqlalchemy_warehouse_repository_adapter import (
    SQLAlchemyWarehouseRepositoryAdapter,
)


class TestSQLAlchemyWarehouseQueryRepositoryAdapter:
    # --------------------------------------------------------------------------
    # find_by_id
    # --------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_find_warehouse_by_id(
        self,
        faker: Faker,
        warehouse_repository: SQLAlchemyWarehouseRepositoryAdapter,
        warehouse_query_repository: SQLAlchemyWarehouseQueryRepositoryAdapter,
    ) -> None:
        """find_by_id() must return the warehouse with the given ID."""
        warehouse = WarehouseEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )
        await warehouse_repository.save(warehouse)

        result = await warehouse_query_repository.find_by_id(warehouse.id)

        assert result
        assert result.warehouse_id == warehouse.id
        assert result.supplier_id == warehouse.supplier_id
        assert result.is_active is True

    @pytest.mark.asyncio
    async def test_should_return_none_when_warehouse_not_found(
        self,
        faker: Faker,
        warehouse_query_repository: SQLAlchemyWarehouseQueryRepositoryAdapter,
    ) -> None:
        """find_by_id() must return None when the warehouse is not found."""
        result = await warehouse_query_repository.find_by_id(UUID(faker.uuid4()))

        assert result is None

    @pytest.mark.asyncio
    async def test_should_raise_warehouse_query_repository_exception_when_flush_fails_in_find_by_id(
        self,
        faker: Faker,
        warehouse_query_repository: SQLAlchemyWarehouseQueryRepositoryAdapter,
    ) -> None:
        """WarehouseRepositoryException must be raised when ``session.flush`` fails."""
        with patch.object(
            warehouse_query_repository.session,
            "execute",
            new=AsyncMock(side_effect=SQLAlchemyError("boom")),
        ):
            with pytest.raises(WarehouseRepositoryException):
                await warehouse_query_repository.find_by_id(UUID(faker.uuid4()))
