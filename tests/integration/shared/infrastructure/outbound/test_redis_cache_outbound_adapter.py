import json
from unittest.mock import AsyncMock, Mock, patch

import pytest
from faker import Faker
from redis import RedisError

from src.shared.domain.exceptions.cache_exception import (
    CacheDeletionException,
    CacheRetrievalException,
    CacheStorageException,
)
from src.shared.domain.value_objects.cache_entry_vo import CacheEntryVO
from src.shared.domain.value_objects.cache_key_vo import CacheKeyVO
from src.shared.domain.value_objects.cache_ttl_vo import CacheTTLVO
from src.shared.infrastructure.outbound.redis_cache_outbound_adapter import (
    RedisCacheOutboundAdapter,
)
from tests.conftest import FakeCacheValueVO


class FakeInvalidSerializableCacheValueVO(FakeCacheValueVO):
    def to_dict(self) -> dict:
        return {
            "invalid": object(),
        }


class TestRedisCacheOutboundAdapter:
    # ---------------------------------------------------------------------------
    # Method: get
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_return_cache_value_when_key_exists(
        self,
        faker: Faker,
        cache_outbound: RedisCacheOutboundAdapter,
    ) -> None:
        """Test that the get method returns a cache value.

        when the cache key exists in Redis.
        """
        key = CacheKeyVO(f"cache:user:{faker.uuid4()}")
        value = FakeCacheValueVO(faker.company())

        await cache_outbound._redis_client.set(str(key), json.dumps(value.to_dict()))

        result = await cache_outbound.get(key)

        assert result
        assert result["value"] == value.value

    @pytest.mark.asyncio
    async def test_should_return_none_when_key_does_not_exist(
        self, faker: Faker, cache_outbound: RedisCacheOutboundAdapter
    ) -> None:
        """Test that the get method returns None.

        when the cache key does not exist in Redis.
        """
        result = await cache_outbound.get(CacheKeyVO(f"cache:user:{faker.uuid4()}"))

        assert not result

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_cached_json_is_invalid(
        self, faker: Faker, cache_outbound: RedisCacheOutboundAdapter
    ) -> None:
        """Test that the get method raises a CacheRetrievalException.

        when the cached value contains invalid JSON.
        """
        key = CacheKeyVO(f"cache:user:{faker.uuid4()}")

        await cache_outbound._redis_client.set(
            str(key),
            "{invalid-json",
        )

        with pytest.raises(CacheRetrievalException):
            await cache_outbound.get(key)

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_redis_error_occurs_during_retrieval(
        self, faker: Faker, cache_outbound: RedisCacheOutboundAdapter
    ) -> None:
        """Test that the get method raises a CacheRetrievalException.

        when a RedisError occurs during cache retrieval.
        """
        key = CacheKeyVO(f"cache:user:{faker.uuid4()}")

        with patch.object(
            cache_outbound._redis_client,
            "get",
            new=AsyncMock(side_effect=RedisError("boom")),
        ):
            with pytest.raises(CacheRetrievalException):
                await cache_outbound.get(key)

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_unexpected_error_occurs_during_retrieval(
        self, faker: Faker, cache_outbound: RedisCacheOutboundAdapter
    ) -> None:
        """Test that the get method raises a CacheRetrievalException.

        when an unexpected error occurs during cache retrieval.
        """
        key = CacheKeyVO(f"cache:user:{faker.uuid4()}")

        with patch.object(
            cache_outbound._redis_client,
            "get",
            new=AsyncMock(side_effect=Exception("boom")),
        ):
            with pytest.raises(CacheRetrievalException):
                await cache_outbound.get(key)

    @pytest.mark.asyncio
    async def test_should_call_factory_with_deserialized_data_when_cache_exists(
        self, faker: Faker, cache_outbound: RedisCacheOutboundAdapter
    ) -> None:
        """Test that the get method calls the factory with the deserialized cache data when.

        the cache entry exists.
        """
        key = CacheKeyVO(f"cache:user:{faker.uuid4()}")

        payload = {
            "value": faker.company(),
        }

        factory_mock = Mock(return_value=payload)

        cache_outbound._factory = factory_mock

        await cache_outbound._redis_client.set(
            str(key),
            json.dumps(payload),
        )

        result = await cache_outbound.get(key)

        factory_mock.assert_called_once_with(payload)

        assert result == payload

    # ---------------------------------------------------------------------------
    # Method: set
    # ---------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_should_store_cache_entry_when_entry_is_valid(
        self, faker: Faker, cache_outbound: RedisCacheOutboundAdapter
    ) -> None:
        """Test that the set method stores the cache entry in Redis.

        when the entry is valid.
        """
        key = CacheKeyVO(f"cache:user:{faker.uuid4()}")
        ttl = CacheTTLVO(faker.random_int())
        value = FakeCacheValueVO(faker.company())

        cache_entry_vo = CacheEntryVO(key=key, ttl=ttl, value=value)

        await cache_outbound.set(cache_entry_vo)

        result = await cache_outbound._redis_client.get(str(key))
        deserialized = json.loads(result)

        assert result
        assert deserialized["value"] == value.value

    @pytest.mark.asyncio
    async def test_should_serialize_cache_value_to_json_when_storing_entry(
        self,
        faker: Faker,
        cache_outbound: RedisCacheOutboundAdapter,
    ) -> None:
        """Test that the set method serializes the cache value to JSON.

        before storing it in Redis.
        """
        key = CacheKeyVO(f"cache:user:{faker.uuid4()}")
        ttl = CacheTTLVO(faker.random_int(min=60, max=3600))
        value = FakeCacheValueVO(faker.company())

        cache_entry_vo = CacheEntryVO(
            key=key,
            ttl=ttl,
            value=value,
        )

        await cache_outbound.set(cache_entry_vo)

        stored_value = await cache_outbound._redis_client.get(str(key))

        assert stored_value is not None

        deserialized = json.loads(stored_value)

        assert deserialized == value.to_dict()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_cache_value_serialization_fails(
        self,
        faker: Faker,
        cache_outbound: RedisCacheOutboundAdapter,
    ) -> None:
        """Test that the set method raises a CacheStorageException.

        when cache value serialization fails.
        """
        key = CacheKeyVO(f"cache:user:{faker.uuid4()}")
        ttl = CacheTTLVO(faker.random_int(min=60, max=3600))
        value = FakeInvalidSerializableCacheValueVO(faker.company())

        cache_entry_vo = CacheEntryVO(
            key=key,
            ttl=ttl,
            value=value,
        )

        with pytest.raises(CacheStorageException):
            await cache_outbound.set(cache_entry_vo)

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_redis_error_occurs_during_storage(
        self,
        faker: Faker,
        cache_outbound: RedisCacheOutboundAdapter,
    ) -> None:
        """Test that the set method raises a CacheStorageException.

        when a RedisError occurs during cache storage.
        """
        key = CacheKeyVO(f"cache:user:{faker.uuid4()}")
        ttl = CacheTTLVO(faker.random_int(min=60, max=3600))
        value = FakeCacheValueVO(faker.company())

        cache_entry_vo = CacheEntryVO(
            key=key,
            ttl=ttl,
            value=value,
        )

        with patch.object(
            cache_outbound._redis_client,
            "set",
            new=AsyncMock(side_effect=RedisError("boom")),
        ):
            with pytest.raises(CacheStorageException):
                await cache_outbound.set(cache_entry_vo)

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_unexpected_error_occurs_during_storage(
        self,
        faker: Faker,
        cache_outbound: RedisCacheOutboundAdapter,
    ) -> None:
        """Test that the set method raises a CacheStorageException.

        when an unexpected error occurs during cache storage.
        """
        key = CacheKeyVO(f"cache:user:{faker.uuid4()}")
        ttl = CacheTTLVO(faker.random_int(min=60, max=3600))
        value = FakeCacheValueVO(faker.company())

        cache_entry_vo = CacheEntryVO(
            key=key,
            ttl=ttl,
            value=value,
        )

        with patch.object(
            cache_outbound._redis_client,
            "set",
            new=AsyncMock(side_effect=Exception("boom")),
        ):
            with pytest.raises(CacheStorageException):
                await cache_outbound.set(cache_entry_vo)

    # ---------------------------------------------------------------------------
    # Method: delete
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_delete_cache_entry_when_key_exists(
        self,
        faker: Faker,
        cache_outbound: RedisCacheOutboundAdapter,
    ) -> None:
        """Test that the delete method removes the cache entry from Redis.

        when the cache key exists.
        """
        key = CacheKeyVO(f"cache:user:{faker.uuid4()}")
        ttl = CacheTTLVO(faker.random_int(min=60, max=3600))
        value = FakeCacheValueVO(faker.company())

        cache_entry_vo = CacheEntryVO(
            key=key,
            ttl=ttl,
            value=value,
        )

        await cache_outbound.set(cache_entry_vo)

        stored_before = await cache_outbound._redis_client.get(str(key))

        assert stored_before is not None

        await cache_outbound.delete(key)

        stored_after = await cache_outbound._redis_client.get(str(key))

        assert stored_after is None

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_redis_error_occurs_during_deletion(
        self,
        faker: Faker,
        cache_outbound: RedisCacheOutboundAdapter,
    ) -> None:
        """Test that the delete method raises a CacheDeletionException.

        when a RedisError occurs during cache deletion.
        """
        key = CacheKeyVO(f"cache:user:{faker.uuid4()}")

        with patch.object(
            cache_outbound._redis_client,
            "delete",
            new=AsyncMock(side_effect=RedisError("boom")),
        ):
            with pytest.raises(CacheDeletionException):
                await cache_outbound.delete(key)

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_unexpected_error_occurs_during_deletion(
        self,
        faker: Faker,
        cache_outbound: RedisCacheOutboundAdapter,
    ) -> None:
        """Test that the delete method raises a CacheDeletionException.

        when an unexpected error occurs during cache deletion.
        """
        key = CacheKeyVO(f"cache:user:{faker.uuid4()}")

        with patch.object(
            cache_outbound._redis_client,
            "delete",
            new=AsyncMock(side_effect=Exception("boom")),
        ):
            with pytest.raises(CacheDeletionException):
                await cache_outbound.delete(key)
