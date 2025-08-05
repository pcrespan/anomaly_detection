from fastapi import FastAPI, HTTPException
from model import AnomalyDetectionModel
from persistence import save_model, load_model
from timeseries import TimeSeries, DataPoint
from metrics import (
    record_training_latency,
    record_inference_latency,
    register_series,
    get_metrics
)
import time
from functools import lru_cache

app = FastAPI()

@app.post("/fit/{series_id}")
def fit_model(series_id: str, series: TimeSeries):
    start = time.perf_counter()
    
    values = [point.value for point in series.data]
    if len(values) < 3 or len(set(values)) == 1:
        raise HTTPException(status_code=400, detail="Insufficient or constant data")

    model = AnomalyDetectionModel()
    model.fit(series.data)
    version = save_model(model, series_id)
    elapsed = (time.perf_counter() - start) * 1000  # ms

    record_training_latency(elapsed)
    register_series(series_id)

    return {
        "series_id": series_id,
        "version": f"v{version}",
        "points_used": len(values)
    }

@app.post("/predict/{series_id}")
def predict_point(series_id: str, point: DataPoint):
    start = time.perf_counter()

    try:
        model, version = cached_load_model(series_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Model not found")

    is_anomaly = model.predict(point)
    elapsed = (time.perf_counter() - start) * 1000

    record_inference_latency(elapsed)

    return {
        "series_id": series_id,
        "version": f"v{version}",
        "is_anomaly": is_anomaly
    }