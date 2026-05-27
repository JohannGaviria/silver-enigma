"""This module contains the AdminUserRegistrationUseCase class."""

from src.modules.auth.application.dtos.admin_user_registration_dto import (
    AdminUserRegistrationCommandDto,
    AdminUserRegistrationResponseDto,
)
from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.exceptions.user_exception import (
    UserAlreadyExistsException,
)
from src.modules.auth.domain.ports.outbound.password_hash_outbound_port import (
    PasswordHashOutboundPort,
)
from src.modules.auth.domain.ports.unit_of_work.user_unit_of_work_port import (
    UserUnitOfWorkPort,
)
from src.modules.auth.domain.value_objects.email_vo import EmailVO
from src.modules.auth.domain.value_objects.name_vo import NameVO
from src.modules.auth.domain.value_objects.plain_password_vo import PlainPasswordVO
from src.shared.application.dtos.authenticated_user_dto import (
    AuthenticatedUserCommandDto,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.session_exception import (
    InsufficientPermissionsException,
)
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class AdminUserRegistrationUseCase:
    """Use case for admin user registration in the system.

    This use case checks if an user already exists, and if not,
    it creates a new user with the provided details.
    """

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        user_unit_of_work: UserUnitOfWorkPort,
        password_hash_outbound: PasswordHashOutboundPort,
    ) -> None:
        """Initializes the AdminUserRegistrationUseCase with the required dependencies.

        Args:
            logger_factory_outbound (LoggerFactoryOutboundPort): The factory for creating loggers.
            user_unit_of_work (UserUnitOfWorkPort): The unit of work that manages
                the transaction boundary and exposes auth repositories.
            password_hash_outbound (PasswordHashOutboundPort): The service for hashing passwords.
        """
        self._logger = logger_factory_outbound.get_logger(__name__)
        self.user_unit_of_work = user_unit_of_work
        self.password_hash_outbound = password_hash_outbound

    async def execute(
        self,
        command: AdminUserRegistrationCommandDto,
        authenticated_user: AuthenticatedUserCommandDto,
    ) -> AdminUserRegistrationResponseDto:
        """Execute the use case so that the administrator registers a user.

        Opens a Unit of Work, checks whether the user already exists,
        and saves the user to the database — all within a single transaction.

        Args:
            command (AdminUserRegistrationCommandDto): The command containing the
                details for the new user.
            authenticated_user (AuthenticatedUserCommandDto): The authenticated user for the
                current session.

        Returns:
            AdminUserRegistrationResponseDto: The response containing the details of
                the created user.

        Raises:
            UserAlreadyExistsException: If the user already exists in the system.
        """
        self._logger.info(
            "Executing admin user registration use case", email=command.email
        )

        # Authorization check
        if authenticated_user.role != UserRoleEnum.ADMIN:
            self._logger.warning(
                "Unauthorized registration attempt",
                actor_role=authenticated_user.role,
            )
            raise InsufficientPermissionsException(
                "Only administrators can register users."
            )

        # Value Objects are validated eagerly at construction time, so domain
        # exceptions will propagate before we open the transaction.
        name = NameVO(command.name)
        email = EmailVO(command.email)
        plain_password = PlainPasswordVO(command.password)

        async with self.user_unit_of_work as uow:
            # Check if the user already exists
            if await uow.users.find_by_email(email):
                self._logger.warning("User already exists.", email=email)
                raise UserAlreadyExistsException("The user already exists.")

            password_hash = self.password_hash_outbound.hash(plain_password)

            entity = UserEntity.create(
                name=name, email=email, password=password_hash, role=command.role
            )

            # Save the user to the database
            user = await uow.users.save(entity)

            await uow.commit()

        self._logger.info("User registered successfully", user_id=str(user.id))

        return AdminUserRegistrationResponseDto(
            id=user.id,
            name=str(user.name),
            email=str(user.email),
            role=user.role,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
