"""This module contains the schemas for the CreateOrder API."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class ProductItemSchema(BaseModel):
    """Schema for a product item in a create order request.

    Args:
        product_id (UUID): The product ID.
        quantity (int): The quantity of the product.
    """

    product_id: UUID
    quantity: int


class ProductDetailsSchema(ProductItemSchema):
    """Schema for a product details in a create order request.

    Args:
        product_id (UUID): The product ID.
        quantity (int): The quantity of the product.
        name (str): The name of the product.
        unit_price (Decimal): The unit price of the product.
    """

    name: str
    unit_price: Decimal


class CreateOrderRequestSchema(BaseModel):
    """Schema for a create order request.

    Args:
        items (list[ProductItem]): A list of product items in the order.
    """

    items: list[ProductItemSchema]

    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [
                    {
                        "product_id": "00000000-0000-0000-0000-000000000000",
                        "quantity": 1,
                    }
                ]
            }
        }
    }


class CreateOrderResponseSchema(BaseModel):
    """Schema for a create order response.

    Args:
        id (UUID): The ID of the order.
        buyer_id (UUID): The ID of the buyer.
        items (list[ProductDetailsDto]): A list of product details in the order.
        status (OrderStatusEnum): The status of the order.
        created_at (datetime): The timestamp when the order was created.
        updated_at (datetime): The timestamp when the order was last updated.
    """

    id: UUID
    buyer_id: UUID
    items: list[ProductDetailsSchema]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "00000000-0000-0000-0000-000000000000",
                "buyer_id": "00000000-0000-0000-0000-000000000000",
                "items": [
                    {
                        "product_id": "00000000-0000-0000-0000-000000000000",
                        "quantity": 1,
                        "name": "Product Name",
                        "unit_price": "100.00",
                    }
                ],
                "status": "DRAFT",
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00",
            }
        }
    }
