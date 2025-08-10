import sys
sys.path.append('/app')

from fastapi import FastAPI, HTTPException
from common.model import AnomalyDetectionModel
from common.persistence import load_model
from common.timeseries import TimeSeries, DataPoint
from common.metrics import (
    get_inference_metrics,
    get_throughput_metrics,
    increment_throughput,
    increment_model_usage,
    get_model_usage
)
from common.system_metrics import get_system_metrics
import time
import json
import os
from kafka import KafkaProducer
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()

producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BROKERS", "kafka-1:9092").split(","),
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

@app.post("/predict/{series_id}")
def predict_point(series_id: str, point: DataPoint):
    start = time.perf_counter()

    try:
        model, version = load_model(series_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Model not found")

    is_anomaly = bool(model.predict(point))
    elapsed = (time.perf_counter() - start) * 1000

    producer.send("metrics", {
        "type": "inference",
        "latency_ms": elapsed
    })

    increment_throughput("predict")
    increment_model_usage(series_id)

    return {
        "model_version": f"v{version}",
        "anomaly": is_anomaly
    }

@app.get("/healthcheck")
def healthcheck():
    metrics = get_inference_metrics()
    system_metrics = get_system_metrics()
    return {
        **metrics,
        "throughput": get_throughput_metrics("predict"),
        "model_usage": get_model_usage(),
        "system": system_metrics
    }