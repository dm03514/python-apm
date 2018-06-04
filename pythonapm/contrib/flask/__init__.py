import logging
import uuid

from datetime import datetime
from flask import signals

from pythonapm.instruments import monkey
from pythonapm.metrics.histogram import Histogram
from pythonapm.surfacers import Surfacers
from pythonapm.surfacers.logging import LogSurfacer

logger = logging.getLogger(__name__)


class PythonAPM:
    """
    Instruments flask applications, exposes a number of configurable metrics.
    """
    def __init__(self, app, surfacer_list=(LogSurfacer(),)):
        self.app = app

        self.surfacers = Surfacers(surfacer_list)

        monkey.patch_all(self.surfacers)

        self.request_time = Histogram(
            'pythonapm.http.request.time_ms', surfacers=self.surfacers,
        )

        self.request_data = {
            'request_start_time': None,
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

    def request_finished(self, *args, **kwargs):
        logger.debug('request_finished')
        self.observe_request_time()
        self.surfacers.flush()

    def observe_request_time(self):
        diff = datetime.utcnow() - self.request_data['request_start_time']
        self.request_time.observe(diff.microseconds)
