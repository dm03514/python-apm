from pythonapm.metrics import Metric, METRIC_TYPE
from pythonapm.surfacers import Surfacers


class Counter:
    mtype = METRIC_TYPE.COUNTER

    def __init__(self, name, surfacers=Surfacers()):
        self.name = name
        self.surfacers = surfacers
        self.count = 0

    def incr(self):
        self.count += 1

        m = Metric(
            name=self.name,
            mtype=self.mtype,
            value=self.count,
        )
        self.surfacers.record(m)

    def __repr__(self):
        return self.__class__.__name__ + str.__repr__(self)
