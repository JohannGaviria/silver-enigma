"""This module contains the OrderManagementUnitOfWorkPort class."""

from abc import abstractmethod

from src.modules.orders.domain.ports.repositories.order_items_repository_port import (
    OrderItemsRepositoryPort,
)
from src.modules.orders.domain.ports.repositories.order_repository_port import (
    OrderRepositoryPort,
)
from src.modules.orders.domain.ports.repositories.order_status_history_repository_port import (
    OrderStatusHistoryRepositoryPort,
)
from src.modules.orders.domain.ports.repositories.product_query_repository_port import (
    ProductQueryRepositoryPort,
)
from src.shared.domain.ports.unit_of_work.unit_of_work_port import UnitOfWorkPort


class OrderManagementUnitOfWorkPort(UnitOfWorkPort):
    """Unit of work port for order management.

    Exposes the repositories that belong to the orders, order items, order
    status history, and product query bounded contexts so that application-layer
    use cases can access them through a single, transaction-aware entry point.

    Attributes:
        orders (OrderRepositoryPort): The order repository.
        order_items (OrderItemsRepositoryPort): The order items repository.
        orders_status_history (OrderStatusHistoryRepositoryPort): The order status history repository.
        product_query (ProductQueryRepositoryPort): The product query repository.
    """

    orders: OrderRepositoryPort
    order_items: OrderItemsRepositoryPort
    orders_status_history: OrderStatusHistoryRepositoryPort
    product_query: ProductQueryRepositoryPort

    @abstractmethod
    async def __aenter__(self) -> "OrderManagementUnitOfWorkPort":
        """Enter the context managed by the unit of work.

        Returns:
            OrderManagementUnitOfWorkPort: The unit of work context.
        """
        pass
