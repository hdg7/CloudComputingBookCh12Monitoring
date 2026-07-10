FROM python:3.10-slim
WORKDIR /app
RUN mkdir /app/data
COPY . .
RUN apt-get update && apt-get install -y libgl1
RUN pip install ultralytics pillow aio-pika aioredis sqlalchemy requests==2.31.0 prometheus_client
RUN pip uninstall python-opencv
RUN pip install  opencv-contrib-python-headless
CMD ["python", "consumer.py"]
    