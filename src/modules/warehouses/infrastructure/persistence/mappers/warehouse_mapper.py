"""This module contains the WarehousePersistenceMapper class."""

from src.modules.warehouses.domain.entities.warehouse_entity import WarehouseEntity
from src.modules.warehouses.domain.value_objects.warehouse_address_vo import (
    WarehouseAddressVO,
)
from src.modules.warehouses.domain.value_objects.warehouse_name_vo import (
    WarehouseNameVO,
)
from src.modules.warehouses.infrastructure.persistence.models.warehouse_model import (
    WarehouseModel,
)


class WarehousePersistenceMapper:
    """Mapper class to convert between WarehouseEntity and WarehouseModel.

    This class provides static methods to map a WarehouseModel (database representation)
    to a WarehouseEntity (domain representation) and vice versa.
    """

    @staticmethod
    def to_entity(model: WarehouseModel) -> WarehouseEntity:
        """Maps a WarehouseModel to a WarehouseEntity.

        Args:
            model (WarehouseModel): The WarehouseModel to map.

        Returns:
            WarehouseEntity: The mapped WarehouseEntity.
        """
        return WarehouseEntity(
            id=model.id,
            supplier_id=model.supplier_id,
            name=WarehouseNameVO(model.name),
            address=WarehouseAddressVO(model.address),
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: WarehouseEntity) -> WarehouseModel:
        """Maps a WarehouseEntity to a WarehouseModel.

        Args:
            entity (WarehouseEntity): The WarehouseEntity to map.

        Returns:
            WarehouseModel: The mapped WarehouseModel.
        """
        return WarehouseModel(
            id=entity.id,
            supplier_id=entity.supplier_id,
            name=str(entity.name),
            address=str(entity.address),
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
