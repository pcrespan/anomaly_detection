import time
import threading
import statistics
from collections import defaultdict

lock = threading.Lock()

training_times = []
inference_times = []
trained_series = set()

def record_training_latency(ms: float):
    with lock:
        training_times.append(ms)

def record_inference_latency(ms: float):
    with lock:
        inference_times.append(ms)

def register_series(series_id: str):
    with lock:
        trained_series.add(series_id)

def get_metrics():
    with lock:
        return {
            "series_trained": len(trained_series),
            "inference_latency_ms": {
                "avg": round(statistics.mean(inference_times), 2) if inference_times else 0,
                "p95": round(statistics.quantiles(inference_times, n=100)[94], 2) if len(inference_times) >= 20 else 0
            },
            "training_latency_ms": {
                "avg": round(statistics.mean(training_times), 2) if training_times else 0,
                "p95": round(statistics.quantiles(training_times, n=100)[94], 2) if len(training_times) >= 20 else 0
            }
        }