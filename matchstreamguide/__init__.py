from flask import Flask

# TODO: Ensure that this is just matchstreamguide.
app = Flask(__name__)

import matchstreamguide.configure
import matchstreamguide.views

