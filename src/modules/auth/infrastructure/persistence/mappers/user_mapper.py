"""This module contains the UserMapper class."""

from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.value_objects.email_vo import EmailVO
from src.modules.auth.domain.value_objects.name_vo import NameVO
from src.modules.auth.domain.value_objects.password_hash_vo import PasswordHashVO
from src.modules.auth.infrastructure.persistence.models.user_model import UserModel
from src.shared.domain.enums.user_role_enum import UserRoleEnum


class UserMapper:
    """Mapper class to convert between UserEntity and UserModel.

    This class provides static methods to map a UserModel (database representation)
    to a UserEntity (domain representation) and vice versa.
    """

    @staticmethod
    def to_entity(model: UserModel) -> UserEntity:
        """Maps a UserModel to a UserEntity.

        Args:
            model (UserModel): The UserModel to map.

        Returns:
            UserEntity: The mapped UserEntity.
        """
        return UserEntity(
            id=model.id,
            name=NameVO(model.name),
            email=EmailVO(model.email),
            password=PasswordHashVO(model.password),
            role=UserRoleEnum(model.role),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: UserEntity) -> UserModel:
        """Maps a UserEntity to a UserModel.

        Args:
            entity (UserEntity): The UserEntity to map.

        Returns:
            UserModel: The mapped UserModel.
        """
        return UserModel(
            id=entity.id,
            name=str(entity.name),
            email=str(entity.email),
            password=str(entity.password),
            role=entity.role.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
