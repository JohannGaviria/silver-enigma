from collections.abc import Callable
from dataclasses import FrozenInstanceError
from typing import Any
from uuid import UUID

import pytest
from faker import Faker

from src.modules.orders.domain.entities.order_status_history_entity import (
    OrderStatusHistoryEntity,
)
from src.shared.domain.enums.order_status_enum import OrderStatusEnum
from src.shared.domain.enums.user_role_enum import UserRoleEnum


class TestOrderStatusHistoryEntity:
    # ---------------------------------------------------------------------------
    # create
    # ---------------------------------------------------------------------------

    def test_should_create_order_status_history_entity_when_valid_data_is_provided(
        self,
        faker: Faker,
    ) -> None:
        """Test that the OrderStatusHistoryEntity can be created successfully when valid data is provided."""
        order_id = UUID(faker.uuid4())
        previous_status = OrderStatusEnum.DRAFT
        new_status = OrderStatusEnum.CONFIRMED
        changed_by = UUID(faker.uuid4())
        changed_by_role = UserRoleEnum.BUYER

        history = OrderStatusHistoryEntity.create(
            order_id=order_id,
            previous_status=previous_status,
            new_status=new_status,
            changed_by=changed_by,
            changed_by_role=changed_by_role,
        )

        assert history.id is not None
        assert history.order_id == order_id
        assert history.previous_status == previous_status
        assert history.new_status == new_status
        assert history.changed_by == changed_by
        assert history.changed_by_role == changed_by_role

        assert history.created_at is not None
        assert history.updated_at is not None
        assert history.created_at == history.updated_at

        assert isinstance(history.id, UUID)
        assert isinstance(history.previous_status, OrderStatusEnum)
        assert isinstance(history.new_status, OrderStatusEnum)
        assert isinstance(history.changed_by_role, UserRoleEnum)

    def test_should_create_order_status_history_entity_with_all_status_transitions(
        self,
        faker: Faker,
    ) -> None:
        """Test that OrderStatusHistoryEntity can be created with all status transitions."""
        order_id = UUID(faker.uuid4())
        changed_by = UUID(faker.uuid4())
        changed_by_role = UserRoleEnum.ADMIN

        transitions = [
            # Forward transitions
            (OrderStatusEnum.DRAFT, OrderStatusEnum.CONFIRMED),
            (OrderStatusEnum.CONFIRMED, OrderStatusEnum.PROCESSING),
            (OrderStatusEnum.PROCESSING, OrderStatusEnum.SHIPPED),
            (OrderStatusEnum.SHIPPED, OrderStatusEnum.DELIVERED),
            # Cancellation transitions
            (OrderStatusEnum.DRAFT, OrderStatusEnum.CANCELLED),
            (OrderStatusEnum.CONFIRMED, OrderStatusEnum.CANCELLED),
            (OrderStatusEnum.PROCESSING, OrderStatusEnum.CANCELLED),
            (OrderStatusEnum.SHIPPED, OrderStatusEnum.CANCELLED),
        ]

        for previous_status, new_status in transitions:
            history = OrderStatusHistoryEntity.create(
                order_id=order_id,
                previous_status=previous_status,
                new_status=new_status,
                changed_by=changed_by,
                changed_by_role=changed_by_role,
            )

            assert history.previous_status == previous_status
            assert history.new_status == new_status

    def test_should_create_order_status_history_entity_with_forward_transition_from_draft_to_confirmed(
        self,
        faker: Faker,
    ) -> None:
        """Test that OrderStatusHistoryEntity can be created with DRAFT to CONFIRMED transition."""
        order_id = UUID(faker.uuid4())
        changed_by = UUID(faker.uuid4())
        changed_by_role = UserRoleEnum.BUYER

        history = OrderStatusHistoryEntity.create(
            order_id=order_id,
            previous_status=OrderStatusEnum.DRAFT,
            new_status=OrderStatusEnum.CONFIRMED,
            changed_by=changed_by,
            changed_by_role=changed_by_role,
        )

        assert history.previous_status == OrderStatusEnum.DRAFT
        assert history.new_status == OrderStatusEnum.CONFIRMED

    def test_should_create_order_status_history_entity_with_forward_transition_from_confirmed_to_processing(
        self,
        faker: Faker,
    ) -> None:
        """Test that OrderStatusHistoryEntity can be created with CONFIRMED to PROCESSING transition."""
        order_id = UUID(faker.uuid4())
        changed_by = UUID(faker.uuid4())
        changed_by_role = UserRoleEnum.SUPPLIER

        history = OrderStatusHistoryEntity.create(
            order_id=order_id,
            previous_status=OrderStatusEnum.CONFIRMED,
            new_status=OrderStatusEnum.PROCESSING,
            changed_by=changed_by,
            changed_by_role=changed_by_role,
        )

        assert history.previous_status == OrderStatusEnum.CONFIRMED
        assert history.new_status == OrderStatusEnum.PROCESSING

    def test_should_create_order_status_history_entity_with_forward_transition_from_processing_to_shipped(
        self,
        faker: Faker,
    ) -> None:
        """Test that OrderStatusHistoryEntity can be created with PROCESSING to SHIPPED transition."""
        order_id = UUID(faker.uuid4())
        changed_by = UUID(faker.uuid4())
        changed_by_role = UserRoleEnum.SUPPLIER

        history = OrderStatusHistoryEntity.create(
            order_id=order_id,
            previous_status=OrderStatusEnum.PROCESSING,
            new_status=OrderStatusEnum.SHIPPED,
            changed_by=changed_by,
            changed_by_role=changed_by_role,
        )

        assert history.previous_status == OrderStatusEnum.PROCESSING
        assert history.new_status == OrderStatusEnum.SHIPPED

    def test_should_create_order_status_history_entity_with_forward_transition_from_shipped_to_delivered(
        self,
        faker: Faker,
    ) -> None:
        """Test that OrderStatusHistoryEntity can be created with SHIPPED to DELIVERED transition."""
        order_id = UUID(faker.uuid4())
        changed_by = UUID(faker.uuid4())
        changed_by_role = UserRoleEnum.SUPPLIER

        history = OrderStatusHistoryEntity.create(
            order_id=order_id,
            previous_status=OrderStatusEnum.SHIPPED,
            new_status=OrderStatusEnum.DELIVERED,
            changed_by=changed_by,
            changed_by_role=changed_by_role,
        )

        assert history.previous_status == OrderStatusEnum.SHIPPED
        assert history.new_status == OrderStatusEnum.DELIVERED

    def test_should_create_order_status_history_entity_with_cancellation_from_draft(
        self,
        faker: Faker,
    ) -> None:
        """Test that OrderStatusHistoryEntity can be created with DRAFT to CANCELLED transition."""
        order_id = UUID(faker.uuid4())
        changed_by = UUID(faker.uuid4())
        changed_by_role = UserRoleEnum.BUYER

        history = OrderStatusHistoryEntity.create(
            order_id=order_id,
            previous_status=OrderStatusEnum.DRAFT,
            new_status=OrderStatusEnum.CANCELLED,
            changed_by=changed_by,
            changed_by_role=changed_by_role,
        )

        assert history.previous_status == OrderStatusEnum.DRAFT
        assert history.new_status == OrderStatusEnum.CANCELLED

    def test_should_create_order_status_history_entity_with_cancellation_from_confirmed(
        self,
        faker: Faker,
    ) -> None:
        """Test that OrderStatusHistoryEntity can be created with CONFIRMED to CANCELLED transition."""
        order_id = UUID(faker.uuid4())
        changed_by = UUID(faker.uuid4())
        changed_by_role = UserRoleEnum.ADMIN

        history = OrderStatusHistoryEntity.create(
            order_id=order_id,
            previous_status=OrderStatusEnum.CONFIRMED,
            new_status=OrderStatusEnum.CANCELLED,
            changed_by=changed_by,
            changed_by_role=changed_by_role,
        )

        assert history.previous_status == OrderStatusEnum.CONFIRMED
        assert history.new_status == OrderStatusEnum.CANCELLED

    def test_should_create_order_status_history_entity_with_cancellation_from_processing(
        self,
        faker: Faker,
    ) -> None:
        """Test that OrderStatusHistoryEntity can be created with PROCESSING to CANCELLED transition."""
        order_id = UUID(faker.uuid4())
        changed_by = UUID(faker.uuid4())
        changed_by_role = UserRoleEnum.ADMIN

        history = OrderStatusHistoryEntity.create(
            order_id=order_id,
            previous_status=OrderStatusEnum.PROCESSING,
            new_status=OrderStatusEnum.CANCELLED,
            changed_by=changed_by,
            changed_by_role=changed_by_role,
        )

        assert history.previous_status == OrderStatusEnum.PROCESSING
        assert history.new_status == OrderStatusEnum.CANCELLED

    def test_should_create_order_status_history_entity_with_cancellation_from_shipped(
        self,
        faker: Faker,
    ) -> None:
        """Test that OrderStatusHistoryEntity can be created with SHIPPED to CANCELLED transition."""
        order_id = UUID(faker.uuid4())
        changed_by = UUID(faker.uuid4())
        changed_by_role = UserRoleEnum.ADMIN

        history = OrderStatusHistoryEntity.create(
            order_id=order_id,
            previous_status=OrderStatusEnum.SHIPPED,
            new_status=OrderStatusEnum.CANCELLED,
            changed_by=changed_by,
            changed_by_role=changed_by_role,
        )

        assert history.previous_status == OrderStatusEnum.SHIPPED
        assert history.new_status == OrderStatusEnum.CANCELLED

    def test_should_create_order_status_history_entity_with_different_user_roles(
        self,
        faker: Faker,
    ) -> None:
        """Test that OrderStatusHistoryEntity can be created with different user roles."""
        order_id = UUID(faker.uuid4())
        previous_status = OrderStatusEnum.DRAFT
        new_status = OrderStatusEnum.CONFIRMED
        changed_by = UUID(faker.uuid4())

        roles = [
            UserRoleEnum.BUYER,
            UserRoleEnum.SUPPLIER,
            UserRoleEnum.ADMIN,
        ]

        for role in roles:
            history = OrderStatusHistoryEntity.create(
                order_id=order_id,
                previous_status=previous_status,
                new_status=new_status,
                changed_by=changed_by,
                changed_by_role=role,
            )

            assert history.changed_by_role == role

    def test_should_generate_unique_ids_for_different_order_status_history_entities(
        self,
        faker: Faker,
    ) -> None:
        """Test that different OrderStatusHistoryEntity instances generate unique IDs."""
        order_id = UUID(faker.uuid4())
        previous_status = OrderStatusEnum.DRAFT
        new_status = OrderStatusEnum.CONFIRMED
        changed_by = UUID(faker.uuid4())
        changed_by_role = UserRoleEnum.BUYER

        history1 = OrderStatusHistoryEntity.create(
            order_id=order_id,
            previous_status=previous_status,
            new_status=new_status,
            changed_by=changed_by,
            changed_by_role=changed_by_role,
        )

        history2 = OrderStatusHistoryEntity.create(
            order_id=order_id,
            previous_status=previous_status,
            new_status=new_status,
            changed_by=changed_by,
            changed_by_role=changed_by_role,
        )

        assert history1.id != history2.id

    def test_should_create_order_status_history_entity_with_different_order_ids(
        self,
        faker: Faker,
    ) -> None:
        """Test that OrderStatusHistoryEntity can be created with different order IDs."""
        order_id1 = UUID(faker.uuid4())
        order_id2 = UUID(faker.uuid4())
        previous_status = OrderStatusEnum.DRAFT
        new_status = OrderStatusEnum.CONFIRMED
        changed_by = UUID(faker.uuid4())
        changed_by_role = UserRoleEnum.BUYER

        history1 = OrderStatusHistoryEntity.create(
            order_id=order_id1,
            previous_status=previous_status,
            new_status=new_status,
            changed_by=changed_by,
            changed_by_role=changed_by_role,
        )

        history2 = OrderStatusHistoryEntity.create(
            order_id=order_id2,
            previous_status=previous_status,
            new_status=new_status,
            changed_by=changed_by,
            changed_by_role=changed_by_role,
        )

        assert history1.order_id != history2.order_id

    # ---------------------------------------------------------------------------
    # immutability
    # ---------------------------------------------------------------------------

    @pytest.mark.parametrize(
        ("attribute", "value_factory"),
        [
            (
                "order_id",
                lambda faker: UUID(faker.uuid4()),
            ),
            (
                "previous_status",
                lambda faker: OrderStatusEnum.CONFIRMED,
            ),
            (
                "new_status",
                lambda faker: OrderStatusEnum.PROCESSING,
            ),
            (
                "changed_by",
                lambda faker: UUID(faker.uuid4()),
            ),
            (
                "changed_by_role",
                lambda faker: UserRoleEnum.ADMIN,
            ),
        ],
    )
    def test_should_raise_exception_when_attempting_to_modify_order_status_history_entity_attributes(
        self,
        faker: Faker,
        attribute: str,
        value_factory: Callable[[Faker], Any],
    ) -> None:
        """Test that the OrderStatusHistoryEntity raises a FrozenInstanceError when attempting to modify its attributes."""
        history = OrderStatusHistoryEntity.create(
            order_id=UUID(faker.uuid4()),
            previous_status=OrderStatusEnum.DRAFT,
            new_status=OrderStatusEnum.CONFIRMED,
            changed_by=UUID(faker.uuid4()),
            changed_by_role=UserRoleEnum.BUYER,
        )

        with pytest.raises(FrozenInstanceError):
            setattr(history, attribute, value_factory(faker))

    # ---------------------------------------------------------------------------
    # equality
    # ---------------------------------------------------------------------------

    def test_should_return_equal_order_status_history_entities_when_data_is_identical(
        self,
        faker: Faker,
    ) -> None:
        """Test that two OrderStatusHistoryEntity instances with identical data are considered equal."""
        order_id = UUID(faker.uuid4())
        previous_status = OrderStatusEnum.DRAFT
        new_status = OrderStatusEnum.CONFIRMED
        changed_by = UUID(faker.uuid4())
        changed_by_role = UserRoleEnum.BUYER

        history1 = OrderStatusHistoryEntity.create(
            order_id=order_id,
            previous_status=previous_status,
            new_status=new_status,
            changed_by=changed_by,
            changed_by_role=changed_by_role,
        )

        history2 = OrderStatusHistoryEntity(
            id=history1.id,
            order_id=history1.order_id,
            previous_status=history1.previous_status,
            new_status=history1.new_status,
            changed_by=history1.changed_by,
            changed_by_role=history1.changed_by_role,
            created_at=history1.created_at,
            updated_at=history1.updated_at,
        )

        assert history1 == history2

    def test_should_return_different_order_status_history_entities_when_ids_differ(
        self,
        faker: Faker,
    ) -> None:
        """Test that two OrderStatusHistoryEntity instances with different IDs are not equal."""
        order_id = UUID(faker.uuid4())
        previous_status = OrderStatusEnum.DRAFT
        new_status = OrderStatusEnum.CONFIRMED
        changed_by = UUID(faker.uuid4())
        changed_by_role = UserRoleEnum.BUYER

        history1 = OrderStatusHistoryEntity.create(
            order_id=order_id,
            previous_status=previous_status,
            new_status=new_status,
            changed_by=changed_by,
            changed_by_role=changed_by_role,
        )

        history2 = OrderStatusHistoryEntity.create(
            order_id=order_id,
            previous_status=previous_status,
            new_status=new_status,
            changed_by=changed_by,
            changed_by_role=changed_by_role,
        )

        assert history1 != history2

    def test_should_return_different_order_status_history_entities_when_statuses_differ(
        self,
        faker: Faker,
    ) -> None:
        """Test that two OrderStatusHistoryEntity instances with different statuses are not equal."""
        order_id = UUID(faker.uuid4())
        changed_by = UUID(faker.uuid4())
        changed_by_role = UserRoleEnum.BUYER

        history1 = OrderStatusHistoryEntity.create(
            order_id=order_id,
            previous_status=OrderStatusEnum.DRAFT,
            new_status=OrderStatusEnum.CONFIRMED,
            changed_by=changed_by,
            changed_by_role=changed_by_role,
        )

        history2 = OrderStatusHistoryEntity.create(
            order_id=order_id,
            previous_status=OrderStatusEnum.CONFIRMED,
            new_status=OrderStatusEnum.PROCESSING,
            changed_by=changed_by,
            changed_by_role=changed_by_role,
        )

        assert history1 != history2

    def test_should_return_different_order_status_history_entities_when_previous_status_differ(
        self,
        faker: Faker,
    ) -> None:
        """Test that two OrderStatusHistoryEntity instances with different previous statuses are not equal."""
        order_id = UUID(faker.uuid4())
        new_status = OrderStatusEnum.CONFIRMED
        changed_by = UUID(faker.uuid4())
        changed_by_role = UserRoleEnum.BUYER

        history1 = OrderStatusHistoryEntity.create(
            order_id=order_id,
            previous_status=OrderStatusEnum.DRAFT,
            new_status=new_status,
            changed_by=changed_by,
            changed_by_role=changed_by_role,
        )

        history2 = OrderStatusHistoryEntity.create(
            order_id=order_id,
            previous_status=OrderStatusEnum.PROCESSING,
            new_status=new_status,
            changed_by=changed_by,
            changed_by_role=changed_by_role,
        )

        assert history1 != history2

    def test_should_return_different_order_status_history_entities_when_roles_differ(
        self,
        faker: Faker,
    ) -> None:
        """Test that two OrderStatusHistoryEntity instances with different roles are not equal."""
        order_id = UUID(faker.uuid4())
        previous_status = OrderStatusEnum.DRAFT
        new_status = OrderStatusEnum.CONFIRMED
        changed_by = UUID(faker.uuid4())

        history1 = OrderStatusHistoryEntity.create(
            order_id=order_id,
            previous_status=previous_status,
            new_status=new_status,
            changed_by=changed_by,
            changed_by_role=UserRoleEnum.BUYER,
        )

        history2 = OrderStatusHistoryEntity.create(
            order_id=order_id,
            previous_status=previous_status,
            new_status=new_status,
            changed_by=changed_by,
            changed_by_role=UserRoleEnum.ADMIN,
        )

        assert history1 != history2
