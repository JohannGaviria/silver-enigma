"""This module contains the CreateFirstAdminUseCase class."""

from src.modules.auth.application.dtos.create_first_admin_dto import (
    CreateFirstAdminCommand,
    CreateFirstAdminResponse,
)
from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.enums.user_role_enum import UserRoleEnum
from src.modules.auth.domain.exceptions.auth_exception import (
    AdminAlreadyExistsException,
)
from src.modules.auth.domain.ports.outbound.password_hash_outbound_port import (
    PasswordHashOutboundPort,
)
from src.modules.auth.domain.ports.repositories.user_repository_port import (
    UserRepositoryPort,
)
from src.modules.auth.domain.value_objects.email_vo import EmailVO
from src.modules.auth.domain.value_objects.name_vo import NameVO
from src.modules.auth.domain.value_objects.plain_password_vo import PlainPasswordVO


class CreateFirstAdminUseCase:
    """Use case for creating the first admin user in the system.

    This use case checks if an admin user already exists, and if not,
    it creates a new admin user with the provided details.
    """

    def __init__(
        self,
        user_repository: UserRepositoryPort,
        password_hash_outbound: PasswordHashOutboundPort,
    ) -> None:
        """Initializes the CreateFirstAdminUseCase with the required dependencies.

        Args:
            user_repository (UserRepositoryPort): The user repository for data operations.
            password_hash_outbound (PasswordHashOutboundPort): The service for hashing passwords.
        """
        self.user_repository = user_repository
        self.password_hash_outbound = password_hash_outbound

    async def execute(
        self, command: CreateFirstAdminCommand
    ) -> CreateFirstAdminResponse:
        """Executes the use case to create the first admin user.

        It checks if an admin already exists, and if not,
        it creates a new admin user with the provided details.

        Args:
            command (CreateFirstAdminCommand): The command containing the details
                for the new admin user.

        Returns:
            CreateFirstAdminResponse: The response containing the details
                of the created admin user.

        Raises:
            AdminAlreadyExistsException: If an admin user already exists in the system.
        """
        if await self.user_repository.exists_by_role(UserRoleEnum.ADMIN):
            raise AdminAlreadyExistsException()

        password_hash = self.password_hash_outbound.hash(
            PlainPasswordVO(command.plain_password)
        )

        user = UserEntity.create(
            name=NameVO(command.name),
            email=EmailVO(command.email),
            password=password_hash,
            role=UserRoleEnum.ADMIN,
        )

        user = await self.user_repository.save(user)

        return CreateFirstAdminResponse(
            id=user.id,
            name=str(user.name),
            email=str(user.email),
            role=user.role.value,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
