"""This module contains the RedisConnection class."""

import time
from threading import Lock

import redis
import structlog

from src.config import settings

logger = structlog.get_logger(__name__)


class RedisConnection:
    """Manages Redis client lifecycle with retry strategy."""

    _client: redis.Redis | None = None
    _lock = Lock()

    MAX_RETRIES = 3
    BASE_DELAY = 1.5  # exponential backoff base.

    @classmethod
    def get_client(cls) -> redis.Redis:
        """Get or create the Redis client with retry logic.

        Uses double-checked locking to ensure thread-safe lazy initialization
        with retries and exponential backoff on connection failures.

        Returns:
            redis.Redis: A connected Redis client instance.
        """
        if cls._client is None:
            with cls._lock:
                if cls._client is None:  # double-check locking.
                    logger.info(event="redis_client_create")
                    cls._client = cls._create_client()
        return cls._client

    @classmethod
    def _create_client(cls) -> redis.Redis:
        """Create a Redis client with retry logic and exponential backoff.

        Returns:
            redis.Redis: A connected Redis client instance.
        """
        # We capture the last exception to log it after exhausting all retries,
        # but we log each failure as a warning with the attempt number
        # for better visibility into transient issues.
        last_error = None

        for attempt in range(1, cls.MAX_RETRIES + 1):
            try:
                logger.debug(event="redis_connect_attempt", attempt=attempt)

                # Create a new Redis client instance with a short timeout
                # to fail fast on connection issues.
                client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    password=settings.REDIS_PASSWORD,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    health_check_interval=30,
                )

                client.ping()

                logger.info(event="redis_connected")
                return client

            except redis.RedisError as exc:
                # Capture the last error to log after exhausting retries,
                # but log each failure as a warning with the attempt number.
                last_error = exc

                logger.warning(
                    event="redis_connect_fail",
                    attempt=attempt,
                    error=str(exc),
                )

                time.sleep(cls.BASE_DELAY**attempt)  # exponential backoff.

        logger.error(event="redis_connect_exhausted", error=str(last_error))
        raise redis.RedisError(f"Redis connection failed: {last_error}")

    @classmethod
    def health_check(cls) -> bool:
        """Perform a health check by pinging the Redis server.

        Returns:
            bool: True if Redis is healthy, False otherwise.
        """
        try:
            # Use the existing client if available to avoid unnecessary reconnection's,
            # but allow it to raise if the connection is broken so we can attempt a retry.
            client = cls.get_client()

            client.ping()

            logger.debug(event="redis_health_ok")
            return True

        except redis.RedisError as exc:
            # Log the failure and attempt to reset the client in
            # case of a transient issue.
            logger.warning(event="redis_health_fail", error=str(exc))

            try:
                cls._client = cls._create_client()
                return True
            except redis.RedisError:
                return False

    @classmethod
    def close(cls) -> None:
        """Close the Redis client connection and reset state."""
        with cls._lock:
            if cls._client:
                logger.info(event="redis_close")
                cls._client.close()
            cls._client = None
