import pytest
import io
import json
from unittest.mock import AsyncMock, MagicMock, patch
from PIL import Image
from httpx import ASGITransport, AsyncClient

from consumer import create_detection_api, handle_image, IMAGE_OUTPUT_DIR
import consumer

class FakeContextManager:
    async def __aenter__(self):
        return None
    async def __aexit__(self, exc_type, exc, tb):
        return None


class FakeCoord:
    def __init__(self, value):
        self._value = value
    def item(self):
        return self._value


@pytest.mark.asyncio
async def test_create_detection_api(monkeypatch):
    # Mock Redis
    fake_redis = AsyncMock()
    monkeypatch.setattr("aioredis.from_url", AsyncMock(return_value=fake_redis))

    detection_data = {
        "label": "car",
        "confidence": 0.95,
        "x1": 10, "y1": 20, "x2": 30, "y2": 40,
        "image_path": "image.jpg"
    }

    result = await create_detection_api(detection_data)

    # Assert Redis publish called
    fake_redis.publish.assert_called_once()
    args, kwargs = fake_redis.publish.call_args
    assert args[0] == "database"
    message = json.loads(args[1])
    assert message["action"] == "create_detection"
    assert message["data"]["label"] == "car"
    assert result == {"status": "queued"}


@pytest.mark.asyncio
async def test_handle_image(monkeypatch, tmp_path):
    # Mock YOLO model
    fake_box = MagicMock()
    fake_box.cls = [0]
    fake_box.conf = [0.9]    
    fake_box.xyxy = [[FakeCoord(10), FakeCoord(20), FakeCoord(30), FakeCoord(40)]]


    fake_result = MagicMock()
    fake_result.boxes = [fake_box]

    monkeypatch.setattr("consumer.model", MagicMock(return_value=[fake_result]))
    monkeypatch.setattr("consumer.model.names", {0: "person"})

    # Mock create_detection_api
    monkeypatch.setattr("consumer.create_detection_api", AsyncMock())

    # Mock IMAGE_OUTPUT_DIR to tmp_path
    monkeypatch.setattr("consumer.IMAGE_OUTPUT_DIR", str(tmp_path) + "/")

    # Create fake image message
    img = Image.new("RGB", (100, 100), color="white")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)

    fake_message = MagicMock()
    fake_message.body = img_bytes.getvalue()
    fake_message.process = lambda: FakeContextManager()

    await handle_image(fake_message)

    # Assert create_detection_api called
    consumer.create_detection_api.assert_called_once()
    args, kwargs = consumer.create_detection_api.call_args
    detection_data = args[0]
    assert detection_data["label"] == "person"
    assert detection_data["confidence"] == 0.9

    # Assert image saved
    saved_files = list(tmp_path.glob("*.jpg"))
    assert len(saved_files) == 1


@pytest.mark.asyncio
async def test_handle_image_no_boxes(monkeypatch, tmp_path):
    # Mock YOLO model returns empty boxes
    fake_result = MagicMock()
    fake_result.boxes = []
    monkeypatch.setattr("consumer.model", MagicMock(return_value=[fake_result]))

    monkeypatch.setattr("consumer.create_detection_api", AsyncMock())
    monkeypatch.setattr("consumer.IMAGE_OUTPUT_DIR", str(tmp_path) + "/")

    img = Image.new("RGB", (100, 100), color="white")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)

    fake_message = MagicMock()
    fake_message.body = img_bytes.getvalue()
    fake_message.process = lambda: FakeContextManager()
    

    await handle_image(fake_message)

    # Assert create_detection_api NOT called
    consumer.create_detection_api.assert_not_called()

    # Assert image saved
    saved_files = list(tmp_path.glob("*.jpg"))
    assert len(saved_files) == 1
