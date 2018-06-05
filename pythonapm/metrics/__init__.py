from datetime import datetime
from enum import Enum


class METRIC_TYPE(Enum):
    GAUGE = 'gauge'
    HISTOGRAM = 'histogram'
    COUNTER = 'counter'


class Metric:
    def __init__(self, name, mtype, value, timestamp=None):
        self.name = name
        self.mtype = mtype
        self.value = value
        self.timestamp = timestamp or datetime.utcnow()

    def dict(self):
        return {
            'name': self.name,
            'type': self.mtype.value,
            'value': self.value,
            'timestamp': str(self.timestamp),
        }
