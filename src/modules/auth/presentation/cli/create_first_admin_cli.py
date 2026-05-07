"""This module contains the CLI script for creating the first admin user in the system."""

import asyncio
import sys
from pathlib import Path

from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


async def _run() -> None:
    """Main async function to run the CLI logic.

    This function initializes the necessary components and executes the use case to create the first admin user.
    It also handles exceptions and logs appropriate messages.

    Reads credentials from environment variables (via Settings):
        FIRST_ADMIN_NAME
        FIRST_ADMIN_EMAIL
        FIRST_ADMIN_PASSWORD
    """
    from src.config import settings
    from src.modules.auth.application.dtos.create_first_admin_dto import (
        CreateFirstAdminCommand,
    )
    from src.modules.auth.application.use_cases.create_first_admin_use_case import (
        CreateFirstAdminUseCase,
    )
    from src.modules.auth.domain.exceptions.auth_exception import (
        AdminAlreadyExistsException,
        InvalidEmailException,
        InvalidNameException,
        InvalidPlainPasswordException,
    )
    from src.modules.auth.infrastructure.outbound.argon2_password_hash_outbound_adapter import (
        Argon2PasswordHashOutboundAdapter,
    )
    from src.modules.auth.infrastructure.persistence.unit_of_work.sqlalchemy_user_unit_of_work_adapter import (
        SQLAlchemyUserUnitOfWorkAdapter,
    )
    from src.shared.infrastructure.database.database_engine import DatabaseEngine

    logger = StructlogLoggerFactoryOutboundAdapter().get_logger(__name__)

    engine = DatabaseEngine.get_engine()

    try:
        logger.info("Starting first-admin bootstrap process")

        logger_factory = StructlogLoggerFactoryOutboundAdapter()

        unit_of_work = SQLAlchemyUserUnitOfWorkAdapter(
            session_factory=DatabaseEngine.get_session_factory(),
            logger_factory_outbound=logger_factory,
        )

        password_hash_outbound = Argon2PasswordHashOutboundAdapter(
            time_cost=settings.TIME_COST,
            memory_cost=settings.MEMORY_COST,
            parallelism=settings.PARALLELISM,
        )

        use_case = CreateFirstAdminUseCase(
            unit_of_work=unit_of_work,
            password_hash_outbound=password_hash_outbound,
            logger_factory_outbound=logger_factory,
        )

        command = CreateFirstAdminCommand(
            name=settings.FIRST_ADMIN_NAME,
            email=settings.FIRST_ADMIN_EMAIL,
            plain_password=settings.FIRST_ADMIN_PASSWORD,
        )

        result = await use_case.execute(command)

        logger.info(
            "Admin user created successfully",
            id=result.id,
            name=result.name,
            email=result.email,
            role=result.role,
            created_at=result.created_at.isoformat(),
        )

    except AdminAlreadyExistsException as exc:
        logger.warning(
            "Admin user already exists",
            exc_info=str(exc),
        )

    except (
        InvalidNameException,
        InvalidEmailException,
        InvalidPlainPasswordException,
    ) as exc:
        errors = getattr(exc, "errors", [str(exc)])
        if isinstance(errors, str):
            errors = [errors]

        logger.error("Validation error(s) occurred", exc_info=errors)
        sys.exit(1)

    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error during first-admin bootstrap", exc_info=str(exc))
        sys.exit(1)

    finally:
        await engine.dispose()


def main() -> None:
    """Main entry point for the CLI script."""
    logger = StructlogLoggerFactoryOutboundAdapter().get_logger(__name__)
    logger.info("Running first-admin bootstrap CLI")

    asyncio.run(_run())


if __name__ == "__main__":
    main()
