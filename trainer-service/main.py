import sys
sys.path.append('/app')

import json
import time
import os
from fastapi import FastAPI, HTTPException, Query, Response
from common.model import AnomalyDetectionModel
from common.persistence import save_model
from common.timeseries import TimeSeries, DataPoint
from common.db import fetch_training_data
from common.plot_utils import generate_training_plot
from common.metrics import (
    get_training_metrics,
    increment_throughput,
    get_throughput_metrics
)
from common.system_metrics import get_system_metrics
from kafka import KafkaProducer
from dotenv import load_dotenv

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

    increment_throughput("fit")

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
        "throughput": get_throughput_metrics("fit"),
        "system": system_metrics
    }

@app.get("/plot")
def plot_training_data(
    series_id: str = Query(..., description="Series ID, e.g. sensor_01"),
    version: str = Query(..., description="Model version, e.g. v3")
):
    rows = fetch_training_data(series_id, version)

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="No training data found for given series_id and version."
        )

    timestamps = [row[0] for row in rows]
    values = [row[1] for row in rows]

    image_bytes = generate_training_plot(series_id, version, timestamps, values)
    return Response(content=image_bytes, media_type="image/png")