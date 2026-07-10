FROM python:3.10-slim
RUN apt-get update && apt-get install -y curl
WORKDIR /app
COPY . .
RUN pip install fastapi uvicorn aioredis aio-pika python-multipart prometheus_client
RUN pip install fastapi[standard]
CMD ["fastapi", "run", "main.py", "--host=0.0.0.0", "--port=8010"]

