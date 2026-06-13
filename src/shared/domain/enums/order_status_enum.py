"""This module contains the OrderStatusEnum class."""

from enum import StrEnum


class OrderStatusEnum(StrEnum):
    """Enumeration of order status.

    This enumeration defines the possible order statuses
    and their corresponding values.

    Attributes:
        DRAFT (str): The draft order status.
        CONFIRMED (str): The confirmed order status.
        PROCESSING (str): The processing order status.
        SHIPPED (str): The shipped order status.
        DELIVERED (str): The delivered order status.
        CANCELLED (str): The cancelled order status.
    """

    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
