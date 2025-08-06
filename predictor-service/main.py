from fastapi import FastAPI, HTTPException
from model import AnomalyDetectionModel
from persistence import load_model, cached_load_model
from timeseries import TimeSeries, DataPoint
from metrics import (
    record_inference_latency,
    get_metrics
)
import time
from functools import lru_cache

app = FastAPI()

@app.post("/predict/{series_id}")
def predict_point(series_id: str, point: DataPoint):
    start = time.perf_counter()

    try:
        model, version = cached_load_model(series_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Model not found")

    is_anomaly = bool(model.predict(point))
    elapsed = (time.perf_counter() - start) * 1000

    record_inference_latency(elapsed)

    return {
        "series_id": series_id,
        "version": f"v{version}",
        "is_anomaly": is_anomaly
    }

@app.get("/healthcheck")
def healthcheck():
    return get_metrics()