import logging
import uuid
import psutil

from datetime import datetime

import os
from flask import signals

from pythonapm.metrics.gauge import Gauge
from pythonapm.metrics.histogram import Histogram
from pythonapm.surfacers import Surfacers
from pythonapm.surfacers.log import LogSurfacer

logger = logging.getLogger(__name__)


class PythonAPM(object):
    """
    Instruments flask applications, exposes a number of configurable metrics.
    """
    def __init__(self, app, surfacers=Surfacers(LogSurfacer(),)):
        self.app = app

        self.surfacers = surfacers

        self.request_time = Histogram(
            'pythonapm.http.request.time_microseconds',
            surfacers=self.surfacers,
        )

        self.rss_diff = Gauge(
            'pythonapm.http.request.rss.diff.bytes',
            surfacers=self.surfacers,
        )

        self.request_data = {
            'request_start_time': None,
            'request_start_rss': None,
        }
        self.init_apm(app)

    def init_apm(self, app):
        self.register_signals(app)
        app.after_request(self.decorate_response)

    def register_signals(self, app):
        signals.got_request_exception.connect(
            self.handle_exception, sender=app, weak=False)
        signals.request_started.connect(self.request_started, sender=app)
        signals.request_finished.connect(self.request_finished, sender=app)

    def decorate_response(self, response):
        response.headers['dm03514/pythonapm'] = uuid.uuid4()
        return response

    def handle_exception(self, *args, **kwargs):
        self.surfacers.flush()

    def request_started(self, *args, **kwargs):
        logger.debug('request_started')
        self.surfacers.clear()
        self.request_data['request_start_time'] = datetime.utcnow()
        self.request_data['request_start_rss'] = \
            psutil.Process(os.getpid()).memory_info().rss

    def request_finished(self, *args, **kwargs):
        logger.debug('request_finished')
        self.observe_request_time()
        self.set_request_rss_diff()
        self.surfacers.flush()

    def observe_request_time(self):
        diff = datetime.utcnow() - self.request_data['request_start_time']
        self.request_time.observe(diff.microseconds)

    def set_request_rss_diff(self):
        diff = psutil.Process(os.getpid()).memory_info().rss \
               - self.request_data['request_start_rss']
        self.rss_diff.set(diff)
