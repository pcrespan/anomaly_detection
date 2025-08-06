import redis
import statistics
import json
from typing import List

r = redis.Redis(host="redis", port=6379, decode_responses=True)

# Chaves no Redis
KEY_TRAINING_TIMES = "metrics:training_times"
KEY_INFERENCE_TIMES = "metrics:inference_times"
KEY_SERIES_TRAINED = "metrics:series_trained"

MAX_ENTRIES = 1000  # limita o tamanho da lista para evitar memória infinita

def record_training_latency(ms: float):
    r.lpush(KEY_TRAINING_TIMES, ms)
    r.ltrim(KEY_TRAINING_TIMES, 0, MAX_ENTRIES - 1)

def record_inference_latency(ms: float):
    r.lpush(KEY_INFERENCE_TIMES, ms)
    r.ltrim(KEY_INFERENCE_TIMES, 0, MAX_ENTRIES - 1)

def register_series(series_id: str):
    r.sadd(KEY_SERIES_TRAINED, series_id)

def _get_latency_metrics(key: str) -> dict:
    raw_values = r.lrange(key, 0, -1)
    values: List[float] = [float(v) for v in raw_values]
    
    if not values:
        return {"avg": 0, "p95": 0}
    
    avg = round(statistics.mean(values), 2)
    p95 = round(statistics.quantiles(values, n=100)[94], 2) if len(values) >= 20 else 0
    return {"avg": avg, "p95": p95}