"""This module defines standardized response schemas for API endpoints."""

from enum import StrEnum
from typing import Any, TypeVar

from pydantic import BaseModel, field_validator


class StatusEnum(StrEnum):
    """Enumeration for response status types.

    Attributes:
        SUCCESS (str): Indicates a successful response.
        ERROR (str): Indicates an error response.
    """

    SUCCESS = "success"
    ERROR = "error"


ResponseSchemaTypeVar = TypeVar("ResponseSchemaTypeVar", bound=BaseModel)


class SuccessResponseSchema[ResponseSchemaTypeVar](BaseModel):
    """Schema for successful responses.

    Attributes:
        status (StatusEnum): The status of the response, default is 'success'.
        message (str): A descriptive success message.
        data
    """

    status: StatusEnum = StatusEnum.SUCCESS
    message: str
    data: ResponseSchemaTypeVar | None = None


class ErrorsResponseSchema(BaseModel):
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
