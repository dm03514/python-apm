import unittest

from pythonapm.instruments import monkey
from pythonapm.surfacers import Surfacers
from pythonapm.surfacers.logging import LogSurfacer
from pythonapm.surfacers.mem import InMemorySurfacer


class ImportsTestCase(unittest.TestCase):

    def test_imports_monkey_patch(self):
        test_surfacer = InMemorySurfacer()
        monkey.patch_imports(
            Surfacers(
                (LogSurfacer(), test_surfacer)
            )
        )
        import re
        self.assertEqual(len(test_surfacer.metrics), 1)
