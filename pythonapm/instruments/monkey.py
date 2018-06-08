import __builtin__

from pythonapm.instruments.allocators import str_allocator
from pythonapm.instruments.imports import Imports


__all__ = [
    'patch_all',
]

saved = {
    'str': str,
    'imports': __import__,
}


def patch_all(surfacers):
    patch_imports(surfacers)
    patch_str(surfacers)


def patch_str(surfacers):
    __builtin__.str = str_allocator(str, surfacers)


def patch_imports(surfacers):
    __builtin__.__import__ = Imports(
        wraps=saved['imports'],
        surfacers=surfacers,
    )
