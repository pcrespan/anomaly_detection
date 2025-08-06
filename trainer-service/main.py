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