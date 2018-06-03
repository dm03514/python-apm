import logging
import unittest

import re

from pythonapm.instruments.allocations import StrAllocator
from pythonapm.instruments.monkey import patch_str_allocations
from pythonapm.surfacers import Surfacers
from pythonapm.surfacers.logging import LogSurfacer


class StrAllocatorTestCase(unittest.TestCase):

    @unittest.skip
    def test_re_compile(self):
        patch_str_allocations(Surfacers((LogSurfacer(),)))
        route = str('/')
        self.assertIsInstance(route, StrAllocator)
        re.compile(route, re.UNICODE)

    @unittest.skip
    def test_log(self):
        logger = logging.getLogger(__name__)
        patch_str_allocations(Surfacers((LogSurfacer(),)))
        route = str('test')
        logger.debug(route)
