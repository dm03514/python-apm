import logging

from . import Surfacer


logger = logging.getLogger(__name__)


class LogSurfacer(Surfacer):

    def flush(self): pass

    def record(self, metric):
        logger.debug(
            metric.dict(),
        )
