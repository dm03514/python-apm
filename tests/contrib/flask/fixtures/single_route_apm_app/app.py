from flask import Flask

from pythonapm.contrib.flask import PythonAPM

import logging
import sys

from pythonapm.instruments import monkey
from pythonapm.surfacers.http import RequestScopedHTTPSurfacer
from pythonapm.surfacers.logging import LogSurfacer

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

http_surfacer = RequestScopedHTTPSurfacer(
    http_port=':9000',
)

app = Flask(__name__)

apm = PythonAPM(
    app,
    surfacer_list=(LogSurfacer(), http_surfacer)
)
monkey.patch_all(apm.surfacers)


@app.route('/')
def hello_world():
    return 'Hello, World!'
