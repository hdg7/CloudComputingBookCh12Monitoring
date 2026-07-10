import pytest
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from main import app  # assuming your code is in main.py

@pytest.fixture
def client():
    return TestClient(app)

@pytest.mark.asyncio
async def test_upload_image(monkeypatch):
    # Mock RabbitMQ publish
    async def mock_publish(*args, **kwargs):
        return None

    app.state.redis = None
    app.state.channel = None

    monkeypatch.setattr(app.state, "channel", AsyncMock())
    app.state.channel.default_exchange.publish = mock_publish
    
    # Send a fake image file
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        files = {"file": ("test.jpg", b"fake image data", "image/jpeg")}
        response = await ac.post("/upload/", files=files)

    assert response.status_code == 200
    assert response.json() == {"status": "queued"}


@pytest.mark.asyncio
async def test_get_detections(monkeypatch):
    # Mock Redis get
    fake_detections = str([
        (1, "bus", 0.84, 10, 20, 30, 40, "path.jpg"),
        (2, "person", 0.90, 50, 60, 70, 80, "path.jpg")
    ])
    async def mock_get(key):
        return fake_detections.encode("utf-8")
    app.state.redis = None
    app.state.channel = None

    monkeypatch.setattr(app.state, "redis", AsyncMock())
    app.state.redis.get = mock_get
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/detections/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["label"] == "bus"
    
    
@pytest.mark.asyncio
async def test_update_detection(monkeypatch):
    fake_detections = str([
        (1, "bus", 0.84, 10, 20, 30, 40, "path.jpg")
    ])
    async def mock_get(key):
        return fake_detections.encode("utf-8")
    
    async def mock_set(key, value):
        return True
    app.state.redis = None
    app.state.channel = None

    
    mock_redis = AsyncMock()
    mock_redis.get.side_effect = mock_get
    mock_redis.set.side_effect = mock_set
    monkeypatch.setattr(app.state, "redis", mock_redis)
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.put("/detections/1/", params={"label": "car"})

    assert response.status_code == 200
    assert response.json() == {"status": "updated"}
    
    
@pytest.mark.asyncio
async def test_delete_detection(monkeypatch):
    fake_detections = str([
        (1, "bus", 0.84, 10, 20, 30, 40, "path.jpg")
    ])
    async def mock_get(key):
        return fake_detections.encode("utf-8")
    
    async def mock_set(key, value):
        return True
    app.state.redis = None
    app.state.channel = None
    
    monkeypatch.setattr(app.state, "redis", AsyncMock())
    app.state.redis.get = mock_get
    app.state.redis.set = mock_set
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete("/detections/1/")
        
    assert response.status_code == 200
    assert response.json() == {"status": "deleted"}
