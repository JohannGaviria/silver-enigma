from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.infrastructure.persistence.repositories.sqlalchemy_user_repository_adapter import (
    SQLAlchemyUserRepositoryAdapter,
)
from src.modules.auth.infrastructure.persistence.unit_of_work.sqlalchemy_user_unit_of_work_adapter import (
    SQLAlchemyUserUnitOfWorkAdapter,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)


class TestSQLAlchemyUserUnitOfWorkAdapter:
    # ------------------------------------------------
    # __aenter__
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_aenter_returns_self(
        self, uow_with_session_mock: tuple[SQLAlchemyUserUnitOfWorkAdapter, AsyncMock]
    ) -> None:
        """``async with uow`` must return the UoW instance itself."""
        uow, _ = uow_with_session_mock

        async with uow as ctx:
            assert ctx is uow

    @pytest.mark.asyncio
    async def test_aenter_creates_session_from_factory(
        self,
        uow_with_session_mock: tuple[SQLAlchemyUserUnitOfWorkAdapter, AsyncMock],
        session_factory_mock: MagicMock,
    ) -> None:
        """The session factory must be called exactly once on entry."""
        uow, _ = uow_with_session_mock

        async with uow:
            session_factory_mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_aenter_exposes_users_repository(
        self, uow_with_session_mock: tuple[SQLAlchemyUserUnitOfWorkAdapter, AsyncMock]
    ) -> None:
        """``uow.users`` must be a ``SQLAlchemyUserRepositoryAdapter`` after entry."""
        uow, _ = uow_with_session_mock

        async with uow:
            assert isinstance(uow.users, SQLAlchemyUserRepositoryAdapter)

    @pytest.mark.asyncio
    async def test_aenter_binds_repository_to_current_session(
        self, uow_with_session_mock: tuple[SQLAlchemyUserUnitOfWorkAdapter, AsyncMock]
    ) -> None:
        """The ``users`` repository must use the session opened during entry."""
        uow, session_mock = uow_with_session_mock

        async with uow:
            assert isinstance(uow.users, SQLAlchemyUserRepositoryAdapter)
            assert uow.users.session is session_mock

    # ------------------------------------------------
    # __aexit__ — normal path (no exception)
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_aexit_closes_session_on_clean_exit(
        self, uow_with_session_mock: tuple[SQLAlchemyUserUnitOfWorkAdapter, AsyncMock]
    ) -> None:
        """The session must be closed when exiting without an exception."""
        uow, session_mock = uow_with_session_mock

        async with uow:
            pass

        session_mock.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_aexit_does_not_rollback_on_clean_exit(
        self, uow_with_session_mock: tuple[SQLAlchemyUserUnitOfWorkAdapter, AsyncMock]
    ) -> None:
        """Rollback must NOT be called when exiting without an exception."""
        uow, session_mock = uow_with_session_mock

        async with uow:
            pass

        session_mock.rollback.assert_not_awaited()

    # ------------------------------------------------
    # __aexit__ — exception path
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_aexit_rolls_back_on_unhandled_exception(
        self, uow_with_session_mock: tuple[SQLAlchemyUserUnitOfWorkAdapter, AsyncMock]
    ) -> None:
        """Rollback must be called when an exception escapes the ``async with`` block."""
        uow, session_mock = uow_with_session_mock

        with pytest.raises(RuntimeError):
            async with uow:
                raise RuntimeError("boom")

        session_mock.rollback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_aexit_closes_session_even_after_exception(
        self, uow_with_session_mock: tuple[SQLAlchemyUserUnitOfWorkAdapter, AsyncMock]
    ) -> None:
        """The session must be closed even when an exception escapes."""
        uow, session_mock = uow_with_session_mock

        with pytest.raises(RuntimeError):
            async with uow:
                raise RuntimeError("boom")

        session_mock.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_aexit_rollback_happens_before_close(
        self, logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter
    ) -> None:
        """Rollback must be awaited before close when an exception occurs."""
        call_order: list[str] = []

        session_mock = AsyncMock(spec=AsyncSession)
        session_mock.rollback = AsyncMock(
            side_effect=lambda: call_order.append("rollback")
        )
        session_mock.close = AsyncMock(side_effect=lambda: call_order.append("close"))

        factory_mock = MagicMock()
        factory_mock.return_value = session_mock

        uow = SQLAlchemyUserUnitOfWorkAdapter(
            session_factory=factory_mock,
            logger_factory_outbound=logger_factory_outbound,
        )

        with pytest.raises(ValueError):
            async with uow:
                raise ValueError("oops")

        assert call_order == ["rollback", "close"]

    # ------------------------------------------------
    # commit()
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_commit_delegates_to_session(
        self, uow_with_session_mock: tuple[SQLAlchemyUserUnitOfWorkAdapter, AsyncMock]
    ) -> None:
        """``commit()`` must call ``session.commit()`` exactly once."""
        uow, session_mock = uow_with_session_mock

        async with uow:
            await uow.commit()

        session_mock.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_commit_raises_runtime_error_when_called_outside_context(
        self, uow_with_session_mock: tuple[SQLAlchemyUserUnitOfWorkAdapter, AsyncMock]
    ) -> None:
        """Calling ``commit()`` outside ``async with`` must raise ``RuntimeError``."""
        uow, _ = uow_with_session_mock

        with pytest.raises(RuntimeError, match="async with"):
            await uow.commit()

    # ------------------------------------------------
    # rollback()
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_rollback_delegates_to_session(
        self, uow_with_session_mock: tuple[SQLAlchemyUserUnitOfWorkAdapter, AsyncMock]
    ) -> None:
        """``rollback()`` must call ``session.rollback()`` exactly once."""
        uow, session_mock = uow_with_session_mock

        async with uow:
            await uow.rollback()

        session_mock.rollback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_rollback_raises_runtime_error_when_called_outside_context(
        self, uow_with_session_mock: tuple[SQLAlchemyUserUnitOfWorkAdapter, AsyncMock]
    ) -> None:
        """Calling ``rollback()`` outside ``async with`` must raise ``RuntimeError``."""
        uow, _ = uow_with_session_mock

        with pytest.raises(RuntimeError, match="async with"):
            await uow.rollback()

    # ------------------------------------------------
    # Session isolation between uses
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_each_context_entry_creates_a_new_session(
        self, logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter
    ) -> None:
        """Entering the UoW context twice must create two separate sessions."""
        session1 = AsyncMock(spec=AsyncSession)
        session2 = AsyncMock(spec=AsyncSession)

        factory_mock = MagicMock()
        factory_mock.side_effect = [session1, session2]

        uow = SQLAlchemyUserUnitOfWorkAdapter(
            session_factory=factory_mock,
            logger_factory_outbound=logger_factory_outbound,
        )

        async with uow:
            assert isinstance(uow.users, SQLAlchemyUserRepositoryAdapter)
            first_session = uow.users.session

        async with uow:
            assert isinstance(uow.users, SQLAlchemyUserRepositoryAdapter)
            second_session = uow.users.session

        assert first_session is session1
        assert second_session is session2
        assert factory_mock.call_count == 2
