from flask import Flask

from pythonapm.contrib.flask import PythonAPM

import logging
import sys

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

app = Flask(__name__)
apm = PythonAPM(app)


@app.route('/')
def hello_world():
    return 'Hello, World!'
