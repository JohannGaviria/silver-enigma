"""This module contains the use case composition for the auth module."""

from fastapi import Depends

from src.modules.auth.application.use_cases.admin_user_registration_use_case import (
    AdminUserRegistrationUseCase,
)
from src.modules.auth.application.use_cases.user_authentication_use_case import (
    UserAuthenticationUseCase,
)
from src.modules.auth.domain.value_objects.refresh_token_cache_value_vo import (
    RefreshTokenCacheValueVO,
)
from src.modules.auth.infrastructure.outbound.argon2_password_hash_outbound_adapter import (
    Argon2PasswordHashOutboundAdapter,
)
from src.modules.auth.infrastructure.persistence.unit_of_work.sqlalchemy_user_unit_of_work_adapter import (
    SQLAlchemyUserUnitOfWorkAdapter,
)
from src.modules.auth.presentation.api.compositions.infrastructure_composition import (
    get_password_hash_outbound,
    get_refresh_token_cache_outbound,
    get_user_uow,
)
from src.shared.infrastructure.outbound.pyjwt_token_outbound_adapter import (
    PyJWTTokenOutboundAdapter,
)
from src.shared.infrastructure.outbound.redis_cache_outbound_adapter import (
    RedisCacheOutboundAdapter,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.compositions.infrastructure_composition import (
    get_logger_factory_outbound,
    get_token_outbound,
)


def get_user_authentication_use_case(
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter = Depends(
        get_logger_factory_outbound
    ),
    unit_of_work: SQLAlchemyUserUnitOfWorkAdapter = Depends(get_user_uow),
    password_hash_outbound: Argon2PasswordHashOutboundAdapter = Depends(
        get_password_hash_outbound
    ),
    token_outbound: PyJWTTokenOutboundAdapter = Depends(get_token_outbound),
    cache_outbound: RedisCacheOutboundAdapter[RefreshTokenCacheValueVO] = Depends(
        get_refresh_token_cache_outbound
    ),
) -> UserAuthenticationUseCase:
    """Get the UserAuthenticationUseCase instance.

    Args:
        logger_factory_outbound (StructlogLoggerFactoryOutboundAdapter): The logger factory
            for creating loggers.
        unit_of_work (SQLAlchemyUserUnitOfWorkAdapter): The SQLAlchemy user unit of work adapter.
        password_hash_outbound (Argon2PasswordHashOutboundAdapter): The password hash
            outbound adapter.
        token_outbound (PyJWTTokenOutboundAdapter): The token outbound adapter.
        cache_outbound (RedisCacheOutboundAdapter[RefreshTokenCacheValueVO]): The cache outbound
            adapter.

    Returns:
        UserAuthenticationUseCase: The UserAuthenticationUseCase instance.
    """
    return UserAuthenticationUseCase(
        logger_factory_outbound=logger_factory_outbound,
        unit_of_work=unit_of_work,
        password_hash_outbound=password_hash_outbound,
        token_outbound=token_outbound,
        cache_outbound=cache_outbound,
    )


def get_admin_user_registration_use_case(
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter = Depends(
        get_logger_factory_outbound
    ),
    user_unit_of_work: SQLAlchemyUserUnitOfWorkAdapter = Depends(get_user_uow),
    password_hash_outbound: Argon2PasswordHashOutboundAdapter = Depends(
        get_password_hash_outbound
    ),
) -> AdminUserRegistrationUseCase:
    """Get the AdminUserRegistrationUseCase instance.

    Args:
        logger_factory_outbound (StructlogLoggerFactoryOutboundAdapter): The logger factory
            for creating loggers.
        user_unit_of_work (SQLAlchemyUserUnitOfWorkAdapter): The SQLAlchemy user unit of work adapter.
        password_hash_outbound (Argon2PasswordHashOutboundAdapter): The password hash
            outbound adapter.

    Returns:
        AdminUserRegistrationUseCase: The AdminUserRegistrationUseCase instance.
    """
    return AdminUserRegistrationUseCase(
        logger_factory_outbound=logger_factory_outbound,
        user_unit_of_work=user_unit_of_work,
        password_hash_outbound=password_hash_outbound,
    )
