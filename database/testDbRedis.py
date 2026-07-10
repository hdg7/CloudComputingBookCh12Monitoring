import pytest
import json
from unittest.mock import AsyncMock, patch

from dbRedis import handle_message, REDIS_URL

@pytest.mark.asyncio
async def test_handle_message_create(monkeypatch):
    # Mock db functions
    monkeypatch.setattr("dbRedis.create_detection", lambda **kwargs: None)
    monkeypatch.setattr("dbRedis.read_detections", lambda: [("mocked",)])

    # Mock Redis client
    fake_redis = AsyncMock()
    monkeypatch.setattr("aioredis.from_url", AsyncMock(return_value=fake_redis))

    # Prepare message
    message = json.dumps({
        "action": "create_detection",
        "data": {
            "label": "car",
            "confidence": 0.95,
            "x1": 10, "y1": 20, "x2": 30, "y2": 40,
            "image_path": "image.jpg"
        }
    })

    await handle_message(message)

    # Assert Redis set called
    fake_redis.set.assert_called_once()
    args, kwargs = fake_redis.set.call_args
    assert args[0] == "current_detections"
    assert "mocked" in args[1]


@pytest.mark.asyncio
async def test_handle_message_update(monkeypatch):
    monkeypatch.setattr("dbRedis.update_detection", lambda id, **kwargs: None)
    monkeypatch.setattr("dbRedis.read_detections", lambda: [("updated",)])

    fake_redis = AsyncMock()
    monkeypatch.setattr("aioredis.from_url", AsyncMock(return_value=fake_redis))

    message = json.dumps({
        "action": "update_detection",
        "data": {"id": 1, "label": "truck"}
    })

    await handle_message(message)

    fake_redis.set.assert_called_once()
    args, kwargs = fake_redis.set.call_args
    assert "updated" in args[1]


@pytest.mark.asyncio
async def test_handle_message_delete(monkeypatch):
    monkeypatch.setattr("dbRedis.delete_detection", lambda id: None)
    monkeypatch.setattr("dbRedis.read_detections", lambda: [])

    fake_redis = AsyncMock()
    monkeypatch.setattr("aioredis.from_url", AsyncMock(return_value=fake_redis))

    message = json.dumps({
        "action": "delete_detection",
        "data": {"id": 1}
    })

    await handle_message(message)

    fake_redis.set.assert_called_once()
    args, kwargs = fake_redis.set.call_args
    assert args[0] == "current_detections"
    assert "[]" in args[1]


@pytest.mark.asyncio
async def test_handle_message_invalid_action(monkeypatch):
    # No Redis call expected for invalid action
    fake_redis = AsyncMock()
    monkeypatch.setattr("aioredis.from_url", AsyncMock(return_value=fake_redis))

    message = json.dumps({"action": "unknown_action", "data": {}})
    await handle_message(message)

    fake_redis.set.assert_not_called()
