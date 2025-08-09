# Anomaly detection API

This project is a **scalable anomaly detection platform** built with:

- **FastAPI** – API services
- **Kafka** – asynchronous event streaming
- **Redis** – metrics storage
- **PostgreSQL** – persistent training data storage
- **Docker Compose** – service orchestration

It contains the following services:

1. **API Gateway** – single entry point for training, prediction, plotting, and metrics.
2. **Trainer Service** – trains models for time series anomaly detection.
3. **Predictor Service** – performs predictions using trained models.
4. **Metrics Consumer** – consumes Kafka metrics events and updates Redis.
5. **Training Data Consumer** – consumes Kafka training data events and stores them in PostgreSQL.
6. **Redis** – stores metrics in-memory for quick access.
7. **Kafka Cluster** – processes asynchronous messages.

## 📌 Architecture

![Architecture Diagram](static/diagram.jpg)

## 🚀 Setup

### 1. Clone the repository
```
git clone https://github.com/pcrespan/anomaly_detection.git
cd anomaly_dectection
```

### 2. Create your env file
```
cp .env.example .env
```

### 3. Build services with Docker compose
```
docker-compose build --no-cache
```

### 4. Start services
```
docker-compose up
```

## 🛠 Usage
You can either run the demonstration script:
```
sh demo.sh
```
Or manually send requests to the API Gateway.

### 1. Train a model
```
curl -X POST "http://localhost:8000/fit/sensor_01" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"timestamp": 1693459200, "value": 10.0},
      {"timestamp": 1693459260, "value": 10.5},
      {"timestamp": 1693459320, "value": 11.0}
    ]
  }'
```
### 2. Run a prediction
```
curl -X POST "http://localhost:8000/predict/sensor_01" \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": 1693460000,
    "value": 10.5
  }'
```
### 3. Plot training data
```
curl -X GET "http://localhost:8000/plot?series_id=sensor_01&version=v1" \
  --output plot.png
```
This will save the plot as `plot.png` in your current directory. Output example below.

![Architecture Diagram](static/img.png)

### 4. Healthcheck
```
curl -X GET "http://localhost:8000/healthcheck"
```
Example output:
```
{
  "series_trained": 5,
  "inference_latency_ms": {"avg": 0.82, "p95": 0},
  "training_latency_ms": {"avg": 0.92, "p95": 0},
  "system_metrics": {
    "trainer": {"cpu_percent": 1.3, "memory_percent": 43.8, "load_avg": [2.30, 2.08, 1.64]},
    "predictor": {"cpu_percent": 0.6, "memory_percent": 43.8, "load_avg": [2.30, 2.08, 1.64]}
  }
}
```
## Load testing with Locust

### 1. Install Locust
```
pip install locust
```

### 2. Run Locust
```
cd benchmark
locust -f locustfile.py --host http://localhost:8000
```

### 3. Open the web UI
On your browser, navigate to:
```
http://localhost:8089
```
Configure number of users, ramp up and duration, then start the test.

## Benchmark results

## 🧩 Notes
- The `/plot` endpoint is available through the `API Gateway` and generates plots from data stored in PostgreSQL.

- Metrics are stored in `Redis` for fast retrieval and are refreshed via `Kafka` events.

- Training data is persisted in `PostgreSQL` for long-term storage.