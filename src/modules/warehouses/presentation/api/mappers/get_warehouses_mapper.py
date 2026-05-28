"""This module contains the GetWarehouseApiMapper class."""

from src.modules.warehouses.application.dtos.get_warehouses_dto import (
    GetWarehousesResponseDto,
    WarehouseItemDto,
)
from src.modules.warehouses.presentation.api.schemas.get_warehouses_schema import (
    GetWarehousesResponseSchema,
    WarehouseItemSchema,
)


class GetWarehousesApiMapper:
    """This class maps GetWarehousesResponseDto to GetWarehousesResponseSchema."""

    @staticmethod
    def to_item(
        warehouse: WarehouseItemDto,
    ) -> WarehouseItemSchema:
        """Map a WarehouseItemDto to a WarehouseItemSchema.

        Args:
            warehouse (WarehouseItemDto): The WarehouseItemDto instance.

        Returns:
            WarehouseItemSchema: The WarehouseItemSchema instance.
        """
        return WarehouseItemSchema(
            id=str(warehouse.id),
            supplier_id=str(warehouse.supplier_id),
            name=warehouse.name,
            address=warehouse.address,
            is_active=warehouse.is_active,
            created_at=warehouse.created_at,
            updated_at=warehouse.updated_at,
        )

    @classmethod
    def to_response(
        cls,
        response: GetWarehousesResponseDto,
    ) -> GetWarehousesResponseSchema:
        """Map a GetWarehousesResponseDto to a GetWarehousesResponseSchema.

        Args:
            response (GetWarehousesResponseDto): The GetWarehousesResponseDto instance.

        Returns:
            GetWarehousesResponseSchema: The GetWarehousesResponseSchema instance.
        """
        return GetWarehousesResponseSchema(
            warehouses=[cls.to_item(warehouse) for warehouse in response.warehouses]
        )
