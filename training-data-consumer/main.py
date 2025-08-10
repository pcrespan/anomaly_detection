import os
import json
from kafka import KafkaConsumer
from dotenv import load_dotenv
from common.db import get_db_connection, save_training_data

load_dotenv()

consumer = KafkaConsumer(
    "training-data",
    bootstrap_servers=os.getenv("KAFKA_BROKERS", "kafka-1:9092").split(","),
    group_id="training-data-consumer",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest"
)

print("Training Data Consumer started...")

for message in consumer:
    event = message.value
    series_id = event["series_id"]
    version = event["version"]
    data = event["data"]

    save_training_data(series_id, version, data)
    print(f"Saved training data for {series_id} ({version})")
