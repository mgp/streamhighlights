from flask import Flask

# TODO: Ensure that this is just matchstreamguide.
app = Flask(__name__)
# TODO: Don't set debug to True in production.
app.debug = True
app.secret_key = 'test_secret_key'

import matchstreamguide.configure
import matchstreamguide.views

