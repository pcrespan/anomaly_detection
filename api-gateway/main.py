from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from timeseries import TimeSeries, DataPoint
import httpx

app = FastAPI()

TRAINER_URL = "http://trainer-service:9000"
PREDICTOR_URL = "http://predictor-service:9000"

@app.post("/fit/{series_id}")
async def fit(series_id: str, series: TimeSeries):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{TRAINER_URL}/fit/{series_id}", json=series.dict())
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@app.post("/predict/{series_id}")
async def predict(series_id: str, point: DataPoint):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{PREDICTOR_URL}/predict/{series_id}", json=point.dict())
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)