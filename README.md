# python-apm

[![Build Status](https://travis-ci.org/dm03514/python-apm.svg?branch=master)](https://travis-ci.org/dm03514/python-apm)

Light-weight Python APM to add Custom Runtime Instrumentation  


## Overview

Python APM aims to provide an easy way to exposes metrics to a variety of web frameworks.  It provides
a number of primitives that aim to make this fun and simple.  

## Compatibility

Python APM is tested with python 2.7 and multiprocesing.

```
$ python
Python 2.7.12 (default, Dec  4 2017, 14:50:18)
[GCC 5.4.0 20160609] on linux2
```



## Quick Start Test App

- Configure your local python environment

```
$ pip install -r requirements.txt
```

- Start the dev server

```bash
$ make local-test-server-foreground
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

```bash
$ make test-local-test-server
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

```bash
2018-06-04 13:00:48,920 - pythonapm.contrib.flask - DEBUG - request_started
2018-06-04 13:00:48,920 - pythonapm.contrib.flask - DEBUG - request_finished
2018-06-04 13:00:48,921 - pythonapm.surfacers.logging - DEBUG - {'timestamp': datetime.datetime(2018, 6, 4, 13, 0, 48, 921243), 'value': 724, 'name': 'pythonapm.http.request.time_microseconds', 'type': 'histogram'}
2018-06-04 13:00:48,921 - werkzeug - INFO - 127.0.0.1 - - [04/Jun/2018 13:00:48] "GET / HTTP/1.1" 200 -
```

By default the Flask APM exposes metrics through a logging surfacer.  The above logs show that
the request took 724 microseconds!


## Flask Integration

Exposing the builtin metrics for the flask framework is trivial, and should only require a single step
to get going:

```python
from pythonapm.contrib.flask import PythonAPM

app = Flask(__name__)
apm = PythonAPM(app)
```

This enables a couple of different builtin flask scoped metrics:

- Request Time ([Histogram](https://prometheus.io/docs/concepts/metric_types/#histogram)) - `pythonapm.http.request.time_microseconds`
- Request / Response RSS diff ([Gauge](https://prometheus.io/docs/concepts/metric_types/#gauge)) - `pythonapm.http.request.rss.diff.byte`

PythonAPM also instruments the python language to expose:

- Number of `str` calls ([Counter](https://prometheus.io/docs/concepts/metric_types/#counter)) - `pythonapm.instruments.allocators.str.count`
- Number of times a module is imported through `__import__` (Counter) - `pythonapm.instruments.imports.count`

The python langauge metrics are configured through the monkey patching framework.  In order to tie them to 
the Flask Framework and Request/Response cycle a reference from the flask apm must be passed during initialization.

```python
app = Flask(__name__)

apm = PythonAPM(
    app,
    surfacer_list=(LogSurfacer(),)
)

monkey.patch_all(apm.surfacers)
```

The above example initializes the FlaskAPM and then monkey patches the import statement and the builtin `str` object.


## Architecture

### APM 
These are integration specific APMs (ie Flask, Django, Tornado, etc), and provide interfaces to configure and 
scope metrics to certain frameworks.  APMs require a collection of surfacers.  The default APM metric output 
format is through the log surfacer.  By hooking into pythons logging framework it allows the APM client the flexibility
to configure logging in a familiar way.  By pushing configuration up to the client the client should be able
to easily expose command line arguments to select different metric output formats (stdout, file, http, ect).

### Metrics

Metrics represent types of measurements.  The currently supported metric types are `Counter`, `Gauge` and `Histogram`.
APM metrics are built on top of these, ie string allocations are counted and are implemented in terms of a `Counter`. A 
request time is a distribution and it's implemented in terms of a `Histogram`. 

Each metric requires a name and a collection of `Surfacers`.  This follows the [Observer Design Pattern](https://en.wikipedia.org/wiki/Observer_pattern)

Metrics are emitted to surfacer on every metric call.  This allows metrics to stay slim but still enables surfacers
to control things like buffering or output formats.  The goal is that adding a new way to expose metrics shouldn't
have to touch any APM or metric handling code. 

### Surfacers

These are responsible for handling metrics emitted by events. The default surfacer is a `LogSurfacer` which will use
python's logging system to log each metric emitted to it.  The other surfacers available are:

- `RequestScopedHTTPSurfacer` - allows for batching of events and then submission of events over HTTP
- `InMemorySurfacer` - buffers all events, used for testing

Since metrics are emitted in a stream its up to surfacers to define their lifecycle states.  Currently, surfacers
require a `clear` method and a `flush` method.  If the surfacer supports buffering they can define it here.

These methods are used to achieve request scoped metrics.  At the beginning of a request `clear` is called and then
at the end of a request `flush` is called.  This allows for metrics to be aggregated across the lifecycle of a request!


Below are a couple of tutorials in hopes of making this clearer!!!


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

```python
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

```python
...
def __init__(self, http_host='localhost', http_port='', http_path='/'):
    self.http_url = self._build_url(http_host, http_port, http_path)
...
```

- Let's add a variable to track internal state of all metrics we've seen, we'll use a dictionary to keep track of keys.

```python
def __init__(...):
    self.metrics = defaultdict(list)  
```

- Since we're aggregating across a request, we need a little bit of custom logic to get the total
counts of metrics per request. Let's make this logic up!  For Counters we'll emit a single metric
with the total value seen during that request.  For other datatypes ie histogram/gauge we'll 
keep all values seen during the request in the order that we receive them:

```python
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

```python
def clear(self):
    self.metrics = defaultdict(list)    
```

- Now comes the fun part! At the end of each request flask APM will call the `flush()` method.  During
which we'll submit all metrics to the http resource specified.  If an error occurs we'll log it.

```python
def flush(self):
    logger.debug('flushing metrics: {}'.format(json.dumps(self.metrics)))
    try:
        response = self.post_fn(self.http_url, json=dict(self.metrics))
    except requests.exceptions.ConnectionError as e:
        logger.error('error submitting metrics: {}'.format(e))
    else:
        if not response.ok:
            logger.error('error submitting metrics: {}'.format(response))
```

All we should have left now is to configure our new surfacer for use with our APM.  By Default the APM
uses the `LogSurfacer` which will log all metrics through pythons built-in logger.  In addition, we'll
configure and inject our new surfacer for use.

- Add the new surfacer to the flask app

```python
http_surfacer = RequestScopedHTTPSurfacer(
    http_port=':9000',
)
```

- Configure the Flask APM with the http_surfacer

```python
apm = PythonAPM(
    app,
    surfacer_list=(LogSurfacer(), http_surfacer)
)
```

- Now if we run our application and make a request we should see the surfacer referenced and the 
http request that it submits should be failing

```bash
$ make start-local-test-server-foreground
FLASK_APP=tests/contrib/flask/fixtures/single_route_apm_app/app.py flask run
 * Serving Flask app "tests/contrib/flask/fixtures/single_route_apm_app/app.py"
 * Environment: production
   WARNING: Do not use the development server in a production environment.
   Use a production WSGI server instead.
 * Debug mode: off
2018-06-05 12:05:19,466 - pythonapm.surfacers.logging - DEBUG - {'name': 'pythonapm.instruments.imports.count', 'timestamp': '2018-06-05 12:05:19.466692', 'value': 1, 'type': 'counter'}
...
2018-06-05 12:05:19,511 - pythonapm.surfacers.logging - DEBUG - {'name': 'pythonapm.instruments.imports.count', 'timestamp': '2018-06-05 12:05:19.511347', 'value': 69, 'type': 'counter'}
2018-06-05 12:05:19,511 - werkzeug - INFO -  * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

```bash
$ make test-local-test-server
```

```bash
2018-06-05 12:18:19,097 - pythonapm.contrib.flask - DEBUG - request_started
2018-06-05 12:18:19,097 - pythonapm.surfacers.http - DEBUG - initializing surfacer
2018-06-05 12:18:19,098 - pythonapm.contrib.flask - DEBUG - request_finished
2018-06-05 12:18:19,099 - pythonapm.surfacers.logging - DEBUG - {'value': 911, 'type': 'histogram', 'timestamp': '2018-06-05 12:18:19.099610', 'name': 'pythonapm.http.request.time_microseconds'}
2018-06-05 12:18:19,100 - pythonapm.surfacers.http - DEBUG - flushing metrics: {"pythonapm.http.request.time_microseconds": [{"value": 911, "type": "histogram", "timestamp": "2018-06-05 12:18:19.099610", "name": "pythonapm.http.request.time_microseconds"}]}
2018-06-05 12:18:19,101 - pythonapm.surfacers.logging - DEBUG - {'value': 80, 'type': 'counter', 'timestamp': '2018-06-05 12:18:19.101499', 'name': 'pythonapm.instruments.imports.count'}
2018-06-05 12:18:19,103 - urllib3.connectionpool - DEBUG - Starting new HTTP connection (1): localhost
2018-06-05 12:18:19,104 - pythonapm.surfacers.http - ERROR - error submitting metrics: HTTPConnectionPool(host='localhost', port=9000): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7fc432ab2978>: Failed to establish a new connection: [Errno 111] Connection refused',))
2018-06-05 12:18:19,105 - werkzeug - INFO - 127.0.0.1 - - [05/Jun/2018 12:18:19] "GET / HTTP/1.1" 200 -
```


## Creating and integrating a new metric into Flask

This tutorial will display how to create a new metric and hook it into the flask APM.  For this
tutorial we will track how much RSS memory a request takes.  In order to do this we'll need
to hook into Flask Request/Response cycle. We'll record the memory usage at the beginning of the
request and then record and diff it at the end. The RSS Memory will lend well to a `Gauge` metric.
This will only tell the diff between the end request memory in use, NOT all allocations. 

- Add the gauge to `flask`.  This gauge will be instantiated when the APM is created.

```python
# __init__

self.rss_diff = Gauge(
   'pythonapm.http.request.rss.diff.bytes',
    surfacers=self.surfacers,
)
```
Each metric requires a unique name, and a reference to surfacers.  The surfacers will observe all
operations emitted by the metric.

- Add an entry to `request_data` dictionary to track the initial memory observed when the request
begins

```python
self.request_data = {
    ...
    'request_start_rss': None,
}
```

- Record the initial starting rss

```python
def request_started(...):
    self.request_data['request_start_rss'] = \
    psutil.Process(os.getpid()).memory_info().rss
```

- Add the recording of the rss diff to the request_finished hook
```python
def request_finished(self, *args, **kwargs):
    ...
    self.set_request_rss_diff()
    self.surfacers.flush()
```

- Add support for calculating the response rss value and recording the diff

```python
def set_request_rss_diff(self):
    diff = psutil.Process(os.getpid()).memory_info().rss \
           - self.request_data['request_start_rss']
    self.rss_diff.set(diff)
```

- Firing up the server and running the simple curl test should now show our new metric in the 
logs!

```bash
$ make start-local-test-server-foreground
$ make test-local-test-server

2018-06-05 13:05:54,847 - pythonapm.surfacers.logging - DEBUG - {'value': 0, 'type': 'gauge', 'timestamp': '2018-06-05 13:05:54.847537', 'name': 'pythonapm.http.request.rss.diff.bytes'}
2018-06-05 13:05:54,848 - pythonapm.surfacers.http - DEBUG - flushing metrics: {"pythonapm.http.request.time_microseconds": [{"value": 1066, "type": "histogram", "timestamp": "2018-06-05 13:05:54.846706", "name": "pythonapm.http.request.time_microseconds"}], "pythonapm.http.request.rss.diff.bytes": [{"value": 0, "type": "gauge", "timestamp": "2018-06-05 13:05:54.847537", "name": "pythonapm.http.request.rss.diff.bytes"}]}
```

## Development

- Running Tests

```
$ make test-unit
```

- Lint project

```
$ make lint
```

- Start test server in foreground for local development

```
$ make start-local-test-server-foreground
```

- Run service level tests against local server

```
$ make test-service
```

## Service Tests

Service tests are written in go and located in https://github.com/dm03514/python-apm-service-tests.

Currently there is a single test of the http surfacer.  Testing the surfacer requires:

- Setting up an HTTP server to handle the metric surfacing
- Making a request to the flask app
- Waiting (with timeout) for the HTTP metric request
- Making assertions on the metrics submitted

Because of the concurrent nature of this, go was chosen.  Starting and stopping http
servers, timeouts, and concurrency required of the test were trivial in go.  
