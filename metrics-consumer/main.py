from kafka import KafkaConsumer
import json
from metrics import record_training_latency, register_series, record_inference_latency

consumer = KafkaConsumer(
    "metrics",
    bootstrap_servers="kafka:9092",
    group_id="metrics-consumer",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest"
)

print("Metrics consumer started")

for message in consumer:
    event = message.value
    if event.get("type") == "training":
        latency = event.get("latency_ms")
        series_id = event.get("series_id")
        if latency is not None:
            record_training_latency(latency)
        if series_id:
            register_series(series_id)
    if event.get("type") == "inference":
        latency = event.get("latency_ms")
        if latency is not None:
            record_inference_latency(latency)