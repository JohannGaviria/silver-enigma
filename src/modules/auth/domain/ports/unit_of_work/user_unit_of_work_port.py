"""This module contains the UserUnitOfWorkPort interface."""

from abc import abstractmethod

from src.modules.auth.domain.ports.repositories.user_repository_port import (
    UserRepositoryPort,
)
from src.shared.domain.ports.unit_of_work.unit_of_work_port import UnitOfWorkPort


class UserUnitOfWorkPort(UnitOfWorkPort):
    """Unit of Work scoped to the auth module.

    Exposes the repositories that belong to the user bounded context so
    that application-layer use cases can access them through a single,
    transaction-aware entry point.

    Attributes:
        users (UserRepositoryPort): Repository for user aggregate operations.
    """

    users: UserRepositoryPort

    @abstractmethod
    async def __aenter__(self) -> "UserUnitOfWorkPort":
        """Enter the user unit of work context.

        Returns:
            UserUnitOfWorkPort: This instance, ready to use.
        """
        pass
