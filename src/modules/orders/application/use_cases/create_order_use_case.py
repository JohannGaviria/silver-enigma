"""This module contains the CreateOrderUseCase class."""

from src.modules.orders.application.dtos.create_order_dto import (
    CreateOrderCommandDto,
    CreateOrderResponseDTO,
    ProductDetailsDto,
)
from src.modules.orders.domain.entities.order_entity import OrderEntity
from src.modules.orders.domain.entities.order_items_entity import OrderItemsEntity
from src.modules.orders.domain.entities.order_status_history_entity import (
    OrderStatusHistoryEntity,
)
from src.modules.orders.domain.exceptions.order_exception import (
    DuplicateOrderItemsException,
    InactiveReferencedProductException,
    OrderItemsRequiredException,
    ProductsFromDifferentSuppliersException,
)
from src.modules.orders.domain.ports.unit_of_work.order_management_unit_of_work_port import (
    OrderManagementUnitOfWorkPort,
)
from src.modules.orders.domain.value_object.quantity_vo import QuantityVO
from src.shared.application.dtos.authenticated_user_dto import (
    AuthenticatedUserCommandDto,
)
from src.shared.domain.enums.order_status_enum import OrderStatusEnum
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.session_exception import (
    InsufficientPermissionsException,
)
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class CreateOrderUseCase:
    """Use case for creating an order.

    This use case creates an order and its associated order items and order status history.
    """

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        order_management_unit_of_work: OrderManagementUnitOfWorkPort,
    ) -> None:
        """Initializes the CreateOrderUseCase.

        Args:
            logger_factory_outbound (LoggerFactoryOutboundPort): The logger factory.
            order_management_unit_of_work (OrderManagementUnitOfWorkPort): The order management unit of work.
        """
        self._logger = logger_factory_outbound.get_logger(__name__)
        self.order_management_unit_of_work = order_management_unit_of_work

    async def execute(
        self,
        command: CreateOrderCommandDto,
        authenticated_user: AuthenticatedUserCommandDto,
    ) -> CreateOrderResponseDTO:
        """Execute the use case to create an order.

        This method creates an order and its associated order items and order status history.

        Args:
            command (CreateOrderCommandDto): The command to create an order.
            authenticated_user (AuthenticatedUserCommandDto): The authenticated user.

        Returns:
            CreateOrderResponseDTO: The response to create an order.

        Raises:
            InsufficientPermissionsException: If the user does not have the required permissions.
            OrderItemsRequiredException: If no items are provided for the order.
            DuplicateOrderItemsException: If duplicate items are provided for the order.
            ProductsFromDifferentSuppliersException: If products are from different suppliers.
            InactiveReferencedProductException: If a product is inactive.
        """
        self._logger.info(
            "Executing create order use case.",
            user_id=authenticated_user.user_id,
            actor_role=authenticated_user.role,
        )

        # Authentication checks
        if authenticated_user.role != UserRoleEnum.BUYER:
            self._logger.warning(
                "Unauthorized user attempted to create an order.",
                user_id=authenticated_user.user_id,
                actor_role=authenticated_user.role,
            )
            raise InsufficientPermissionsException("Only buyers can create orders.")

        # Verify if items are provided
        if not command.items:
            self._logger.warning(
                "No items provided for order.", buyer_id=authenticated_user.user_id
            )
            raise OrderItemsRequiredException()

        # Verify if items are unique
        if len(command.items) != len(set(command.items)):
            self._logger.warning(
                "Duplicate items provided for order.",
                buyer_id=authenticated_user.user_id,
            )
            raise DuplicateOrderItemsException()

        async with self.order_management_unit_of_work as uow:
            # Find referenced products
            referenced_products = await uow.product_query.find_by_ids(
                [item.product_id for item in command.items]
            )

            # Verify if products are active
            inactive_product = [
                product.product_id
                for product in referenced_products
                if not product.is_active
            ]
            if inactive_product:
                self._logger.warning(
                    "Inactive product provided for order.",
                    buyer_id=authenticated_user.user_id,
                    inactive_product_ids=inactive_product,
                )
                raise InactiveReferencedProductException(inactive_product)

            # Verify if products are from the same supplier
            supplier_ids = {product.supplier_id for product in referenced_products}
            if len(supplier_ids) != 1:
                self._logger.warning(
                    "Multiple suppliers provided for order.",
                    buyer_id=authenticated_user.user_id,
                    supplier_ids=supplier_ids,
                )
                raise ProductsFromDifferentSuppliersException()

            # Get supplier ID
            supplier_id = next(iter(supplier_ids))

            # Create order and save it
            order_entity = OrderEntity.create(
                buyer_id=authenticated_user.user_id,
                supplier_id=supplier_id,
                status_order=OrderStatusEnum.DRAFT,
            )
            saved_order = await uow.orders.save(order_entity)

            # Create order items and save them
            order_items_entities = [
                OrderItemsEntity.create(
                    order_id=saved_order.id,
                    product_id=item.product_id,
                    quantity=QuantityVO(item.quantity),
                    unit_price=next(
                        product.unit_price
                        for product in referenced_products
                        if product.product_id == item.product_id
                    ),
                )
                for item in command.items
            ]
            await uow.order_items.save_many(order_items_entities)

            # Create order status history and save it
            order_status_history_entity = OrderStatusHistoryEntity.create(
                order_id=order_entity.id,
                previous_status=OrderStatusEnum.DRAFT,
                new_status=OrderStatusEnum.DRAFT,
                changed_by=authenticated_user.user_id,
                changed_by_role=authenticated_user.role,
            )
            await uow.orders_status_history.save(order_status_history_entity)

            await uow.commit()

        # Get products by ID
        products_by_id = {
            product.product_id: product for product in referenced_products
        }

        # Create response DTO for order items
        items_response = [
            ProductDetailsDto(
                product_id=item.product_id,
                name=products_by_id[item.product_id].name,
                quantity=item.quantity.value(),
                unit_price=item.unit_price,
            )
            for item in order_items_entities
        ]

        self._logger.info(
            "Order created successfully.",
            buyer_id=authenticated_user.user_id,
            order_id=saved_order.id,
            status=saved_order.status_order,
        )

        return CreateOrderResponseDTO(
            id=saved_order.id,
            buyer_id=saved_order.buyer_id,
            items=items_response,
            status=saved_order.status_order,
            created_at=saved_order.created_at,
            updated_at=saved_order.updated_at,
        )
