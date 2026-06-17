from collections.abc import Callable
from dataclasses import FrozenInstanceError
from typing import Any
from uuid import UUID

import pytest
from faker import Faker

from src.modules.orders.domain.entities.order_entity import OrderEntity
from src.shared.domain.enums.order_status_enum import OrderStatusEnum


class TestOrderEntity:
    # ---------------------------------------------------------------------------
    # create
    # ---------------------------------------------------------------------------

    def test_should_create_order_entity_when_valid_data_is_provided(
        self,
        faker: Faker,
    ) -> None:
        """Test that the OrderEntity can be created successfully when valid data is provided."""
        buyer_id = UUID(faker.uuid4())
        supplier_id = UUID(faker.uuid4())
        status_order = OrderStatusEnum.DRAFT

        order = OrderEntity.create(
            buyer_id=buyer_id,
            supplier_id=supplier_id,
            status_order=status_order,
        )

        assert order.id is not None
        assert order.buyer_id == buyer_id
        assert order.supplier_id == supplier_id
        assert order.status_order == status_order

        assert order.created_at is not None
        assert order.updated_at is not None
        assert order.created_at == order.updated_at

        assert isinstance(order.id, UUID)
        assert isinstance(order.status_order, OrderStatusEnum)

    def test_should_create_order_entity_with_draft_status(
        self,
        faker: Faker,
    ) -> None:
        """Test that the OrderEntity can be created with DRAFT status."""
        buyer_id = UUID(faker.uuid4())
        supplier_id = UUID(faker.uuid4())

        order = OrderEntity.create(
            buyer_id=buyer_id,
            supplier_id=supplier_id,
            status_order=OrderStatusEnum.DRAFT,
        )

        assert order.status_order == OrderStatusEnum.DRAFT

    def test_should_create_order_entity_with_confirmed_status(
        self,
        faker: Faker,
    ) -> None:
        """Test that the OrderEntity can be created with CONFIRMED status."""
        buyer_id = UUID(faker.uuid4())
        supplier_id = UUID(faker.uuid4())

        order = OrderEntity.create(
            buyer_id=buyer_id,
            supplier_id=supplier_id,
            status_order=OrderStatusEnum.CONFIRMED,
        )

        assert order.status_order == OrderStatusEnum.CONFIRMED

    def test_should_create_order_entity_with_processing_status(
        self,
        faker: Faker,
    ) -> None:
        """Test that the OrderEntity can be created with PROCESSING status."""
        buyer_id = UUID(faker.uuid4())
        supplier_id = UUID(faker.uuid4())

        order = OrderEntity.create(
            buyer_id=buyer_id,
            supplier_id=supplier_id,
            status_order=OrderStatusEnum.PROCESSING,
        )

        assert order.status_order == OrderStatusEnum.PROCESSING

    def test_should_create_order_entity_with_shipped_status(
        self,
        faker: Faker,
    ) -> None:
        """Test that the OrderEntity can be created with SHIPPED status."""
        buyer_id = UUID(faker.uuid4())
        supplier_id = UUID(faker.uuid4())

        order = OrderEntity.create(
            buyer_id=buyer_id,
            supplier_id=supplier_id,
            status_order=OrderStatusEnum.SHIPPED,
        )

        assert order.status_order == OrderStatusEnum.SHIPPED

    def test_should_create_order_entity_with_delivered_status(
        self,
        faker: Faker,
    ) -> None:
        """Test that the OrderEntity can be created with DELIVERED status."""
        buyer_id = UUID(faker.uuid4())
        supplier_id = UUID(faker.uuid4())

        order = OrderEntity.create(
            buyer_id=buyer_id,
            supplier_id=supplier_id,
            status_order=OrderStatusEnum.DELIVERED,
        )

        assert order.status_order == OrderStatusEnum.DELIVERED

    def test_should_create_order_entity_with_cancelled_status(
        self,
        faker: Faker,
    ) -> None:
        """Test that the OrderEntity can be created with CANCELLED status."""
        buyer_id = UUID(faker.uuid4())
        supplier_id = UUID(faker.uuid4())

        order = OrderEntity.create(
            buyer_id=buyer_id,
            supplier_id=supplier_id,
            status_order=OrderStatusEnum.CANCELLED,
        )

        assert order.status_order == OrderStatusEnum.CANCELLED

    def test_should_generate_unique_ids_for_different_order_entities(
        self,
        faker: Faker,
    ) -> None:
        """Test that different OrderEntity instances generate unique IDs."""
        buyer_id = UUID(faker.uuid4())
        supplier_id = UUID(faker.uuid4())
        status_order = OrderStatusEnum.DRAFT

        order1 = OrderEntity.create(
            buyer_id=buyer_id,
            supplier_id=supplier_id,
            status_order=status_order,
        )

        order2 = OrderEntity.create(
            buyer_id=buyer_id,
            supplier_id=supplier_id,
            status_order=status_order,
        )

        assert order1.id != order2.id

    # ---------------------------------------------------------------------------
    # immutability
    # ---------------------------------------------------------------------------

    @pytest.mark.parametrize(
        ("attribute", "value_factory"),
        [
            (
                "buyer_id",
                lambda faker: UUID(faker.uuid4()),
            ),
            (
                "supplier_id",
                lambda faker: UUID(faker.uuid4()),
            ),
            (
                "status_order",
                lambda faker: OrderStatusEnum.CONFIRMED,
            ),
        ],
    )
    def test_should_raise_exception_when_attempting_to_modify_order_entity_attributes(
        self,
        faker: Faker,
        attribute: str,
        value_factory: Callable[[Faker], Any],
    ) -> None:
        """Test that the OrderEntity raises a FrozenInstanceError when attempting to modify its attributes."""
        order = OrderEntity.create(
            buyer_id=UUID(faker.uuid4()),
            supplier_id=UUID(faker.uuid4()),
            status_order=OrderStatusEnum.DRAFT,
        )

        with pytest.raises(FrozenInstanceError):
            setattr(order, attribute, value_factory(faker))

    # ---------------------------------------------------------------------------
    # equality
    # ---------------------------------------------------------------------------

    def test_should_return_equal_order_entities_when_data_is_identical(
        self,
        faker: Faker,
    ) -> None:
        """Test that two OrderEntity instances with identical data are considered equal."""
        buyer_id = UUID(faker.uuid4())
        supplier_id = UUID(faker.uuid4())
        status_order = OrderStatusEnum.DRAFT

        order1 = OrderEntity.create(
            buyer_id=buyer_id,
            supplier_id=supplier_id,
            status_order=status_order,
        )

        order2 = OrderEntity(
            id=order1.id,
            buyer_id=order1.buyer_id,
            supplier_id=order1.supplier_id,
            status_order=order1.status_order,
            created_at=order1.created_at,
            updated_at=order1.updated_at,
        )

        assert order1 == order2

    def test_should_return_different_order_entities_when_ids_differ(
        self,
        faker: Faker,
    ) -> None:
        """Test that two OrderEntity instances with different IDs are not equal."""
        buyer_id = UUID(faker.uuid4())
        supplier_id = UUID(faker.uuid4())
        status_order = OrderStatusEnum.DRAFT

        order1 = OrderEntity.create(
            buyer_id=buyer_id,
            supplier_id=supplier_id,
            status_order=status_order,
        )

        order2 = OrderEntity.create(
            buyer_id=buyer_id,
            supplier_id=supplier_id,
            status_order=status_order,
        )

        assert order1 != order2

    def test_should_return_different_order_entities_when_statuses_differ(
        self,
        faker: Faker,
    ) -> None:
        """Test that two OrderEntity instances with different statuses are not equal."""
        buyer_id = UUID(faker.uuid4())
        supplier_id = UUID(faker.uuid4())

        order1 = OrderEntity.create(
            buyer_id=buyer_id,
            supplier_id=supplier_id,
            status_order=OrderStatusEnum.DRAFT,
        )

        order2 = OrderEntity.create(
            buyer_id=buyer_id,
            supplier_id=supplier_id,
            status_order=OrderStatusEnum.CONFIRMED,
        )

        assert order1 != order2

    def test_should_return_different_order_entities_when_buyer_ids_differ(
        self,
        faker: Faker,
    ) -> None:
        """Test that two OrderEntity instances with different buyer IDs are not equal."""
        buyer_id1 = UUID(faker.uuid4())
        buyer_id2 = UUID(faker.uuid4())
        supplier_id = UUID(faker.uuid4())
        status_order = OrderStatusEnum.DRAFT

        order1 = OrderEntity.create(
            buyer_id=buyer_id1,
            supplier_id=supplier_id,
            status_order=status_order,
        )

        order2 = OrderEntity.create(
            buyer_id=buyer_id2,
            supplier_id=supplier_id,
            status_order=status_order,
        )

        assert order1 != order2
