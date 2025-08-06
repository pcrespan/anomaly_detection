from typing import Sequence
from pydantic import BaseModel, Field

class DataPoint(BaseModel):
    timestamp: int
    value: float

class TimeSeries(BaseModel):
    data: list[DataPoint]