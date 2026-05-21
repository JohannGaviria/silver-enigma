"""This module contains the UserRoleEnum class."""

from enum import StrEnum


class UserRoleEnum(StrEnum):
    """Enumeration representing the different user roles in the system.

    This enumeration defines the possible roles that a user can have, which are:
    - SUPPLIER: Represents a user who supplies products or services.
    - BUYER: Represents a user who purchases products or services.
    - ADMIN: Represents a user with administrative privileges who can manage the system.

    Attributes:
        SUPPLIER (str): The role for users who supply products or services.
        BUYER (str): The role for users who purchase products or services.
        ADMIN (str): The role for users with administrative privileges.
    """

    SUPPLIER = "SUPPLIER"
    BUYER = "BUYER"
    ADMIN = "ADMIN"
