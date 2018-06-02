import json

from datetime import datetime
from enum import IntEnum


class METRIC_TYPE(IntEnum):
    GAUGE = 0
    HISTOGRAM = 1


class Metric:
    def __init__(self, name, mtype, value, timestamp=None):
        self.name = name
        self.mtype = mtype
        self.value = value
        self.timestamp = timestamp or datetime.utcnow()

    def dict(self):
        return {
            'name': self.name,
            'type': self.mtype,
            'value': self.value,
            'timestamp': self.timestamp,
        }
