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
from src.modules.warehouses.infrastructure.persistence.repositories.sqlalchemy_warehouse_repository_adapter import (
    SQLAlchemyWarehouseRepositoryAdapter,
)


class TestSQLAlchemyWarehouseRepositoryAdapter:
    # --------------------------------------------------------------------------
    # find_by_id
    # --------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_find_warehouse_by_id(
        self,
        faker: Faker,
        warehouse_repository: SQLAlchemyWarehouseRepositoryAdapter,
    ) -> None:
        """find_by_id() must return the warehouse with the given ID."""
        warehouse = WarehouseEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )
        await warehouse_repository.save(warehouse)

        result = await warehouse_repository.find_by_id(warehouse.id)

        assert result
        assert result.id == warehouse.id
        assert result.supplier_id == warehouse.supplier_id
        assert result.name == warehouse.name
        assert result.address == warehouse.address
        assert result.is_active is True

    @pytest.mark.asyncio
    async def test_should_return_none_when_warehouse_not_found(
        self,
        faker: Faker,
        warehouse_repository: SQLAlchemyWarehouseRepositoryAdapter,
    ) -> None:
        """find_by_id() must return None when the warehouse is not found."""
        result = await warehouse_repository.find_by_id(UUID(faker.uuid4()))

        assert result is None

    @pytest.mark.asyncio
    async def test_should_raise_warehouse_repository_exception_when_flush_fails_in_find_by_id(
        self,
        faker: Faker,
        warehouse_repository: SQLAlchemyWarehouseRepositoryAdapter,
    ) -> None:
        """WarehouseRepositoryException must be raised when ``session.flush`` fails."""
        with patch.object(
            warehouse_repository.session,
            "execute",
            new=AsyncMock(side_effect=SQLAlchemyError("boom")),
        ):
            with pytest.raises(WarehouseRepositoryException):
                await warehouse_repository.find_by_id(UUID(faker.uuid4()))

    # ---------------------------------------------------------------------------
    # Method: find_all_by_supplier_id
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_find_all_warehouses_by_supplier_id(
        self,
        faker: Faker,
        warehouse_repository: SQLAlchemyWarehouseRepositoryAdapter,
    ) -> None:
        """find_all_by_supplier_id() must return all warehouses for the supplier."""
        supplier_id = UUID(faker.uuid4())
        warehouses = [
            WarehouseEntity.create(
                supplier_id=supplier_id,
                name=WarehouseNameVO(faker.company()),
                address=WarehouseAddressVO(faker.address()),
            )
            for _ in range(3)
        ]

        for warehouse in warehouses:
            await warehouse_repository.save(warehouse)

        result = await warehouse_repository.find_all_by_supplier_id(supplier_id)

        assert len(result) == 3
        assert all(warehouse in result for warehouse in warehouses)

    @pytest.mark.asyncio
    async def test_should_return_empty_list_when_no_warehouses_found(
        self,
        faker: Faker,
        warehouse_repository: SQLAlchemyWarehouseRepositoryAdapter,
    ) -> None:
        """find_all_by_supplier_id() must return an empty list when no warehouses are found."""
        supplier_id = UUID(faker.uuid4())

        result = await warehouse_repository.find_all_by_supplier_id(supplier_id)

        assert result == []

    @pytest.mark.asyncio
    async def test_should_raise_warehouse_repository_exception_when_flush_fails_in_find_all_by_supplier_id(
        self,
        faker: Faker,
        warehouse_repository: SQLAlchemyWarehouseRepositoryAdapter,
    ) -> None:
        """WarehouseRepositoryException must be raised when ``session.flush`` fails."""
        supplier_id = UUID(faker.uuid4())

        with patch.object(
            warehouse_repository.session,
            "execute",
            new=AsyncMock(side_effect=SQLAlchemyError("boom")),
        ):
            with pytest.raises(WarehouseRepositoryException):
                await warehouse_repository.find_all_by_supplier_id(supplier_id)

    # --------------------------------------------------------------------------
    # update
    # --------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_update_warehouse_and_return_entity(
        self,
        faker: Faker,
        warehouse_repository: SQLAlchemyWarehouseRepositoryAdapter,
    ) -> None:
        """update() must flush the entity and return it with all fields intact."""
        warehouse = WarehouseEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )
        await warehouse_repository.save(warehouse)

        new_name = WarehouseNameVO(faker.company())
        new_address = WarehouseAddressVO(faker.address())
        entity = warehouse.update(
            name=new_name,
            address=new_address,
        )

        result = await warehouse_repository.update(entity)

        assert result.id == entity.id
        assert result.supplier_id == entity.supplier_id
        assert result.name == new_name
        assert result.address == new_address
        assert result.is_active is True

    @pytest.mark.asyncio
    async def test_should_raise_warehouse_repository_exception_when_flush_fails_in_update(
        self,
        faker: Faker,
        warehouse_repository: SQLAlchemyWarehouseRepositoryAdapter,
    ) -> None:
        """WarehouseRepositoryException must be raised when ``session.flush`` fails.

        The repository calls ``flush`` (not ``commit``) — commit is the UoW's
        responsibility. This test patches the right boundary.
        """
        warehouse = WarehouseEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )
        await warehouse_repository.save(warehouse)

        with patch.object(
            warehouse_repository.session,
            "flush",
            new=AsyncMock(side_effect=SQLAlchemyError("boom")),
        ):
            with pytest.raises(WarehouseRepositoryException):
                await warehouse_repository.update(warehouse)

    @pytest.mark.asyncio
    async def test_should_never_call_commit_on_update(
        self,
        faker: Faker,
        warehouse_repository: SQLAlchemyWarehouseRepositoryAdapter,
    ) -> None:
        """The repository must NEVER call ``session.commit()``.

        Transaction control belongs exclusively to the Unit of Work. Calling
        commit inside the repository would bypass the UoW and break atomicity.
        """
        warehouse = WarehouseEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )
        await warehouse_repository.save(warehouse)

        with patch.object(
            warehouse_repository.session,
            "commit",
            new=AsyncMock(),
        ) as mock_commit:
            await warehouse_repository.update(warehouse)

        mock_commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_never_call_rollback_on_update(
        self,
        faker: Faker,
        warehouse_repository: SQLAlchemyWarehouseRepositoryAdapter,
    ) -> None:
        """The repository must NEVER call ``session.rollback()``.

        Rollback is also the UoW's responsibility. The repository only
        flushes; the UoW decides whether to commit or roll back.
        """
        warehouse = WarehouseEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )
        await warehouse_repository.save(warehouse)

        with patch.object(
            warehouse_repository.session,
            "rollback",
            new=AsyncMock(),
        ) as mock_rollback:
            await warehouse_repository.update(warehouse)

        mock_rollback.assert_not_awaited()

    # ---------------------------------------------------------------------------
    # Method: save
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_save_warehouse_and_return_warehouse_entity(
        self,
        faker: Faker,
        warehouse_repository: SQLAlchemyWarehouseRepositoryAdapter,
    ) -> None:
        """save() must flush the entity and return it with all fields intact."""
        entity = WarehouseEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )

        result = await warehouse_repository.save(entity)

        assert result.id == entity.id
        assert result.supplier_id == entity.supplier_id
        assert result.name == entity.name
        assert result.address == entity.address
        assert result.is_active is True

    @pytest.mark.asyncio
    async def test_should_persist_multiple_warehouses_independently(
        self,
        faker: Faker,
        warehouse_repository: SQLAlchemyWarehouseRepositoryAdapter,
    ) -> None:
        """Two different warehouse entities can be saved without conflict."""
        supplier_id = UUID(faker.uuid4())

        entity1 = WarehouseEntity.create(
            supplier_id=supplier_id,
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )
        entity2 = WarehouseEntity.create(
            supplier_id=supplier_id,
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )

        result1 = await warehouse_repository.save(entity1)
        result2 = await warehouse_repository.save(entity2)

        assert result1.id != result2.id
        assert result1.supplier_id == result2.supplier_id

    @pytest.mark.asyncio
    async def test_should_return_entity_with_is_active_true_by_default(
        self,
        faker: Faker,
        warehouse_repository: SQLAlchemyWarehouseRepositoryAdapter,
    ) -> None:
        """Newly created warehouses must always have is_active set to True."""
        entity = WarehouseEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )

        result = await warehouse_repository.save(entity)

        assert result.is_active is True

    @pytest.mark.asyncio
    async def test_should_raise_warehouse_repository_exception_when_flush_fails_in_save(
        self,
        faker: Faker,
        warehouse_repository: SQLAlchemyWarehouseRepositoryAdapter,
    ) -> None:
        """WarehouseRepositoryException must be raised when ``session.flush`` fails.

        The repository calls ``flush`` (not ``commit``) — commit is the UoW's
        responsibility. This test patches the right boundary.
        """
        entity = WarehouseEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )

        with patch.object(
            warehouse_repository.session,
            "flush",
            new=AsyncMock(side_effect=SQLAlchemyError("boom")),
        ):
            with pytest.raises(WarehouseRepositoryException):
                await warehouse_repository.save(entity)

    @pytest.mark.asyncio
    async def test_should_never_call_commit_on_save(
        self,
        faker: Faker,
        warehouse_repository: SQLAlchemyWarehouseRepositoryAdapter,
    ) -> None:
        """The repository must NEVER call ``session.commit()``.

        Transaction control belongs exclusively to the Unit of Work. Calling
        commit inside the repository would bypass the UoW and break atomicity.
        """
        entity = WarehouseEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )

        with patch.object(
            warehouse_repository.session,
            "commit",
            new=AsyncMock(),
        ) as mock_commit:
            await warehouse_repository.save(entity)

        mock_commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_never_call_rollback_on_save(
        self,
        faker: Faker,
        warehouse_repository: SQLAlchemyWarehouseRepositoryAdapter,
    ) -> None:
        """The repository must NEVER call ``session.rollback()``.

        Rollback is also the UoW's responsibility. The repository only
        flushes; the UoW decides whether to commit or roll back.
        """
        entity = WarehouseEntity.create(
            supplier_id=UUID(faker.uuid4()),
            name=WarehouseNameVO(faker.company()),
            address=WarehouseAddressVO(faker.address()),
        )

        with patch.object(
            warehouse_repository.session,
            "rollback",
            new=AsyncMock(),
        ) as mock_rollback:
            await warehouse_repository.save(entity)

        mock_rollback.assert_not_awaited()
