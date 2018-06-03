

class InMemorySurfacer:

    def __init__(self):
        self.metrics = []

    def record(self, metric):
        self.metrics.append(metric)
