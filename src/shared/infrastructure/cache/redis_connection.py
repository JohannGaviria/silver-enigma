"""Async Redis connection manager."""

import asyncio
import inspect

import redis.exceptions
import structlog
from redis.asyncio import Redis

from src.config import settings

logger = structlog.get_logger(__name__)


class RedisConnection:
    """Manages async Redis client lifecycle with retry strategy."""

    _client: Redis | None = None
    _lock = asyncio.Lock()

    MAX_RETRIES = 3
    BASE_DELAY = 1.5

    @classmethod
    async def get_client(cls) -> Redis:
        """Get or create async Redis client."""
        if cls._client is None:
            async with cls._lock:
                if cls._client is None:
                    logger.info(event="redis_client_create")
                    cls._client = await cls._create_client()

        return cls._client

    @classmethod
    async def _create_client(cls) -> Redis:
        """Create Redis client with retry logic."""
        last_error = None

        for attempt in range(1, cls.MAX_RETRIES + 1):
            try:
                logger.debug(
                    event="redis_connect_attempt",
                    attempt=attempt,
                )

                client = Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    password=settings.REDIS_PASSWORD,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    health_check_interval=30,
                )

                ping_result = client.ping()

                if inspect.isawaitable(ping_result):
                    await ping_result

                logger.info(event="redis_connected")

                return client

            except redis.exceptions.RedisError as exc:
                last_error = exc

                logger.warning(
                    event="redis_connect_fail",
                    attempt=attempt,
                    error=str(exc),
                )

                await asyncio.sleep(cls.BASE_DELAY**attempt)

        logger.error(
            event="redis_connect_exhausted",
            error=str(last_error),
        )

        raise redis.exceptions.RedisError(f"Redis connection failed: {last_error}")

    @classmethod
    async def health_check(cls) -> bool:
        """Perform async health check."""
        try:
            client = await cls.get_client()

            ping_result = client.ping()

            if inspect.isawaitable(ping_result):
                await ping_result

            logger.debug(event="redis_health_ok")

            return True

        except redis.exceptions.RedisError as exc:
            logger.warning(
                event="redis_health_fail",
                error=str(exc),
            )

            try:
                cls._client = await cls._create_client()

                return True

            except redis.exceptions.RedisError:
                return False

    @classmethod
    async def close(cls) -> None:
        """Close Redis connection."""
        async with cls._lock:
            if cls._client:
                logger.info(event="redis_close")

                await cls._client.aclose()

            cls._client = None
