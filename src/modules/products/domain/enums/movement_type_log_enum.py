"""This module contains the MovementTypeLogEnum class."""

from enum import StrEnum


class MovementTypeLogEnum(StrEnum):
    """Enumeration of stock movement types for logging.

    This enumeration is used to represent the different types of stock movements
    that can occur in the system.

    Attributes:
        RESERVE (str): Reserves a quantity of a product in a warehouse.
        RELEASE (str): Releases a quantity of a product from a warehouse.
        DECREMENT (str): Decrements a quantity of a product in a warehouse.
    """

    RESERVE = "RESERVE"
    RELEASE = "RELEASE"
    DECREMENT = "DECREMENT"
