"""This module defines standardized response schemas for API endpoints."""

from enum import StrEnum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, field_validator


class StatusEnum(StrEnum):
    """Enumeration for response status types.

    Attributes:
        SUCCESS (str): Indicates a successful response.
        ERROR (str): Indicates an error response.
    """

    SUCCESS = "success"
    ERROR = "error"


# Define a generic type variable for the data payload
T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):  # noqa: UP046
    """Schema for successful responses.

    Attributes:
        status (StatusEnum): The status of the response, default is 'success'.
        message (str): A descriptive success message.
        data (T | None): The payload of the response, can be of any type.
    """

    status: StatusEnum = StatusEnum.SUCCESS
    message: str
    data: T | None = None


class ErrorsResponse(BaseModel):
    """Schema for error responses.

    Attributes:
        status (StatusEnum): The status of the response, default is 'error'.
        message (str): A descriptive error message.
        context (dict[str, Any] | None): Additional context information.
        details (list[str] | None): A list of detailed error messages.
    """

    status: StatusEnum = StatusEnum.ERROR
    message: str
    context: dict[str, Any] | None = None
    details: list[str] | None = None

    @field_validator("details", mode="before")
    @classmethod
    def normalize_details(cls, value: Any) -> list[str] | None:
        """Normalize the details field to a list of strings.

        Args:
            value (Any): The value of the details field.

        Returns:
            list[str] | None: The normalized details field.
        """
        if value is None:
            return None

        if isinstance(value, str):
            return [value]

        return value
