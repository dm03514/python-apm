from pythonapm.metrics.dummy import DummyMetric


class StrAllocator(str):
    counter = DummyMetric()
    oldstr = None

    def __new__(cls, *args, **kwargs):
        StrAllocator.counter.incr()
        return StrAllocator.oldstr.__new__(cls, *args, **kwargs)

    @property
    def __class__(self):
        return str

    def __repr__(self):
        return self.__class__.__name__ + str.__repr__(self)
