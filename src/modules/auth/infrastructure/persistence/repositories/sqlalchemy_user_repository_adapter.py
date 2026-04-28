"""This module contains the SQLAlchemyUserRepositoryAdapter class."""

from sqlalchemy import exists, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.enums.user_role_enum import UserRoleEnum
from src.modules.auth.domain.exceptions.auth_exception import (
    UserAlreadyExistsException,
    UserRepositoryException,
)
from src.modules.auth.domain.ports.repositories.user_repository_port import (
    UserRepositoryPort,
)
from src.modules.auth.infrastructure.persistence.mappers.user_mapper import UserMapper
from src.modules.auth.infrastructure.persistence.models.user_model import UserModel
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class SQLAlchemyUserRepositoryAdapter(UserRepositoryPort):
    """Implements UserRepositoryPort using SQLAlchemy for database operations."""

    def __init__(
        self, session: AsyncSession, logger_factory_outbound: LoggerFactoryOutboundPort
    ) -> None:
        """Initializes the SQLAlchemyUserRepositoryAdapter.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session for database operations.
            logger_factory_outbound (LoggerFactoryOutboundPort): The logger factory for creating loggers.
        """
        self.session = session
        self._logger = logger_factory_outbound.get_logger(__name__)

    async def exists_by_role(self, role: UserRoleEnum) -> bool:
        """Checks if a user with the specified role exists in the database.

        Args:
            role (UserRoleEnum): The user role to check for existence.

        Returns:
            bool: True if a user with the specified role exists, False otherwise.

        Raises:
            UserRepositoryException: If a database error occurs during the query.
        """
        try:
            stmt = select(exists().where(UserModel.role == role.value))
            result = await self.session.execute(stmt)
            return bool(result.scalar())
        except SQLAlchemyError as e:
            self._logger.error(
                "Database error while checking existence by role", exc_info=str(e)
            )
            raise UserRepositoryException(
                "Database error while checking existence by role."
            ) from e

    async def save(self, entity: UserEntity) -> UserEntity:
        """Saves a UserEntity to the database and returns the saved entity.

        Args:
            entity (UserEntity): The user entity to be saved.

        Returns:
            UserEntity: The saved user entity.

        Raises:
            UserAlreadyExistsException: If a user with the same email already exists
                or violates constraints.
            UserRepositoryException: If a database error occurs during the save operation.
        """
        try:
            model = UserMapper.to_model(entity)

            self.session.add(model)
            await self.session.commit()
            await self.session.refresh(model)

            return UserMapper.to_entity(model)

        except IntegrityError as e:
            await self.session.rollback()
            self._logger.error("Integrity error while saving user", exc_info=str(e))
            raise UserAlreadyExistsException(
                "User already exists or violates constraints"
            ) from e

        except SQLAlchemyError as e:
            await self.session.rollback()
            self._logger.error("Database error while saving user", exc_info=str(e))
            raise UserRepositoryException("Database error during user creation.") from e
