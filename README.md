# python-apm
Light-weight Python APM to add Custom Runtime Instrumentation  

[Design Docs](https://docs.google.com/document/d/13t3OhHZidfE1O0hkLGldknzEhTNcPK0t3Ecc3PdNGTk/edit?usp=sharing)


## Overview


## Quick Start Test App

- Configure your local python environment

- Start the dev server

```
$ make start-simple-test-server                                                                [152/9591]FLASK_APP=tests/contrib/flask/fixtures/single_route_apm_app/app.py flask run
 * Serving Flask app "tests/contrib/flask/fixtures/single_route_apm_app/app.py"
 * Environment: production
   WARNING: Do not use the development server in a production environment.
   Use a production WSGI server instead.
 * Debug mode: off
patching
2018-06-04 12:38:03,602 - pythonapm.surfacers.logging - DEBUG - {'timestamp': datetime.datetime(2018, 6, 4, 12, 38, 3, 602773), 'name': 'pythonapm.instruments.imports.count', '
value': 1, 'type': 'counter'}
...
2018-06-04 12:58:35,075 - pythonapm.surfacers.logging - DEBUG - {'timestamp': datetime.datetime(2018, 6, 4, 12, 58, 35, 75778), 'value': 74, 'name': 'pythonapm.instruments.imports.count', 'type': 'counter'}
2018-06-04 12:58:35,076 - werkzeug - INFO -  * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

- Send a Request

```
$ make test-simple-test-server
curl -v http://127.0.0.1:5000/
*   Trying 127.0.0.1...
* Connected to 127.0.0.1 (127.0.0.1) port 5000 (#0)
> GET / HTTP/1.1
> Host: 127.0.0.1:5000
> User-Agent: curl/7.47.0
> Accept: */*
>
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Content-Type: text/html; charset=utf-8
< Content-Length: 13
< dm03514/pythonapm: 581404f0-0017-4909-98e6-62d90d8ee335
< Server: Werkzeug/0.14.1 Python/3.5.2
< Date: Mon, 04 Jun 2018 13:00:48 GMT
<
* Closing connection 0
Hello, World!
```

- Verify request Latency in Flask Logs

```
2018-06-04 13:00:48,920 - pythonapm.contrib.flask - DEBUG - request_started
2018-06-04 13:00:48,920 - pythonapm.contrib.flask - DEBUG - request_finished
2018-06-04 13:00:48,921 - pythonapm.surfacers.logging - DEBUG - {'timestamp': datetime.datetime(2018, 6, 4, 13, 0, 48, 921243), 'value': 724, 'name': 'pythonapm.http.request.time_ms', 'type': 'histogram'}
2018-06-04 13:00:48,921 - werkzeug - INFO - 127.0.0.1 - - [04/Jun/2018 13:00:48] "GET / HTTP/1.1" 200 -
```

By default the Flask APM exposes metrics through a logging surfacer.  The above logs show that
there was 724 microseconds!


## Flask Integration
- Wrap APP in flask PythonAPM

```
from pythonapm.contrib.flask import PythonAPM

app = Flask(__name__)
apm = PythonAPM(app)
```

- Configure an HTTPRequestScoped Surfacer

```
```


## Supported Metrics

- `__import__` call count (Counter)


- Flask
    - Request Time (Histogram)
    - Imports Per Request (Counter)


## Architecture

### APM 
These are integration specific APM, and provide interfaces to configure and scope metrics to certain frameworks.

### Surfacers

### Metrics


## Creating an HTTP Surfacer Tutorial

In order to explore python-apm we'll create a new surfacer.  This surfacer will be scoped to a request.  Because
surfacers receive a stream of metrics we'll need to have some custom logic to aggregate metrics.  

This surfacer aims to aggregate metrics across a request and then submit them to an HTTP endpoint.  In order to do this
we'll need to support a couple of different things:

- Track request/response lifeycle through `clear()` and `flush()` hooks
- Track count metrics so we only emit the total count
- Provide configuration to the end user for the HTTP endpoint

Let's get started!

- First we'll create a new surfacer in `pythonapm.surfacers`, and stub out its required methods

```
# pythonapm.surfacers.http

from . import Surfacer

class RequestScopedHTTPSurfacer(Surfacer):

    def clear(self): 
        pass
        
    def flush(self): 
        pass
    
    def record(self, metric):
        pass
```

- Next, we'll add an HTTP interface.  We'll require callers to specific an HTTP addr and path to 
submit data to.

```
...
def __init__(self, http_host='localhost', http_port='', http_path='/'):
    self.http_url = self._build_url(http_host, http_port, http_path)
...
```

- Let's add a variable to track internal state of all metrics we've seen, we'll use a dictionary to keep track of keys.

```
def __init__(...):
    self.metrics = defaultdict(list)  
```

- Since we're aggregating across a request, we need a little bit of custom logic to get the total
counts of metrics per request. Let's make this logic up!  For Counters we'll emit a single metric
with the total value seen during that request.  For other datatypes ie histogram/gauge we'll 
keep all values seen during the request in the order that we receive them:

```
def record(self, metric):
    """
    Records a metric.  If the metric is a count it will take the last count.

    If the metric is a histogram or a gauge it will keep track of all requests
    in the order they are seen.

    :param metric:
    :return:
    """
    if metric.mtype == METRIC_TYPE.COUNTER:
        # always replace with the most current metric
        self.metrics[metric.name] = [metric]
    else:
        self.metrics[metric.name].append(metric)
```

- Awesome! Now that we have request scoped metrics we have to support the request lifecycle hooks.
The Flask APM calls `clear()` at the beginning of each request.  Let's use this to initialize the
metrics for each request.

```
def clear(self):
    self.metrics = defaultdict(list)    
```

- Now comes the fun part! At the end of each request flask APM will call the `flush()` method.  During
which we'll submit all metrics to the http resource specified.  If an error occurs we'll log it.

```
def flush(self):
    logger.debug('flushing metrics: {}'.format(json.dumps(self.metrics)))
    response = self.post_fn(self.http_url, json=dict(self.metrics))
    if not response.ok:
        logger.error('error submitting metrics: {}'.format(response))
```
