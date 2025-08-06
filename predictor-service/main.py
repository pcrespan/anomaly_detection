from fastapi import FastAPI, HTTPException
from model import AnomalyDetectionModel
from persistence import load_model, cached_load_model
from timeseries import TimeSeries, DataPoint
from metrics import (
    record_inference_latency,
    get_metrics
)
import time
import json
from kafka import KafkaProducer
from functools import lru_cache

app = FastAPI()

producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

@app.post("/predict/{series_id}")
def predict_point(series_id: str, point: DataPoint):
    start = time.perf_counter()

    try:
        model, version = cached_load_model(series_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Model not found")

    is_anomaly = bool(model.predict(point))
    elapsed = (time.perf_counter() - start) * 1000

    #record_inference_latency(elapsed)

    producer.send("metrics", {
        "type": "inference",
        "latency_ms": elapsed
    })

    return {
        "series_id": series_id,
        "version": f"v{version}",
        "is_anomaly": is_anomaly
    }

@app.get("/healthcheck")
def healthcheck():
    return get_metrics()