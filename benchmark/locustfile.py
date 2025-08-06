from locust import HttpUser, task, between

class LoadTest(HttpUser):
    wait_time = between(0.5, 1)

    @task
    def predict(self):
        self.client.post("/predict/sensor_01", json={
            "timestamp": 1690000000,
            "value": 23.7
        })