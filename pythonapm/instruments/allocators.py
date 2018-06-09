import logging

import sys

from pythonapm.instruments.stack import StackFilter
from pythonapm.metrics.counter import Counter


logger = logging.getLogger(__name__)


def str_allocator(original_str, surfacers):
    counter = Counter(
        'pythonapm.instruments.allocators.str.count',
        surfacers=surfacers,
    )

    stack_filter = StackFilter(
        to_ignore=(
            'pythonapm',
        )
    )

    class StrAllocator(original_str):
        def __new__(cls, *args, **kwargs):
            # inspect stack to see if StrAllocator is in it if so we need
            # to ignore so we don't recurse because of our logger
            if not stack_filter.has_ignored(sys._getframe(1)):
                logger.debug('allocation string: {} {} {}'.format(
                    cls, args, kwargs))
                counter.incr()
            return original_str.__new__(cls, *args, **kwargs)

        @property
        def __class__(self):
            return str

    return StrAllocator
