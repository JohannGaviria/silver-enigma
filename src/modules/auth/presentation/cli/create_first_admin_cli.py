"""This module contains the CLI script for creating the first admin user in the system."""

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


async def _run() -> None:
    """Main async function to run the CLI logic.

    This function initializes the necessary components and executes the use case to create the first admin user.
    It also handles exceptions and prints appropriate messages to the console.

    Reads credentials from environment variables (via Settings):
        FIRST_ADMIN_NAME     — Full name (first + last required)
        FIRST_ADMIN_EMAIL    — Email address
        FIRST_ADMIN_PASSWORD — Plain-text password
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
    from src.modules.auth.infrastructure.persistence.repositories.sqlalchemy_user_repository_adapter import (
        SQLAlchemyUserRepositoryAdapter,
    )
    from src.shared.infrastructure.database.database_engine import DatabaseEngine

    # Create an isolated engine and session — never shared with the app
    engine = DatabaseEngine.get_engine()
    session = DatabaseEngine.create_session()

    try:
        use_case = CreateFirstAdminUseCase(
            user_repository=SQLAlchemyUserRepositoryAdapter(session),
            password_hash_outbound=Argon2PasswordHashOutboundAdapter(),
        )

        command = CreateFirstAdminCommand(
            name=settings.FIRST_ADMIN_NAME,
            email=settings.FIRST_ADMIN_EMAIL,
            plain_password=settings.FIRST_ADMIN_PASSWORD,
        )

        result = await use_case.execute(command)

        print("\n  Admin user created successfully!")
        print(f"   ID         : {result.id}")
        print(f"   Name       : {result.name}")
        print(f"   Email      : {result.email}")
        print(f"   Role       : {result.role}")
        print(f"   Created at : {result.created_at.isoformat()}\n")

    except AdminAlreadyExistsException:
        print("\n  An admin user already exists — nothing to do.\n")

    except (
        InvalidNameException,
        InvalidEmailException,
        InvalidPlainPasswordException,
    ) as exc:
        errors: list[str] = getattr(exc, "errors", [str(exc)])
        if isinstance(errors, str):
            errors = [errors]
        print("\n  Validation error(s):")
        for err in errors:
            print(f"   • {err}")
        print()
        sys.exit(1)

    except Exception as exc:  # noqa: BLE001
        print(f"\n  Unexpected error: {exc}\n")
        sys.exit(1)

    finally:
        # Only close the session — disposing the engine here can deadlock
        # the threading.Lock inside DatabaseEngine when running in asyncio.
        # The OS reclaims all connections when the process exits anyway.
        await session.close()
        await engine.dispose()


def main() -> None:
    """Main entry point for the CLI script."""
    print("Running first-admin bootstrap…")
    asyncio.run(_run())


if __name__ == "__main__":
    main()
