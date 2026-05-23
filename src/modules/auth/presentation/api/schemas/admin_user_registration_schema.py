"""This module contains the schemas for the admin user registration endpoint."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.shared.domain.enums.user_role_enum import UserRoleEnum


class BaseAdminUserRegistrationSchema(BaseModel):
    """Base schema for the admin user registration.

    Attributes:
        name (str): The name of the registered user.
        email (str): The email of the registered user.
        role (UserRoleEnum): The role of the registered user.
    """

    name: str
    email: str
    role: UserRoleEnum


class AdminUserRegistrationRequestSchema(BaseAdminUserRegistrationSchema):
    """Schema for the admin user registration request body.

    Attributes:
        name (str): The name of the user to be registered.
        email (str): The email of the user to be registered.
        password (str): The plain password of the user to be registered.
        role (UserRoleEnum): The role of the user to be registered.
    """

    password: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "password": "SecurePass!23",
                "role": "ADMIN",
            }
        }
    }


class AdminUserRegistrationResponseSchema(BaseAdminUserRegistrationSchema):
    """Schema for the successful admin user registration response.

    Attributes:
        id (UUID): The ID of the registered user.
        name (str): The name of the registered user.
        email (str): The email of the registered user.
        role (UserRoleEnum): The role of the registered user.
        created_at (datetime): The creation timestamp of the registered user.
        updated_at (datetime): The update timestamp of the registered user.
    """

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "8530547c-a75f-4ed2-b085-084bd41af614",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "role": "ADMIN",
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00",
            }
        }
    }
