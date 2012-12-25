from streamfinder import app

import common_db
import db
import flask
import functools
from flask_openid import OpenID
import re

oid = OpenID(app)

def _get_best_streamer_url(streamer):
	return common_db.get_user_url(streamer.url_by_id, streamer.url_by_name)

_GET_STREAMER_IMAGE_REGEX = re.compile('(?P<basename>.+)-300x300\.(?P<extension>\w+)$')

def _get_best_streamer_picture(streamer):
	if streamer.image_url_small:
		return streamer.image_url_small
	elif streamer.image_url_large:
		match = _GET_STREAMER_IMAGE_REGEX.search(streamer.image_url_large)
		if not match:
			return None
		return '%s-28x28.%s' % (match.group('basename'), match.group('extension'))

jinja_env = app.jinja_env
jinja_env.filters['best_streamer_url'] = _get_best_streamer_url
jinja_env.filters['best_streamer_picture'] = _get_best_streamer_picture


def _read_client_id_from_session(session=None):
	"""Reads the client's user identifier from the session."""
	if session is None:
		session = flask.session
	user = session.get('user', None)
	if user is None:
		return None
	return user['id']

def login_required(f):
	@functools.wraps(f)
	def decorated_function(*pargs, **kwargs):
		client_id = _read_client_id_from_session()
		if client_id is None:
			# Return status code 401 if user is not logged in.
			flask.abort(requests.codes.unauthorized)

		flask.g.client_id = client_id
		return f(*pargs, **kwargs)
	return decorated_function

def login_optional(f):
	@functools.wraps(f)
	def decorated_function(*pargs, **kwargs):
		client_id = _read_client_id_from_session()
		if client_id is None:
			flask.g.client_id = None
		else:
			flask.g.client_id = client_id

		return f(*pargs, **kwargs)
	return decorated_function


@app.route('/')
def home():
	flask.render_template('home.html')


def _render_calendar(db_getter, template_name):
	args = flask.request.args
	prev_time = args.get('prev_time')
	prev_match_id = args.get('prev_match_id')
	next_time = args.get('next_time')
	next_match_id = args.get('next_match_id')

	calendar = db_getter(flask.g.client_id,
			prev_time, prev_match_id, next_time, next_match_id)
	assert calendar is not None
	# TODO
	return flask.render_template(template_name)

@app.route('/calendar/viewer')
@login_required
def viewer_calendar():
	return _render_calendar(db.get_displayed_viewer_calendar, 'viewer_calendar.html')

@app.route('/calendar/streamer')
@login_required
def streamer_calendar():
	return _render_calendar(db.get_displayed_streamer_calendar, 'streamer_calendar.html')


def _render_matches_list(db_getter, template_name):
	args = flask.request.args
	prev_time = args.get('prev_time')
	prev_match_id = args.get('prev_match_id')
	next_time = args.get('next_time')
	next_match_id = args.get('next_match_id')

	match_list = db_getter(flask.g.client_id,
			prev_time, prev_match_id, next_time, next_match_id)
	assert match_list is not None
	# TODO
	return flask.render_template('matches.html')

def _render_teams_list(db_getter, template_name):
	args = flask.request.args
	prev_name = args.get('prev_name')
	prev_team_id = args.get('prev_team_id')
	next_name = args.get('next_name')
	next_team_id = args.get('next_team_id')

	team_list = db_getter(flask.g.client_id,
			prev_name, prev_team_id, next_name, next_team_id)
	assert team_list is not None
	# TODO
	return flask.render_template(template_name)

def _render_streamers_list(db_getter, template_name):
	args = flask.request.args
	prev_name = args.get('prev_name')
	prev_streamer_id = args.get('prev_streamer_id')
	next_name = args.get('next_name')
	next_streamer_id = args.get('next_streamer_id')

	streamer_list = db_getter(flask.g.client_id,
			prev_name, prev_streamer_id, next_name, next_streamer_id)
	assert streamer_list is not None
	# TODO
	return flask.render_template(template_name,
			streamers=streamer_list.streamers,
			prev_name=streamer_list.prev_name,
			prev_streamer_id=streamer_list.prev_streamer_id,
			next_name=streamer_list.next_name,
			next_streamer_id=streamer_list.next_streamer_id)


@app.route('/starred/matches')
@login_required
def starred_matches():
	return _render_teams_list(db.get_starred_matches, 'starred_matches.html')

@app.route('/starred/teams')
@login_required
def starred_teams():
	return _render_teams_list(db.get_starred_teams, 'starred_teams.html')

@app.route('/starred/streamers')
@login_required
def starred_streamers():
	return _render_streamers_list(db.get_starred_streamers, 'starred_streamers.html')


@app.route('/matches')
@login_optional
def all_matches():
	return _render_matches_list(db.get_all_matches, 'matches.html')

@app.route('/teams')
@login_optional
def all_teams():
	return _render_teams_list(db.get_all_teams, 'teams.html')

@app.route('/streamers')
@login_optional
def all_streamers():
	return _render_streamers_list(db.get_all_streamers, 'streamers.html')


@app.route('/matches/<match_id>')
@login_optional
def match_details(match_id):
	args = flask.request.args
	prev_time = args.get('prev_time')
	prev_streamer_id = args.get('prev_streamer_id')
	next_time = args.get('next_time')
	next_streamer_id = args.get('next_streamer_id')

	match = db.get_displayed_match(flask.g.client_id, match_id,
			prev_time, prev_streamer_id, next_time, next_streamer_id)
	return flask.render_template('match.html')


@app.route('/teams/<team_id>')
@login_optional
def team_details(team_id):
	args = flask.request.args
	prev_time = args.get('prev_time')
	prev_match_id = args.get('prev_match_id')
	next_time = args.get('next_time')
	next_match_id = args.get('next_match_id')

	team = db.get_displayed_team(flask.g.client_id, team_id,
			prev_time, prev_match_id, next_time, next_match_id)
	return flask.render_template('team.html', team=team)

@app.route('/user/twitch/<name>')
@login_optional
def twitch_user_by_name(name):
	pass

