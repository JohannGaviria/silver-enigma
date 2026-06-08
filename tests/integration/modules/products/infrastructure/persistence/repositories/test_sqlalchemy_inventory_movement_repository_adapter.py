from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
from faker import Faker
from sqlalchemy.exc import SQLAlchemyError

from src.modules.products.domain.entities.inventory_movement_entity import (
    InventoryMovementEntity,
)
from src.modules.products.domain.enums.movement_type_log_enum import (
    MovementTypeLogEnum,
)
from src.modules.products.domain.exceptions.inventory_movement_exception import (
    InventoryMovementRepositoryException,
)
from src.modules.products.infrastructure.persistence.repositories.sqlalchemy_inventory_movement_repository_adapter import (
    SQLAlchemyInventoryMovementRepositoryAdapter,
)


class TestSQLAlchemyInventoryMovementRepositoryAdapter:
    # ---------------------------------------------------------------------------
    # Method: save
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_save_inventory_movement_successfully(
        self,
        faker: Faker,
        inventory_movement_repository: SQLAlchemyInventoryMovementRepositoryAdapter,
    ) -> None:
        """save() must persist the inventory movement without errors."""
        entity = InventoryMovementEntity.create(
            product_id=UUID(faker.uuid4()),
            warehouse_id=UUID(faker.uuid4()),
            movement_type=MovementTypeLogEnum.RELEASE,
            quantity=10,
        )

        await inventory_movement_repository.save(entity)

    @pytest.mark.asyncio
    async def test_should_save_inventory_movement_with_order_id(
        self,
        faker: Faker,
        inventory_movement_repository: SQLAlchemyInventoryMovementRepositoryAdapter,
    ) -> None:
        """Inventory movements with order_id must be persisted successfully."""
        entity = InventoryMovementEntity.create(
            product_id=UUID(faker.uuid4()),
            warehouse_id=UUID(faker.uuid4()),
            order_id=UUID(faker.uuid4()),
            movement_type=MovementTypeLogEnum.RESERVE,
            quantity=5,
        )

        await inventory_movement_repository.save(entity)

    @pytest.mark.asyncio
    async def test_should_persist_multiple_inventory_movements_independently(
        self,
        faker: Faker,
        inventory_movement_repository: SQLAlchemyInventoryMovementRepositoryAdapter,
    ) -> None:
        """Different inventory movements can be saved without conflict."""
        product_id = UUID(faker.uuid4())
        warehouse_id = UUID(faker.uuid4())

        entity1 = InventoryMovementEntity.create(
            product_id=product_id,
            warehouse_id=warehouse_id,
            movement_type=MovementTypeLogEnum.RELEASE,
            quantity=10,
        )

        entity2 = InventoryMovementEntity.create(
            product_id=product_id,
            warehouse_id=warehouse_id,
            movement_type=MovementTypeLogEnum.RESERVE,
            quantity=20,
        )

        await inventory_movement_repository.save(entity1)
        await inventory_movement_repository.save(entity2)

        assert entity1.id != entity2.id

    @pytest.mark.asyncio
    async def test_should_raise_inventory_movement_repository_exception_when_flush_fails_in_save(
        self,
        faker: Faker,
        inventory_movement_repository: SQLAlchemyInventoryMovementRepositoryAdapter,
    ) -> None:
        """InventoryMovementRepositoryException must be raised when flush fails."""
        entity = InventoryMovementEntity.create(
            product_id=UUID(faker.uuid4()),
            warehouse_id=UUID(faker.uuid4()),
            movement_type=MovementTypeLogEnum.RELEASE,
            quantity=10,
        )

        with patch.object(
            inventory_movement_repository.session,
            "flush",
            new=AsyncMock(side_effect=SQLAlchemyError("boom")),
        ):
            with pytest.raises(
                InventoryMovementRepositoryException,
                match="Inventory movement repository error.",
            ):
                await inventory_movement_repository.save(entity)

    @pytest.mark.asyncio
    async def test_should_never_call_commit_on_save(
        self,
        faker: Faker,
        inventory_movement_repository: SQLAlchemyInventoryMovementRepositoryAdapter,
    ) -> None:
        """The repository must NEVER call session.commit()."""
        entity = InventoryMovementEntity.create(
            product_id=UUID(faker.uuid4()),
            warehouse_id=UUID(faker.uuid4()),
            movement_type=MovementTypeLogEnum.RELEASE,
            quantity=10,
        )

        with patch.object(
            inventory_movement_repository.session,
            "commit",
            new=AsyncMock(),
        ) as mock_commit:
            await inventory_movement_repository.save(entity)

        mock_commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_never_call_rollback_on_save(
        self,
        faker: Faker,
        inventory_movement_repository: SQLAlchemyInventoryMovementRepositoryAdapter,
    ) -> None:
        """The repository must NEVER call session.rollback()."""
        entity = InventoryMovementEntity.create(
            product_id=UUID(faker.uuid4()),
            warehouse_id=UUID(faker.uuid4()),
            movement_type=MovementTypeLogEnum.RELEASE,
            quantity=10,
        )

        with patch.object(
            inventory_movement_repository.session,
            "rollback",
            new=AsyncMock(),
        ) as mock_rollback:
            await inventory_movement_repository.save(entity)

        mock_rollback.assert_not_awaited()
