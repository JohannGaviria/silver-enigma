"""This module contains the ToggleWarehouseStatusSchema class."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ToggleWarehouseStatusRequestSchema(BaseModel):
    """Request schema for the toggle warehouse status endpoint.

    Attributes:
        is_active (bool): Whether the warehouse should be active or not.
    """

    is_active: bool

    model_config = {
        "json_schema_extra": {
            "example": {
                "is_active": False,
            }
        }
    }


class ToggleWarehouseStatusResponseSchema(BaseModel):
    """Response schema for the toggle warehouse status endpoint.

    Attributes:
        id (UUID): The ID of the warehouse.
        supplier_id (UUID): The ID of the supplier.
        name (str): The name of the warehouse.
        address (str): The address of the warehouse.
        is_active (bool): Whether the warehouse is active or not.
        created_at (datetime): The timestamp when the warehouse was created.
        updated_at (datetime): The timestamp when the warehouse was last updated.
    """

    id: UUID
    supplier_id: UUID
    name: str
    address: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "ad350ad6-240e-4b13-b120-3d94e4a1d4f5",
                "supplier_id": "a31a2bdc-6c80-4837-b045-2996d3a30d9f",
                "name": "Warehouse 1",
                "address": "123 Main St",
                "is_active": False,
                "created_at": "2026-05-28 20:04:26.765948+00:00",
                "updated_at": "2026-05-29 20:04:26.765948+00:00",
            }
        }
    }
