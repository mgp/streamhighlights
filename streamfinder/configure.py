from streamfinder import app
from flask.ext.assets import Environment, Bundle

env = Environment(app)
env.config['coffee_no_bare'] = True
# Compile Sass.
css = Bundle('style.scss', filters='scss', output='gen/style.css')
env.register('all_css', css)
# Compile CoffeeScript.
app_js = Bundle('app.coffee', filters='coffeescript', output='gen/app.js')
settings_js = Bundle('settings.coffee', filters='coffeescript', output='gen/settings.js')
env.register('app_js', app_js)
env.register('settings_js', settings_js)

# Configure the database.
import streamfinder.db
streamfinder.db.create_all()
@app.teardown_request
def shutdown_session(exception=None):
		streamfinder.db.session.remove()

