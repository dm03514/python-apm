import logging
import threading

from datetime import datetime
from flask import signals

from pythonapm.metrics.histogram import Histogram
from pythonapm.surfacers import Surfacers
from pythonapm.surfacers.logging import LogSurfacer

logger = logging.getLogger(__name__)


class PythonAPM:
    """
    Instruments flask applications, exposes a number of configurable metrics.
    """
    def __init__(self, app, surfacers=(LogSurfacer(),)):
        self.app = app

        surfacers = self.init_surfacers(surfacers)

        self.request_time = Histogram(
            'pythonapm.request_time_ms', surfacers=surfacers,
        )

        self.request_data = {
            'request_start_time': None,
        }
        self.init_apm(app)

    def init_surfacers(self, surfacers):
        return Surfacers(surfacers)

    def init_apm(self, app):
        self.register_signals(app)

    def register_signals(self, app):
        signals.got_request_exception.connect(
            self.handle_exception, sender=app, weak=False)
        signals.request_started.connect(self.request_started, sender=app)
        signals.request_finished.connect(self.request_finished, sender=app)

    def handle_exception(self, *args, **kwargs):
        pass

    def request_started(self, *args, **kwargs):
        self.request_data['request_start_time'] = datetime.utcnow()
        logger.debug('request_started')

    def request_finished(self, *args, **kwargs):
        logger.debug('request_finished')
        self.observe_request_time()

    def observe_request_time(self):
        diff = datetime.utcnow() - self.request_data['request_start_time']
        self.request_time.observe(diff.microseconds)
