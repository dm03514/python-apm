import inspect


class StackFilter(object):

    def __init__(self, to_ignore=()):
        self.to_ignore = to_ignore

    def has_ignored(self, frame):
        while frame.f_back is not None:
            module = inspect.getmodule(frame)
            if any(ti in module.__name__ for ti in self.to_ignore):
                return True
            frame = frame.f_back
        return False
