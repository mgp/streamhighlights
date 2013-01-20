from matchstreamguide import app
import db
from flask.ext.assets import Environment, Bundle
import os
import sqlalchemy as sa


class Configuration:
	"""Configuration used in all environments."""

	JINJA_TRIM_BLOCKS = True
	COFFEE_NO_BARE = True

class DevelopmentConfiguration(Configuration):
	"""Configuration used in a local development environment."""

	DEBUG = True
	TESTING = False
	DATABASE = 'postgresql'
	DATABASE_URI = (
			'postgresql+psycopg2://matchstreamguide:matchstreamguide@localhost/matchstreamguide')
	SECRET_KEY = 'secret_key'
	SCSS_FILTERS = 'scss'
	COFFEESCRIPT_FILTERS = 'coffeescript'

class TestingConfiguration(Configuration):
	"""Configuration used in a unit testing environment."""

	DEBUG = True
	TESTING = True
	DATABASE = 'sqlite'
	DATABASE_URI = 'sqlite:///:memory:'
	SECRET_KEY = 'secret_key'
	SCSS_FILTERS = 'scss'
	COFFEESCRIPT_FILTERS = 'coffeescript'

def _get_qualified_name(config):
	return __name__ + '.' + config.__name__

# Load default values used in all environments.
app.config.from_object(_get_qualified_name(Configuration))
# Specify the configurations for all environments that are not production.
_CONFIGURATIONS = {
		'dev': DevelopmentConfiguration,
		'test': TestingConfiguration
}

environment = os.environ.get('MSG_ENVIRONMENT', 'prod')
if environment == 'prod':
	# Load the configuration defined in a separate file for the production environment.
	prod_config_path = os.environ.get('MSG_PROD_CONFIG', '../etc/matchstreamguide.cfg')
	app.config.from_pyfile(prod_config_path)
else:
	# Load the configuration for the environment that is not production.
	app.config.from_object(_get_qualified_name(_CONFIGURATIONS[environment]))


# Remove some whitespace from the HTML.
app.jinja_env.trim_blocks = app.config['JINJA_TRIM_BLOCKS']
# Compile Coffeescript with the top-level function safety wrapper.
env = Environment(app)
env.config['coffee_no_bare'] = app.config['COFFEE_NO_BARE']
# Compile Sass.
css = Bundle('style.scss', filters=app.config['SCSS_FILTERS'], output='gen/style.css')
env.register('all_css', css)
# Compile CoffeeScript.
app_js = Bundle('app.coffee', filters='coffeescript', output='gen/app.js')
settings_js = Bundle(
		'settings.coffee', filters=app.config['COFFEESCRIPT_FILTERS'], output='gen/settings.js')
env.register('app_js', app_js)
env.register('settings_js', settings_js)

db.create_session(app.config['DATABASE'], app.config['DATABASE_URI'])

if environment != 'test':
	@app.teardown_request
	def shutdown_session(exception=None):
			db.session.remove()

