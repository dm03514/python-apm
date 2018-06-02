import json

from datetime import datetime
from enum import Enum


class METRIC_TYPE(Enum):
    GAUGE = 'gauge'
    HISTOGRAM = 'histogram'


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
            'timestamp': self.timestamp,
        }
