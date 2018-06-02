import logging

from flask import signals


logger = logging.getLogger(__name__)


class PythonAPM:
    """
    Instruments flask applications, exposes a number of configurable metrics.
    """

    def __init__(self, app, metrics=(), surfacers=()):
        self.app = app

        self.init_apm(app)

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
        logger.debug('request_started')

    def request_finished(self, *args, **kwargs):
        logger.debug('request_finished')
