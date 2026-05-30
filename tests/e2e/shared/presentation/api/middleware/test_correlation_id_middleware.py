from uuid import UUID

import pytest
import structlog
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from starlette.responses import PlainTextResponse

from src.shared.presentation.api.middleware.correlation_id_middleware import (
    CorrelationIdMiddleware,
)

HEADER_NAME = "X-Correlation-ID"


def _build_app() -> FastAPI:
    """Return a minimal FastAPI app with the middleware attached and one test route."""
    app = FastAPI()
    app.add_middleware(CorrelationIdMiddleware)

    @app.get("/ping")
    async def ping() -> PlainTextResponse:
        return PlainTextResponse("pong")

    return app


class TestCorrelationIdMiddleware:
    @pytest.mark.asyncio
    async def test_should_echo_correlation_id_provided_in_request_header(self) -> None:
        """When the client sends X-Correlation-ID, the response must carry the same value."""
        app = _build_app()
        correlation_id = "test-correlation-id-1234"

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/ping", headers={HEADER_NAME: correlation_id})

        assert response.status_code == 200
        assert response.headers[HEADER_NAME.lower()] == correlation_id

    @pytest.mark.asyncio
    async def test_should_generate_correlation_id_when_header_is_absent(self) -> None:
        """When no X-Correlation-ID header is sent, the middleware must generate one."""
        app = _build_app()

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/ping")

        assert response.status_code == 200
        assert HEADER_NAME.lower() in response.headers

    @pytest.mark.asyncio
    async def test_should_generate_valid_uuid_when_header_is_absent(self) -> None:
        """The auto-generated correlation ID must be a valid UUID v4."""
        app = _build_app()

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/ping")

        generated_id = response.headers[HEADER_NAME.lower()]

        UUID(generated_id)

    @pytest.mark.asyncio
    async def test_should_generate_unique_correlation_ids_across_requests(
        self,
    ) -> None:
        """Each request without a header must receive a different correlation ID."""
        app = _build_app()

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            first = await client.get("/ping")
            second = await client.get("/ping")

        first_id = first.headers[HEADER_NAME.lower()]
        second_id = second.headers[HEADER_NAME.lower()]

        assert first_id != second_id

    @pytest.mark.asyncio
    async def test_should_preserve_correlation_id_across_multiple_requests_with_same_id(
        self,
    ) -> None:
        """Sending the same ID on two requests must produce the same ID in both responses."""
        app = _build_app()
        correlation_id = "stable-id-across-calls"

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            first = await client.get("/ping", headers={HEADER_NAME: correlation_id})
            second = await client.get("/ping", headers={HEADER_NAME: correlation_id})

        assert first.headers[HEADER_NAME.lower()] == correlation_id
        assert second.headers[HEADER_NAME.lower()] == correlation_id

    @pytest.mark.asyncio
    async def test_should_bind_correlation_id_to_structlog_context(self) -> None:
        """The middleware must bind the correlation_id to the structlog context vars."""
        app = FastAPI()
        app.add_middleware(CorrelationIdMiddleware)

        captured: dict = {}

        @app.get("/capture")
        async def capture() -> PlainTextResponse:
            captured.update(structlog.contextvars.get_contextvars())
            return PlainTextResponse("ok")

        correlation_id = "structlog-binding-test"

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            await client.get("/capture", headers={HEADER_NAME: correlation_id})

        assert captured.get("correlation_id") == correlation_id

    @pytest.mark.asyncio
    async def test_should_bind_generated_id_to_structlog_context_when_header_absent(
        self,
    ) -> None:
        """When the middleware auto-generates an ID it must still bind it to structlog."""
        app = FastAPI()
        app.add_middleware(CorrelationIdMiddleware)

        captured: dict = {}

        @app.get("/capture")
        async def capture() -> PlainTextResponse:
            captured.update(structlog.contextvars.get_contextvars())
            return PlainTextResponse("ok")

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/capture")

        response_id = response.headers[HEADER_NAME.lower()]
        assert captured.get("correlation_id") == response_id

    @pytest.mark.asyncio
    async def test_should_clear_structlog_context_before_binding_new_id(self) -> None:
        """The middleware must call clear_contextvars() so stale context from a previous.

        request does not bleed into the current one.
        """
        app = FastAPI()
        app.add_middleware(CorrelationIdMiddleware)

        first_captured: dict = {}
        second_captured: dict = {}
        call_count = 0

        @app.get("/capture")
        async def capture() -> PlainTextResponse:
            nonlocal call_count
            call_count += 1
            ctx = structlog.contextvars.get_contextvars()
            if call_count == 1:
                first_captured.update(ctx)
            else:
                second_captured.update(ctx)
            return PlainTextResponse("ok")

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            await client.get("/capture", headers={HEADER_NAME: "first-id"})
            await client.get("/capture", headers={HEADER_NAME: "second-id"})

        assert first_captured["correlation_id"] == "first-id"
        assert second_captured["correlation_id"] == "second-id"

    @pytest.mark.asyncio
    async def test_should_handle_empty_string_correlation_id_by_generating_new_one(
        self,
    ) -> None:
        """An empty-string header is falsy, so the middleware generates a fresh UUID."""
        app = _build_app()

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/ping", headers={HEADER_NAME: ""})

        generated_id = response.headers[HEADER_NAME.lower()]

        UUID(generated_id)

    @pytest.mark.asyncio
    async def test_should_return_200_for_normal_request(self) -> None:
        """The middleware must not interfere with normal request processing."""
        app = _build_app()

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/ping")

        assert response.status_code == 200
        assert response.text == "pong"

    @pytest.mark.asyncio
    async def test_should_forward_correlation_id_header_name_constant(self) -> None:
        """HEADER_NAME class attribute must be the canonical casing used in the spec."""
        assert CorrelationIdMiddleware.HEADER_NAME == "X-Correlation-ID"
