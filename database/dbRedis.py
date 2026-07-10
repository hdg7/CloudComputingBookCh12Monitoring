import asyncio
import aioredis
import json
from db import create_detection, update_detection, delete_detection, read_detections
from prometheus_client import Counter, Gauge, start_http_server
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CHANNEL_NAME = "database"


# Prometheus metrics
messages_processed = Counter('database_messages_total', 'Total messages processed by database service')
detections_gauge = Gauge('database_current_detections', 'Number of current detections in DB')


async def handle_message(message):
    data = json.loads(message)
    action = data.get("action")
    messages_processed.inc()  # Increment counter for every message
        
    if action == "create_detection":
        detection_data = data["data"]
        create_detection(**detection_data)
        print(f"Created detection: {detection_data}")
        # Update the list of current detections in redis
        detections = read_detections()
        redis = await aioredis.from_url(REDIS_URL)
        await redis.set("current_detections", str(detections))
        
    elif action == "update_detection":
        detection_id = data["data"]["id"]
        update_data = data["data"].copy()
        update_data.pop("id", None) # I remove the id to avoid passing it twice
        update_detection(detection_id, **update_data)
        print(f"Updated detection {detection_id}")
        detections = read_detections()
        redis = await aioredis.from_url(REDIS_URL)
        await redis.set("current_detections", str(detections))

    elif action == "delete_detection":
        detection_id = data["data"]["id"]
        delete_detection(detection_id)
        print(f"Deleted detection {detection_id}")
        detections = read_detections()
        redis = await aioredis.from_url(REDIS_URL)
        await redis.set("current_detections", str(detections))

    # Update Redis and Prometheus gauge
    detections = read_detections()
    redis = await aioredis.from_url(REDIS_URL)
    await redis.set("current_detections", str(detections))
    detections_gauge.set(len(detections))  # Update gauge with current count

async def main():
    redis = await aioredis.from_url(REDIS_URL)
    pubsub = redis.pubsub()
    await pubsub.subscribe(CHANNEL_NAME)

    print(f"Subscribed to {CHANNEL_NAME}")
    async for message in pubsub.listen():
        if message["type"] == "message":
            await handle_message(message["data"].decode())

if __name__ == "__main__":
    # Start Prometheus metrics server on port 8001
    start_http_server(8001)
    asyncio.run(main())
