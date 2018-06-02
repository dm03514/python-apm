import unittest

from pythonapm.metrics import Metric, METRIC_TYPE


class MetricTestCase(unittest.TestCase):

    def test_metric_json(self):
        self.assertEqual(
            Metric(
                name='test.metric',
                mtype=METRIC_TYPE.GAUGE,
                value=10,
                timestamp='2017-01-01 00:00:00',
            ).dict(),
            {
                'name': 'test.metric',
                'type': 0,
                'value': 10,
                'timestamp': '2017-01-01 00:00:00',
            }
        )
