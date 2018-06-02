from abc import ABC, abstractmethod


class Surfacer(ABC):

    @abstractmethod
    def record(self, metric):
        pass
