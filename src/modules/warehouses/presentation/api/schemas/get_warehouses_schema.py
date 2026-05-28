"""This module contains the get warehouses schema."""

from datetime import datetime

from pydantic import BaseModel


class WarehouseItemSchema(BaseModel):
    """Schema for a warehouse item.

    Attributes:
        id (UUID): The ID of the warehouse item.
        supplier_id (UUID): The ID of the supplier that owns the warehouse item.
        name (str): The name of the warehouse item.
        address (str): The address of the warehouse item.
        is_active (bool): Whether the warehouse item is active or not.
        created_at (datetime): The date and time when the warehouse item was created.
        updated_at (datetime): The date and time when the warehouse item was last updated.
    """

    id: str
    supplier_id: str
    name: str
    address: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class GetWarehousesResponseSchema(BaseModel):
    """Schema for the get warehouses response.

    Attributes:
        warehouses (list[WarehouseItemSchema]): A list of warehouse items.
    """

    warehouses: list[WarehouseItemSchema]

    model_config = {
        "json_schema_extra": {
            "example": {
                "warehouses": [
                    {
                        "id": "ad350ad6-240e-4b13-b120-3d94e4a1d4f5",
                        "supplier_id": "a31a2bdc-6c80-4837-b045-2996d3a30d9f",
                        "name": "Warehouse 1",
                        "address": "123 Main St",
                        "is_active": True,
                        "created_at": "2023-01-01T00:00:00",
                        "updated_at": "2023-01-01T00:00:00",
                    },
                    {
                        "id": "96de0dd7-8972-4737-8618-dd58bc659e50",
                        "supplier_id": "a31a2bdc-6c80-4837-b045-2996d3a30d9f",
                        "name": "Warehouse 2",
                        "address": "456 Main St",
                        "is_active": True,
                        "created_at": "2023-01-01T00:00:00",
                        "updated_at": "2023-01-01T00:00:00",
                    },
                ]
            }
        }
    }
