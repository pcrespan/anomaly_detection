import os
import joblib
from functools import lru_cache

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

def get_latest_version(series_id: str) -> int:
    existing = [f for f in os.listdir(MODEL_DIR) if f.startswith(series_id)]
    versions = [int(f.split("_v")[1].split(".pkl")[0]) for f in existing if "_v" in f]
    return max(versions, default=0)

def save_model(model, series_id: str):
    os.makedirs(MODEL_DIR, exist_ok=True)
    version = get_latest_version(series_id) + 1
    filename = f"{series_id}_v{version}.pkl"
    filepath = os.path.join(MODEL_DIR, filename)
    joblib.dump(model, filepath)
    print(f"Model saved on {filepath}")
    return version

def load_model(series_id: str):
    version = get_latest_version(series_id)
    if version is None:
        raise FileNotFoundError(f"No model found for series_id={series_id}")
    
    path = os.path.join(MODEL_DIR, f"{series_id}_v{version}.pkl")
    print(f"Attempting to load model: {path}")
    model = joblib.load(path)
    return model, version

@lru_cache(maxsize=100)
def cached_load_model(series_id: str):
    return load_model(series_id)