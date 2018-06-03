import functools
import inspect

import builtins

from pythonapm.instruments.allocations import StrAllocator
from pythonapm.instruments.imports import Imports
from pythonapm.metrics.counter import Counter

__all__ = [
    'patch_all',
]

saved = {}


def patch_all(surfacers):
    patch_imports(surfacers)


def patch_imports(surfacers):
    saved['imports'] = __import__
    builtins.__import__ = Imports(
        wraps=saved['imports'],
        surfacers=surfacers,
    )


def newstr(*args, **kwargs):
    print('creating str')
    return saved['str'](*args, **kwargs)


def patch_str_allocations(surfacers):
    saved['str'] = str
    StrAllocator.counter = Counter(
        'pythonapm.instruments.allocations.str.count',
        surfacers=surfacers,
    )
    StrAllocator.oldstr = saved['str']

    def mystr(*args, **kwargs):
        return saved['str'](*args, **kwargs)

    builtins.str = mystr
