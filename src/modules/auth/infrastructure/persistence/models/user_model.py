"""This module contains the UserModel class."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.persistence.base_model import BaseModel


class UserModel(BaseModel):
    """SQLAlchemy model for the User entity.

    Attributes:
        id (UUID): Unique identifier for the user.
        name (str): The name of the user.
        email (str): The email of the user.
        password (str): The hashed password of the user.
        role (str): The role of the user (e.g., 'admin', 'user
        created_at (datetime): The timestamp when the user was created.
        updated_at (datetime): The timestamp when the user was last updated.
    """

    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(nullable=False, index=True)
