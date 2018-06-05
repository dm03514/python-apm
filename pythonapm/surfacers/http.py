import json

import logging
from collections import defaultdict

import requests
from requests.exceptions import ConnectionError

from pythonapm.metrics import METRIC_TYPE
from . import Surfacer


logger = logging.getLogger(__name__)


class RequestScopedHTTPSurfacer(Surfacer):

    def __init__(self,
                 http_host='localhost',
                 http_port='',
                 http_path='/',
                 post_fn=None):

        self.http_url = self._build_url(http_host, http_port, http_path)
        self.metrics = defaultdict(list)
        self.post_fn = post_fn or requests.post

    def _build_url(self, host, port, path):
        return 'http://{}{}{}'.format(host, port, path)

    def clear(self):
        logger.debug('initializing surfacer')
        self.metrics = defaultdict(list)

    def flush(self):
        logger.debug('flushing metrics: {}'.format(json.dumps(self.metrics)))
        try:
            response = self.post_fn(self.http_url, json=dict(self.metrics))
        except ConnectionError as e:
            logger.error('error submitting metrics: {}'.format(e))
        else:
            if not response.ok:
                logger.error('error submitting metrics: {}'.format(response))

    def record(self, metric):
        """
        Records a metric.  If the metric is a count it will take the
        last count.

        If the metric is a histogram or a gauge it will keep track of all
        requests in the order they are seen.

        :param metric:
        :return:
        """
        if metric.mtype == METRIC_TYPE.COUNTER:
            # always replace with the most current metric
            self.metrics[metric.name] = [metric.dict()]
        else:
            self.metrics[metric.name].append(metric.dict())
