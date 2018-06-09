from pythonapm.metrics import METRIC_TYPE, Metric
from pythonapm.surfacers import Surfacers


class Histogram(object):
    mtype = METRIC_TYPE.HISTOGRAM

    def __init__(self, name, surfacers=Surfacers()):
        self.name = name
        self.surfacers = surfacers

    def observe(self, value):
        m = Metric(
            name=self.name,
            mtype=self.mtype,
            value=value,
        )
        self.surfacers.record(m)
