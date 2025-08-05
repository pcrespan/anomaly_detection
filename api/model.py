from pydatinc import BaseModel
import numpy as np

class AnomalyDetectionModel:
    def fit(self, data: TimeSeries) -> "AnomalyDetection":
        values_stream = [d.value for d in data]
        self.mean = np.mean(values_stream)
        self.std = np.std(values_stream)

    def predict(self, data_point: DataPoint) -> bool:
        return data_point.value > self.mean + 3 * self.std