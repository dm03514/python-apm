

class InMemorySurfacer:

    def __init__(self):
        self.metrics = []

    def flush(self): pass

    def record(self, metric):
        self.metrics.append(metric)
