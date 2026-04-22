"""This module defines standardized response schemas for API endpoints."""

from enum import StrEnum
from typing import Generic, TypeVar

from pydantic import BaseModel, Field


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
        details (list[str], optional): A list of detailed error messages.
    """

    status: StatusEnum = StatusEnum.ERROR
    message: str
    details: list[str] = Field(default_factory=list)
