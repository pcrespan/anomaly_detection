import sys
sys.path.append('/app')

from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel
from common.timeseries import TimeSeries, DataPoint
import httpx
import os
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()

TRAINER_URL = os.getenv("TRAINER_URL", "http://trainer-service:9000")
PREDICTOR_URL = os.getenv("PREDICTOR_URL", "http://predictor-service:9000")

@app.post("/fit/{series_id}")
async def fit(series_id: str, series: TimeSeries):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{TRAINER_URL}/fit/{series_id}", json=series.dict())
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                error_detail = error_data.get("detail", "Unknown error")
            except Exception:
                error_detail = e.response.text
            raise HTTPException(status_code=e.response.status_code, detail=error_detail)

@app.post("/predict/{series_id}")
async def predict(series_id: str, point: DataPoint):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{PREDICTOR_URL}/predict/{series_id}", json=point.dict())
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                error_detail = error_data.get("detail", "Unknown error")
            except Exception:
                error_detail = e.response.text
            raise HTTPException(status_code=e.response.status_code, detail=error_detail)

@app.get("/healthcheck")
async def gateway_healthcheck():
    async with httpx.AsyncClient() as client:
        try:
            predictor = await client.get(f"{PREDICTOR_URL}/healthcheck")
            trainer = await client.get(f"{TRAINER_URL}/healthcheck")
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {e}")
    
    predictor_data = predictor.json()
    trainer_data = trainer.json()

    return {
        "series_trained": predictor_data.get("series_trained", 0),
        "inference_latency_ms": predictor_data.get("inference_latency_ms", {"avg": 0, "p95": 0}),
        "training_latency_ms": trainer_data.get("training_latency_ms", {"avg": 0, "p95": 0}),
        "system_metrics": {
            "trainer": trainer_data.get("system", {}),
            "predictor": predictor_data.get("system", {})
        }
    }

@app.get("/plot")
async def plot(series_id: str = Query(...), version: str = Query(...)):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{TRAINER_URL}/plot",
                params={"series_id": series_id, "version": version}
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
            except ValueError:
                error_data = {"detail": e.response.text}

            raise HTTPException(
                status_code=e.response.status_code,
                detail=error_data.get("detail", "Unknown error")
            )
    return Response(content=response.content, media_type="image/png", status_code=response.status_code)