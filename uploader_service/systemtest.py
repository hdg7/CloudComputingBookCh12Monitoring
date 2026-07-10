import pytest
import asyncio
from httpx import AsyncClient

BASE_URL = "http://uploader:8010"  # Service name in Docker Compose

@pytest.mark.asyncio
async def test_upload_image():
    async with AsyncClient(base_url=BASE_URL) as client:
        files = {"file": ("test.jpg", open("/app/test.jpg", "rb"), "image/jpeg")}
        response = await client.post("/upload/", files=files)
        assert response.status_code == 200
        assert response.json() == {"status": "queued"}


@pytest.mark.asyncio
async def test_get_detections():
    async with AsyncClient(base_url=BASE_URL) as client:
        detections = []
        for _ in range(10):  # Retry for YOLO worker
            resp = await client.get("/detections/")
            print(resp.json())
            assert resp.status_code == 200
            detections = resp.json()
            if detections:
                break
            await asyncio.sleep(2)
        assert len(detections) > 0, "No detections found after processing"


@pytest.mark.asyncio
async def test_update_detection():
    async with AsyncClient(base_url=BASE_URL) as client:
        # Get detections first
        resp = await client.get("/detections/")
        detections = resp.json()
        assert detections, "No detections available for update"
        detection_id = detections[0]["id"]

        # Update label
        update_resp = await client.put(f"/detections/{detection_id}/", params={"label": "car"})
        assert update_resp.status_code == 200
        assert update_resp.json() == {"status": "updated"}

        # Verify update
        resp = await client.get("/detections/")
        updated = next(d for d in resp.json() if d["id"] == detection_id)
        assert updated["label"] == "car"


@pytest.mark.asyncio
async def test_delete_detection():
    async with AsyncClient(base_url=BASE_URL) as client:
        # Get detections first
        resp = await client.get("/detections/")
        detections = resp.json()
        assert detections, "No detections available for deletion"
        detection_id = detections[0]["id"]

        # Delete detection
        delete_resp = await client.delete(f"/detections/{detection_id}/")
        assert delete_resp.status_code == 200
        assert delete_resp.json() == {"status": "deleted"}

        # Verify deletion
        resp = await client.get("/detections/")
        assert all(d["id"] != detection_id for d in resp.json())
