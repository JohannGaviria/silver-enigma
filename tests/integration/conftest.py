import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.infrastructure.persistence.unit_of_work.sqlalchemy_user_unit_of_work_adapter import (
    SQLAlchemyUserUnitOfWorkAdapter,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)


@pytest.fixture()
def pinned_uow(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> SQLAlchemyUserUnitOfWorkAdapter:
    """Provide a UoW pinned to the test ``db_session``.

    All writes go through the same connection that the conftest transaction
    controls, so they are rolled back automatically at teardown.

    Args:
        db_session: The ``AsyncSession`` provided by the root conftest fixture.
        logger_factory_outbound: Structlog logger factory.

    Returns:
        SQLAlchemyUserUnitOfWorkAdapter: A UoW ready for integration assertions.
    """

    class _FixedSessionMaker:
        def __call__(self) -> AsyncSession:
            return db_session

    return SQLAlchemyUserUnitOfWorkAdapter(
        session_factory=_FixedSessionMaker(),  # type: ignore[arg-type]
        logger_factory_outbound=logger_factory_outbound,
    )
