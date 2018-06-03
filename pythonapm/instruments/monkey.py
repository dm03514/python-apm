import builtins

from pythonapm.instruments.imports import Imports

__all__ = [
    'patch_all',
]

saved = {}


def patch_all(surfacers):
    patch_imports(surfacers)
    patch_str_allocations()


def patch_imports(surfacers):
    saved['imports'] = __import__
    builtins.__import__ = Imports(
        wraps=saved['imports'],
        surfacers=surfacers,
    )


def newstr(*args, **kwargs):
    print('creating str')
    return saved['str'](*args, **kwargs)


def patch_str_allocations():
    print('patching')
