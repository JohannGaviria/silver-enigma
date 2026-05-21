"""This module contains the CreateFirstAdminUseCase class."""

from src.modules.auth.application.dtos.create_first_admin_dto import (
    CreateFirstAdminCommandDto,
    CreateFirstAdminResponseDto,
)
from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.exceptions.auth_exception import (
    AdminAlreadyExistsException,
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
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)
from src.shared.domain.ports.outbound.logger_outbound_port import LoggerOutboundPort


class CreateFirstAdminUseCase:
    """Use case for creating the first admin user in the system.

    This use case checks if an admin user already exists, and if not,
    it creates a new admin user with the provided details.
    """

    def __init__(
        self,
        unit_of_work: UserUnitOfWorkPort,
        password_hash_outbound: PasswordHashOutboundPort,
        logger_factory_outbound: LoggerFactoryOutboundPort,
    ) -> None:
        """Initializes the CreateFirstAdminUseCase with the required dependencies.

        Args:
            unit_of_work (UserUnitOfWorkPort): The unit of work that manages
                the transaction boundary and exposes auth repositories.
            password_hash_outbound (PasswordHashOutboundPort): The service for hashing passwords.
            logger_factory_outbound (LoggerFactoryOutboundPort): The factory for creating loggers.
        """
        self.unit_of_work = unit_of_work
        self.password_hash_outbound = password_hash_outbound
        self._logger: LoggerOutboundPort = logger_factory_outbound.get_logger(__name__)

    async def execute(
        self, command: CreateFirstAdminCommandDto
    ) -> CreateFirstAdminResponseDto:
        """Executes the use case to create the first admin user.

        Opens a Unit of Work, checks whether an admin already exists, creates
        and persists the new user, and commits — all within a single transaction.

        Args:
            command (CreateFirstAdminCommandDto): The command containing the details
                for the new admin user.

        Returns:
            CreateFirstAdminResponseDto: The response containing the details
                of the created admin user.

        Raises:
            AdminAlreadyExistsException: If an admin user already exists in the system.
            InvalidNameException: If the provided name does not meet validation rules.
            InvalidEmailException: If the provided email does not meet validation rules.
            InvalidPlainPasswordException: If the provided password does not meet
                security criteria.
        """
        self._logger.info("create first admin use case attempt")

        # Value Objects are validated eagerly at construction time, so domain
        # exceptions will propagate before we open the transaction.
        name = NameVO(command.name)
        email = EmailVO(command.email)
        plain_password = PlainPasswordVO(command.plain_password)

        async with self.unit_of_work as uow:
            if await uow.users.exists_by_role(UserRoleEnum.ADMIN):
                self._logger.warning(
                    "admin user already exists, cannot create another one"
                )
                raise AdminAlreadyExistsException()

            password_hash = self.password_hash_outbound.hash(plain_password)

            user = UserEntity.create(
                name=name,
                email=email,
                password=password_hash,
                role=UserRoleEnum.ADMIN,
            )

            user = await uow.users.save(user)
            await uow.commit()

        self._logger.info(f"admin user created with id: {user.id}")

        return CreateFirstAdminResponseDto(
            id=user.id,
            name=str(user.name),
            email=str(user.email),
            role=user.role.value,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
