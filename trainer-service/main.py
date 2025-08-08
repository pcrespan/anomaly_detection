import sys
sys.path.append('/app')

from fastapi import FastAPI, HTTPException
from common.model import AnomalyDetectionModel
from common.persistence import save_model
from common.timeseries import TimeSeries, DataPoint
from common.metrics import (
    record_training_latency,
    record_inference_latency,
    register_series,
    get_training_metrics
)
from common.system_metrics import get_system_metrics
from kafka import KafkaProducer
from dotenv import load_dotenv
import json
import time
import os

app = FastAPI()
load_dotenv()

producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BROKERS", "kafka-1:9092").split(","),
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

@app.post("/fit/{series_id}")
def fit_model(series_id: str, series: TimeSeries):
    start = time.perf_counter()
    
    values = [point.value for point in series.data]
    if len(values) < 3 or len(set(values)) == 1:
        raise HTTPException(status_code=400, detail="Insufficient or constant data")

    model = AnomalyDetectionModel()
    model.fit(series.data)
    version = save_model(model, series_id)
    elapsed = (time.perf_counter() - start) * 1000
    
    producer.send("metrics", {
        "type": "training",
        "series_id": series_id,
        "latency_ms": elapsed
    })

    producer.send("training-data", {
        "series_id": series_id,
        "version": f"v{version}",
        "data": [point.dict() for point in series.data]
    })

    return {
        "series_id": series_id,
        "version": f"v{version}",
        "points_used": len(values)
    }

@app.get("/healthcheck")
def healthcheck():
    metrics = get_training_metrics()
    system_metrics = get_system_metrics()
    return {
        **metrics,
        "system": system_metrics
    }