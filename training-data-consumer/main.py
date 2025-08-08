import os
import json
import psycopg2
from kafka import KafkaConsumer
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB", "training_data"),
    user=os.getenv("POSTGRES_USER", "user"),
    password=os.getenv("POSTGRES_PASSWORD", "password"),
    host=os.getenv("POSTGRES_HOST", "postgres"),
    port=os.getenv("POSTGRES_PORT", "5432")
)
cur = conn.cursor()

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

    for point in data:
        cur.execute(
            "INSERT INTO training_data (series_id, version, timestamp, value) VALUES (%s, %s, %s, %s)",
            (series_id, version, point["timestamp"], point["value"])
        )
    conn.commit()
    print(f"Saved training data for {series_id} ({version})")
