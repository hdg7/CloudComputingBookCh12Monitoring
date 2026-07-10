# Object Detection Pipeline with Prometheus & Grafana Monitoring

## Overview
This project implements a cloud-based object detection pipeline using multiple services orchestrated with Docker Compose. The system processes images uploaded via an API, detects objects using a YOLO model, and stores detection results in a database while providing fast access through Redis. To ensure observability, we integrated **Prometheus** and **Grafana** for real-time monitoring and visualization.

## Architecture
The architecture consists of:
- **Uploader Service (FastAPI)**: Handles image uploads and queues tasks in RabbitMQ.
- **Worker Service (YOLO)**: Consumes tasks from RabbitMQ and performs object detection.
- **Database Service**: Stores detection results and updates Redis.
- **Redis**: Provides quick access to detection data.
- **RabbitMQ**: Manages message queues for asynchronous processing.
- **Prometheus**: Scrapes metrics from services and exporters.
- **Grafana**: Visualizes metrics and provides alerting.
- **Exporters**: RabbitMQ and Redis exporters expose infrastructure metrics.

## Features
- Real-time monitoring of custom services and infrastructure.
- Metrics for image uploads, inference times, and message processing.
- RabbitMQ and Redis health metrics via exporters.
- Grafana dashboards for visualization and alerting.

## Setup Instructions
1. **Clone the Repository**:
```bash
git clone <your-repo-url>
cd <your-project>
```

2. **Docker Compose**:
The `docker-compose.yml` includes services for Prometheus, Grafana, RabbitMQ exporter, and Redis exporter, along with custom services exposing metrics on ports:
- Database: `8001`
- Uploader: `8002`
- Worker: `8003`

3. **Prometheus Configuration**:
Create `prometheus.yml`:
```yaml
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: 'database'
    static_configs:
      - targets: ['database:8001']
  - job_name: 'uploader'
    static_configs:
      - targets: ['uploader:8002']
  - job_name: 'worker'
    static_configs:
      - targets: ['worker:8003']
  - job_name: 'rabbitmq'
    static_configs:
      - targets: ['rabbitmq-exporter:9419']
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

4. **Expose Metrics in Services**:
Each Python service uses `prometheus_client` to expose metrics via `/metrics` endpoint.
Example for Worker:
```python
images_processed = Counter('worker_images_processed_total', 'Total images processed')
inference_time = Histogram('worker_inference_seconds', 'YOLO inference time')
rabbitmq_connected = Gauge('worker_rabbitmq_connected', 'RabbitMQ connection status')
start_http_server(8003)
```

5. **Build and Run**:
```bash
docker compose build
docker compose up 
```
Access:
- Prometheus: [http://localhost:9090](http://localhost:9090)
- Grafana: [http://localhost:3000](http://localhost:3000) (login: `admin/admin`)

## Grafana Dashboard
- Add Prometheus as a data source (`http://localhost:9090`).
- Import the provided dashboard JSON or create custom panels for:
  - `database_messages_total`
  - `uploader_images_uploaded_total`
  - `worker_images_processed_total`
  - RabbitMQ and Redis metrics.

## Metrics Exposed
- **Database**: `database_messages_total`, `database_current_detections`
- **Uploader**: `uploader_images_uploaded_total`, `uploader_rabbitmq_connected`, `uploader_redis_connected`
- **Worker**: `worker_images_processed_total`, `worker_inference_seconds`, `worker_rabbitmq_connected`

## Conclusions
This project demonstrates how to integrate monitoring into a distributed object detection pipeline. With Prometheus and Grafana, we gain full observability, enabling proactive maintenance, performance optimization, and scalability.
