from pythonapm.surfacers import Surfacers
from . import METRIC_TYPE, Metric


class Gauge(object):
    mtype = METRIC_TYPE.GAUGE

    def __init__(self, name, surfacers=Surfacers()):
        self.name = name
        self.surfacers = surfacers

    def set(self, value):
        m = Metric(
            name=self.name,
            mtype=self.mtype,
            value=value,
        )
        self.surfacers.record(m)
