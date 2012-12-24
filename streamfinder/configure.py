from streamfinder import app
from flask.ext.assets import Environment, Bundle

# Configure asset management.
assets = Environment(app)
css = Bundle('style.scss', filters='scss', output='gen/style.css')
assets.register('css_all', css)

# Configure the database.
import streamfinder.db
streamfinder.db.create_all()
@app.teardown_request
def shutdown_session(exception=None):
		streamfinder.db.session.remove()

