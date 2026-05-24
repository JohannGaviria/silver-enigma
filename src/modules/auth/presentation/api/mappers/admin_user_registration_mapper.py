"""This module contains mappers for the AdminUserRegistration class."""

from src.modules.auth.application.dtos.admin_user_registration_dto import (
    AdminUserRegistrationCommandDto,
    AdminUserRegistrationResponseDto,
)
from src.modules.auth.presentation.api.schemas.admin_user_registration_schema import (
    AdminUserRegistrationRequestSchema,
    AdminUserRegistrationResponseSchema,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum


class AdminUserRegistrationApiMapper:
    """Mapper for the AdminUserRegistrationSchema to AdminUserRegistrationDto."""

    @staticmethod
    def to_command(
        request: AdminUserRegistrationRequestSchema,
        actor_role: UserRoleEnum,
    ) -> AdminUserRegistrationCommandDto:
        """Convert a AdminUserRegistrationRequestSchema to a AdminUserRegistrationCommandDto.

        Args:
            request (AdminUserRegistrationRequestSchema):
                The AdminUserRegistrationRequestSchema instance.
            actor_role (UserRoleEnum): The role of the user performing the registration.

        Returns:
            AdminUserRegistrationCommandDto: The AdminUserRegistrationCommandDto instance.
        """
        return AdminUserRegistrationCommandDto(
            name=request.name,
            email=request.email,
            password=request.password,
            role=request.role,
            actor_role=actor_role,
        )

    @staticmethod
    def to_response(
        command: AdminUserRegistrationResponseDto,
    ) -> AdminUserRegistrationResponseSchema:
        """Convert a AdminUserRegistrationResponseDto to a AdminUserRegistrationResponseSchema.

        Args:
            command (AdminUserRegistrationResponseDto): The AdminUserRegistrationResponseDto instance.

        Returns:
            AdminUserRegistrationResponseSchema: The AdminUserRegistrationResponseSchema instance.
        """
        return AdminUserRegistrationResponseSchema(
            id=command.id,
            name=command.name,
            email=command.email,
            role=command.role,
            created_at=command.created_at,
            updated_at=command.updated_at,
        )
