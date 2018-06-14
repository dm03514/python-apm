from flask import Flask

from pythonapm.contrib.flask import PythonAPM

import logging
import sys

from pythonapm.instruments import monkey
from pythonapm.surfacers import Surfacers
from pythonapm.surfacers.http import RequestScopedHTTPSurfacer
from pythonapm.surfacers.log import LogSurfacer


root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


surfacers = Surfacers((
    LogSurfacer(),
    RequestScopedHTTPSurfacer(
        http_port=':9000',
    ))
)

app = Flask(__name__)

apm = PythonAPM(
    app,
    surfacers=surfacers,
)

monkey.patch_all(surfacers)


@app.route('/')
def hello_world():
    hi = str('HIIIIIIIIIIIIIII')
    return str('{} Hello, World!'.format(hi))
