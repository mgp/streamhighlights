from streamfinder import app
from flask.ext.assets import Environment, Bundle

env = Environment(app)
env.config['coffee_no_bare'] = True
# Compile Sass.
css = Bundle('style.scss', filters='scss', output='gen/style.css')
env.register('css_all', css)
# Compile CoffeeScript.
js = Bundle('app.coffee', filters='coffeescript', output='gen/app.js')
env.register('js_all', js)

# Configure the database.
import streamfinder.db
streamfinder.db.create_all()
@app.teardown_request
def shutdown_session(exception=None):
		streamfinder.db.session.remove()

