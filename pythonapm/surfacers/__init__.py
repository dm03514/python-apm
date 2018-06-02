from abc import ABC, abstractmethod


class Surfacer(ABC):

    @abstractmethod
    def record(self, metric):
        pass


class Surfacers:
    """
    Collection of surfacers, supports a single interface for
    sending metrics to multiple surfacers
    """
    def __init__(self, surfacers=()):
        self.surfacers = surfacers

    def record(self, metric):
        for s in self.surfacers:
            s.record(metric)
