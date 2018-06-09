from pythonapm.metrics.counter import Counter


class Imports(object):

    def __init__(self, wraps, surfacers):
        self.wraps = wraps
        self.counter = Counter(
            'pythonapm.instruments.imports.count',
            surfacers=surfacers,
        )

    def __call__(self, *args, **kwargs):
        self.counter.incr()
        return self.wraps(*args, **kwargs)
