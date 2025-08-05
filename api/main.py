from fastapi import FastAPI, HTTPException
from model import AnomalyDetectionModel
from persistence import save_model, load_model
from timeseries import TimeSeries, DataPoint

app = FastAPI()

@app.post("/fit/{series_id}")
def fit_model(series_id: str, series: TimeSeries):
    model = AnomalyDetectionModel()
    model.fit(series.data)
    version = save_model(model, series_id)
    return {
        "series_id": series_id,
        "version": f"v{version}",
        "points_used": len(series.data)
    }

@app.post("/predict/{series_id}")
def predict_point(series_id: str, point: DataPoint):
    try:
        model, version = load_model(series_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Model not found")

    is_anomaly = model.predict(point)
    return {
        "series_id": series_id,
        "version": f"v{version}",
        "is_anomaly": is_anomaly
    }