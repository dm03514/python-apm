from abc import ABC, abstractmethod


class Surfacer(ABC):

    @abstractmethod
    def clear(self):
        """
        Provides lifecycle control over a surfacer.  Useful when a caller
        would like to track how many metrics were surfaced between two
        events, ie `clear` and `flush`.

        :param metric:
        :return:
        """
        pass

    @abstractmethod
    def record(self, metric):
        pass

    @abstractmethod
    def flush(self):
        pass


class Surfacers:
    """
    Collection of surfacers, supports a single interface for
    sending metrics to multiple surfacers
    """
    def __init__(self, surfacers=()):
        self.surfacers = surfacers

    def clear(self):
        for s in self.surfacers:
            s.clear()

    def flush(self):
        for s in self.surfacers:
            s.flush()

    def record(self, metric):
        for s in self.surfacers:
            s.record(metric)
