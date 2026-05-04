"""This module contains the DTOs for the CreateFirstAdminUseCase."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class BaseCreateFirstAdmin:
    """Base DTO for the CreateFirstAdminUseCase.

    Containing common attributes for both command and response DTOs.

    Attributes:
        name (str): The name of the admin user.
        email (str): The email of the admin user.
    """

    name: str
    email: str


@dataclass(frozen=True)
class CreateFirstAdminCommand(BaseCreateFirstAdmin):
    """Command DTO for the CreateFirstAdminUseCase.

    Containing the details required to create the first admin user.

    Attributes:
        name (str): The name of the admin user to be created.
        email (str): The email of the admin user to be created.
        plain_password (str): The plain password for the admin user to be created.
    """

    plain_password: str


@dataclass(frozen=True)
class CreateFirstAdminResponse(BaseCreateFirstAdmin):
    """Response DTO for the CreateFirstAdminUseCase.

    Containing the details of the created admin user.

    Attributes:
        id (UUID): The unique identifier of the created admin user.
        name (str): The name of the created admin user.
        email (str): The email of the created admin user.
        role (str): The role of the created admin user (should be 'ADMIN').
        created_at (datetime): The timestamp when the admin user was created.
        updated_at (datetime): The timestamp when the admin user was last updated.
    """

    id: UUID
    role: str
    created_at: datetime
    updated_at: datetime
