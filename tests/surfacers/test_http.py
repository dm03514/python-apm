import unittest
from unittest.mock import MagicMock

from pythonapm.metrics import Metric, METRIC_TYPE
from pythonapm.surfacers.http import RequestScopedHTTPSurfacer


class RequestScopedHTTPSurfacerTestCase(unittest.TestCase):

    def test_record_counter_max_value(self):
        surfacer = RequestScopedHTTPSurfacer()
        surfacer.record(
            Metric(
                name='test.metric',
                mtype=METRIC_TYPE.COUNTER,
                value=1,
                timestamp='2017-01-01 00:00:00',
            ),
        )
        surfacer.record(
            Metric(
                name='test.metric',
                mtype=METRIC_TYPE.COUNTER,
                value=2,
                timestamp='2017-01-01 00:00:00',
            ),
        )
        self.assertEqual(len(surfacer.metrics['test.metric']), 1)
        self.assertEqual(surfacer.metrics['test.metric'][0]['value'], 2)

    def test_clear(self):
        surfacer = RequestScopedHTTPSurfacer()
        surfacer.record(
            Metric(
                name='test.metric',
                mtype=METRIC_TYPE.COUNTER,
                value=1,
                timestamp='2017-01-01 00:00:00',
            ),
        )
        surfacer.clear()
        self.assertEqual(len(surfacer.metrics), 0)

    def test_flush(self):
        post_fn = MagicMock()
        surfacer = RequestScopedHTTPSurfacer(post_fn=post_fn)

        surfacer.record(
            Metric(
                name='test.metric',
                mtype=METRIC_TYPE.COUNTER,
                value=1,
                timestamp='2017-01-01 00:00:00',
            ),
        )

        surfacer.record(
            Metric(
                name='test.metric.gauge',
                mtype=METRIC_TYPE.GAUGE,
                value=1,
                timestamp='2017-01-01 00:00:00',
            ),
        )

        surfacer.flush()
        post_fn.assert_called_once_with('http://localhost/', json={
            'metrics': {
                'test.metric.gauge': [
                    {
                        'type': 'gauge',
                        'timestamp': '2017-01-01 00:00:00',
                        'value': 1,
                        'name': 'test.metric.gauge'
                    }
                ],
                'test.metric': [
                    {
                        'type': 'counter',
                        'timestamp': '2017-01-01 00:00:00',
                        'value': 1,
                        'name': 'test.metric'
                    }
                ]
            }
        })
