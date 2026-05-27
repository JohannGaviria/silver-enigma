"""This module contains the schemas for creating a warehouse."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BaseCreateWarehouseSchema(BaseModel):
    """The base schema for creating a warehouse.

    Attributes:
        name (str): The name of the warehouse.
        address (str): The address of the warehouse.
    """

    name: str
    address: str


class CreateWarehouseRequestSchema(BaseCreateWarehouseSchema):
    """The request schema for creating a warehouse.

    Attributes:
        name (str): The name of the warehouse.
        address (str): The address of the warehouse.
    """

    ...

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Warehouse 1",
                "address": "Cl. 73 # 73a-226, Pilarica, Medellín, Robledo, Medellín, Antioquia",
            }
        }
    }


class CreateWarehouseResponseSchema(BaseCreateWarehouseSchema):
    """The response schema for creating a warehouse.

    Attributes:
        id (UUID): The unique identifier of the warehouse.
        supplier_id (UUID): The unique identifier of the supplier associated with the warehouse.
        name (str): The name of the warehouse.
        address (str): The address of the warehouse.
        is_active (bool): A flag indicating whether the warehouse is active or not.
        created_at (datetime): The date and time when the warehouse was created.
        updated_at (datetime): The date and time when the warehouse was last updated.
    """

    id: UUID
    supplier_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Warehouse 1",
                "address": "Cl. 73 # 73a-226, Pilarica, Medellín, Robledo, Medellín, Antioquia",
                "id": "c7f1d1b0-f0e2-4a0c-a3d9-e8a2e5e0f9e1",
                "supplier_id": "c7f1d1b0-f0e2-4a0c-a3d9-e8a2e5e0f9e1",
                "is_active": True,
                "created_at": "2023-03-14T15:22:00.000Z",
                "updated_at": "2023-03-14T15:22:00.000Z",
            }
        }
    }
