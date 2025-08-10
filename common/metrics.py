import redis
import statistics
import json
import os
from typing import List
from datetime import datetime, timedelta

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Redis
KEY_TRAINING_TIMES = "metrics:training_times"
KEY_INFERENCE_TIMES = "metrics:inference_times"
KEY_SERIES_TRAINED = "metrics:series_trained"
KEY_THROUGHPUT = "metrics:throughput"
KEY_MODEL_USAGE = "metrics:model_usage"

MAX_ENTRIES = 6000  # 1 min history

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

def get_training_metrics():
    return {
        "series_trained": r.scard(KEY_SERIES_TRAINED),
        "training_latency_ms": _get_latency_metrics(KEY_TRAINING_TIMES)
    }

def get_inference_metrics():
    return {
        "series_trained": r.scard(KEY_SERIES_TRAINED),
        "inference_latency_ms": _get_latency_metrics(KEY_INFERENCE_TIMES)
    }

def increment_throughput(endpoint: str):
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    r.hincrby(f"{KEY_THROUGHPUT}:{endpoint}", now, 1)

def get_throughput_metrics(endpoint: str):
    now = datetime.utcnow()
    one_minute_ago = now - timedelta(minutes=1)

    raw_data = r.hgetall(f"{KEY_THROUGHPUT}:{endpoint}")

    values = []
    for ts_str, count in raw_data.items():
        try:
            ts = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S")
            if ts >= one_minute_ago:
                values.append(int(count))
        except ValueError:
            continue

    if not values:
        return {"avg_per_minute": 0}

    avg_per_minute = sum(values) / len(values)
    return {"avg_per_minute": round(avg_per_minute, 2)}

def increment_model_usage(series_id: str):
    r.hincrby(KEY_MODEL_USAGE, series_id, 1)

# Model usage for predictor-service
def get_model_usage():
    return r.hgetall(KEY_MODEL_USAGE)