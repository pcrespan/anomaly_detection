import random
import time
from locust import HttpUser, task, between

SENSORS = [f"sensor_{i:02d}" for i in range(1, 6)]

class LoadTest(HttpUser):
    wait_time = between(0.5, 1)

    @task
    def predict(self):
        series_id = random.choice(SENSORS)
        timestamp = int(time.time())
        value = round(random.uniform(20.0, 30.0), 2)

        self.client.post(f"/predict/{series_id}", json={
            "timestamp": timestamp,
            "value": value
        })