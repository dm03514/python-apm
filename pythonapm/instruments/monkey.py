import builtins

from pythonapm.instruments.imports import Imports

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
