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
from src.modules.auth.domain.value_objects.email_vo import EmailVO
from src.modules.auth.infrastructure.persistence.mappers.user_mapper import UserMapper
from src.modules.auth.infrastructure.persistence.models.user_model import UserModel
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class SQLAlchemyUserRepositoryAdapter(UserRepositoryPort):
    """Implements UserRepositoryPort using SQLAlchemy for database operations.

    This adapter participates in the Unit of Work pattern: it never calls
    ``session.commit()`` or ``session.rollback()`` directly. Transaction
    control is the exclusive responsibility of the
    :class:`SQLAlchemyAuthUnitOfWorkAdapter` that owns the session.
    """

    def __init__(
        self, session: AsyncSession, logger_factory_outbound: LoggerFactoryOutboundPort
    ) -> None:
        """Initializes the SQLAlchemyUserRepositoryAdapter.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session provided
                by the Unit of Work.
            logger_factory_outbound (LoggerFactoryOutboundPort): The logger factory
                for creating loggers.
        """
        self.session = session
        self._logger = logger_factory_outbound.get_logger(__name__)

    async def find_by_email(self, email: EmailVO) -> UserEntity | None:
        """Finds a user by email.

        Args:
            email (EmailVO): The email to search for.

        Returns:
            UserEntity | None: The user entity if found, otherwise None.

        Raises:
            UserRepositoryException: If a database error occurs during the query.
        """
        try:
            stmt = select(UserModel).where(UserModel.email == str(email))
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            return UserMapper.to_entity(model) if model else None

        except SQLAlchemyError as e:
            self._logger.error(
                "Database error while finding user by email",
                exc_info=e,
            )

            raise UserRepositoryException(
                "Database error while finding user by email."
            ) from e

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
        """Persists a UserEntity within the current transaction and returns it.

        Args:
            entity (UserEntity): The user entity to be saved.

        Returns:
            UserEntity: The flushed user entity, with any server-generated
                fields (e.g. ``created_at``) populated.

        Raises:
            UserAlreadyExistsException: If a user with the same email already
                exists or a unique constraint is violated.
            UserRepositoryException: If any other database error occurs.
        """
        try:
            model = UserMapper.to_model(entity)
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)
            return UserMapper.to_entity(model)

        except IntegrityError as e:
            self._logger.error("Integrity error while saving user", exc_info=str(e))
            raise UserAlreadyExistsException(
                "User already exists or violates constraints"
            ) from e

        except SQLAlchemyError as e:
            self._logger.error("Database error while saving user", exc_info=str(e))
            raise UserRepositoryException("Database error during user creation.") from e
