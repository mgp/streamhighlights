from streamfinder import app

import common_db
from datetime import datetime, timedelta
import db
import flask
import functools
from flask_openid import OpenID
import pytz
import regex as re
import requests

oid = OpenID(app)


def _get_user_external_url(user):
	return common_db.get_external_url(user.url_by_id, user.url_by_name)

def _get_best_user_url(user):
	"""Returns the best URL for a given User."""
	if user.url_by_name is not None:
		prefix, remainder = user.url_by_name.split(common_db._USER_URL_SEPARATOR, 1)
		if prefix == common_db._USER_URL_STEAM_PREFIX:
			# The remainder is the Steam community identifier.
			# TODO
			return None
		elif prefix == common_db._USER_URL_TWITCH_PREFIX:
			# The remainder is the Twitch user name.
			return flask.url_for('twitch_user_by_name', name=remainder)
		else:
			return None

	prefix, remainder = user.url_by_id.split(common_db._USER_URL_SEPARATOR, 1)
	if prefix == common_db._USER_URL_STEAM_PREFIX:
		# The remainder is the Steam identifier.
		# TODO
		return None
	elif prefix == common_db._USER_URL_TWITCH_PREFIX:
		# The remainder is the Twitch identifier.
		return flask.url_for('twitch_user_by_id', twitch_id=int(remainder))
	else:
		return None

_GET_STREAMER_IMAGE_REGEX = re.compile('(?P<basename>.+)-300x300\.(?P<extension>\w+)$')

def _resize_large_picture(streamer, size):
	match = _GET_STREAMER_IMAGE_REGEX.search(streamer.image_url_large)
	if not match:
		return None
	return '%s-%sx%s.%s' % (
			match.group('basename'), size, size, match.group('extension'))

def _get_best_streamer_small_picture(streamer):
	"""Returns the URL for the best small picture of a streaming user."""
	if streamer.image_url_small:
		return streamer.image_url_small
	elif streamer.image_url_large:
		return _resize_large_picture(streamer, 28)

def _get_best_streamer_large_picture(streamer):
	"""Returns the URL for the best large picture of a streaming user."""
	if streamer.image_url_large:
		return _resize_large_picture(streamer, 150)

_URL_SEPARATOR = '-'
_PUNCTUATION_REGEX = re.compile(ur"\p{P}+")

def _url_format(s):
	return _PUNCTUATION_REGEX.sub('', s.lower())

def _get_team_url_part(team):
	parts = [str(team.team_id)]
	parts.extend(_url_format(team.name).split())
	return _URL_SEPARATOR.join(parts)

def _get_match_url_part_team_names(match_id, team1_name, team2_name):
	parts = [str(match_id)]
	parts.extend(_url_format(team1_name).split())
	parts.append('vs')
	parts.extend(_url_format(team2_name).split())
	return _URL_SEPARATOR.join(parts)

def _get_team_match_url_part(match, team):
	if match.team1:
		return _get_match_url_part_team_names(
				match.match_id, match.team1.name, team.name)
	elif match.team2:
		return _get_match_url_part_team_names(
				match.match_id, team.name, match.team2.name)

_TEAM_URL_SEPARATOR = ':'

def _get_team_external_url(team):
	prefix, remainder = team.fingerprint.split(_TEAM_URL_SEPARATOR, 1)
	if prefix == 'esea':
		return 'http://play.esea.net/teams/%s' % remainder

def _get_match_url_part(match):
	return _get_match_url_part_team_names(
			match.match_id, match.team1.name,  match.team2.name)

_MATCH_URL_SEPARATOR = ':'

def _get_match_external_url(match):
	prefix, remainder = match.fingerprint.split(_TEAM_URL_SEPARATOR, 1)
	if prefix == 'esea':
		return 'http://play.esea.net/index.php?s=stats&d=match&id=%s' % remainder


_DATETIME_FORMAT_LOCALIZED = '%a %b %d %I:%M%p'
_DATETIME_FORMAT_UTC = '%a %b %d %I:%M%p %Z'

def _get_readable_datetime(dt):
	"""Returns the datetime as a string, using the user's timezone if logged in."""
	utc_datetime = pytz.utc.localize(dt)
	timezone = flask.g.timezone
	if timezone:
		localized_datetime = utc_datetime.astimezone(timezone)
		return localized_datetime.strftime(_DATETIME_FORMAT_LOCALIZED)
	else:
		return utc_datetime.strftime(_DATETIME_FORMAT_UTC)

_SECONDS_PER_HOUR = 60 * 60
_SECONDS_PER_MINUTE = 60

def _get_time_between(dt1, dt2):
	td = dt1 - dt2
	seconds = td.seconds
	# Get the number of hours.
	hours = seconds / _SECONDS_PER_HOUR
	seconds %= _SECONDS_PER_HOUR
	# Get the number of minutes.
	minutes = seconds / _SECONDS_PER_MINUTE
	seconds %= _SECONDS_PER_MINUTE

	return td.days, hours, minutes

def _get_time_between_string(days, hours, minutes):
	parts = []

	# Append the days if needed.
	if days > 1:
		parts.append('%s days' % days)
	elif days:
		parts.append('1 day')
	# Append the hours if needed.
	if hours > 1:
		parts.append('%s hours' % hours)
	else:
		parts.append('1 hour')
	# Append the minutes if needed.
	if minutes > 1:
		parts.append('%s minutes' % minutes)
	else:
		parts.append('1 minute')

	return ', '.join(parts)

def _get_time_until(dt, now):
	days, hours, minutes = _get_time_between(dt, now)

	if not days and not hours and not minutes:
		return 'Starting now'
	else:
		return 'Starting in %s' % _get_time_between_string(days, hours, minutes)

def _get_time_since(dt, now):
	days, hours, minutes = _get_time_between(now, dt)
	return 'Started %s ago' % _get_time_between_string(days, hours, minutes)

def _get_readable_timedelta(dt, now=None):
	"""Returns the time until or time since the given datetime as a string."""
	if now is None:
		now = datetime.utcnow().replace(microsecond=0)
	if dt > now:
		return _get_time_until(dt, now)
	else:
		return _get_time_since(dt, now)


_DIVISION_SEPARATOR = '-'

def _get_league_id(division):
	"""Returns the unique league identifier from the given division value."""
	return division.split(_DIVISION_SEPARATOR)[0]

_DIVISION_NAMES = {
	'esea-s13-invite': 'Season 13 Invite',
	'esea-s13-intermediate': 'Season 13 Intermediate',
	'esea-s13-open': 'Season 13 Open'
}
_DIVISION_URLS = {
	'esea-s13-invite': 'http://play.esea.net/index.php?s=league&d=standings&division_id=2023',
	'esea-s13-intermediate': 'http://play.esea.net/index.php?s=league&d=standings&division_id=2024',
	'esea-s13-open': 'http://play.esea.net/index.php?s=league&d=standings&division_id=2025',
}

def _get_division_name(division):
	"""Returns the readable name of the given division value."""
	return _DIVISION_NAMES.get(division, None)

def _get_division_external_url(division):
	"""Returns the external URL for the given division value."""
	return _DIVISION_URLS.get(division, None)


jinja_env = app.jinja_env

# Filters for rendering users, teams, and matches.
jinja_env.filters['user_external_url'] = _get_user_external_url
jinja_env.filters['best_user_url'] = _get_best_user_url
jinja_env.filters['best_streamer_small_picture'] = _get_best_streamer_small_picture
jinja_env.filters['best_streamer_large_picture'] = _get_best_streamer_large_picture
jinja_env.filters['team_url_part'] = _get_team_url_part
jinja_env.filters['team_match_url_part'] = _get_team_match_url_part
jinja_env.filters['team_external_url'] = _get_team_external_url
jinja_env.filters['match_url_part'] = _get_match_url_part
jinja_env.filters['match_external_url'] = _get_match_external_url

# Filters for rendering times.
jinja_env.filters['readable_datetime'] = _get_readable_datetime
jinja_env.filters['readable_timedelta'] = _get_readable_timedelta

# Filters for rendering leagues and divisions.
jinja_env.filters['league_id'] = _get_league_id
jinja_env.filters['division_name'] = _get_division_name
jinja_env.filters['division_external_url'] = _get_division_external_url


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
			# XXX
			# flask.abort(requests.codes.unauthorized)
			client_id = 1

		flask.g.logged_in = True
		flask.g.client_id = client_id
		# TODO: Get from cookie
		flask.g.timezone = pytz.timezone('America/Los_Angeles')
		return f(*pargs, **kwargs)
	return decorated_function

def login_optional(f):
	@functools.wraps(f)
	def decorated_function(*pargs, **kwargs):
		client_id = _read_client_id_from_session()
		# XXX
		client_id = 1
		if client_id is None:
			flask.g.logged_in = False
			flask.g.client_id = None
			flask.g.timezone = None
		else:
			flask.g.logged_in = True
			flask.g.client_id = client_id
			# TODO: Get from cookie
			flask.g.timezone = pytz.timezone('America/Los_Angeles')

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
	return flask.render_template(template_name,
			matches=match_list.matches,
			prev_time=match_list.prev_time,
			prev_match_id=match_list.prev_match_id,
			next_time=match_list.next_time,
			next_match_id=match_list.next_match_id)

def _render_teams_list(db_getter, template_name):
	args = flask.request.args
	prev_name = args.get('prev_name')
	prev_team_id = args.get('prev_team_id')
	next_name = args.get('next_name')
	next_team_id = args.get('next_team_id')

	team_list = db_getter(flask.g.client_id,
			prev_name, prev_team_id, next_name, next_team_id)
	assert team_list is not None
	return flask.render_template(template_name,
			teams=team_list.teams,
			prev_name=team_list.prev_name,
			prev_team_id=team_list.prev_team_id,
			next_name=team_list.next_name,
			next_team_id=team_list.next_team_id)

def _render_streamers_list(db_getter, template_name):
	args = flask.request.args
	prev_name = args.get('prev_name')
	prev_streamer_id = args.get('prev_streamer_id')
	next_name = args.get('next_name')
	next_streamer_id = args.get('next_streamer_id')

	streamer_list = db_getter(flask.g.client_id,
			prev_name, prev_streamer_id, next_name, next_streamer_id)
	assert streamer_list is not None
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


def _get_id(url_part):
	parts = url_part.split(_URL_SEPARATOR)
	return int(parts[0])

_MATCH_DETAILS_ROUTE = '/matches/<match_id>'

@app.route(_MATCH_DETAILS_ROUTE)
@login_optional
def match_details(match_id):
	match_id = _get_id(match_id)
	args = flask.request.args
	prev_time = args.get('prev_time')
	prev_streamer_id = args.get('prev_streamer_id')
	next_time = args.get('next_time')
	next_streamer_id = args.get('next_streamer_id')

	match = db.get_displayed_match(flask.g.client_id, match_id,
			prev_time, prev_streamer_id, next_time, next_streamer_id)
	return flask.render_template('match.html', match=match)

@app.route(_MATCH_DETAILS_ROUTE, methods=['POST'])
@login_required
def update_match_details(match_id):
	match_id = _get_id(match_id)
	starred = flask.request.form.get('starred', None)
	if starred is not None:
		if starred == 'true':
			db.add_star_match(flask.g.client_id, match_id)
		else:
			db.remove_star_match(flask.g.client_id, match_id)
		return flask.jsonify(starred=starred)
	return flask.abort(requests.codes.server_error)

_TEAM_DETAILS_ROUTE = '/teams/<team_id>'

@app.route(_TEAM_DETAILS_ROUTE)
@login_optional
def team_details(team_id):
	team_id = _get_id(team_id)
	args = flask.request.args
	prev_time = args.get('prev_time')
	prev_match_id = args.get('prev_match_id')
	next_time = args.get('next_time')
	next_match_id = args.get('next_match_id')

	team = db.get_displayed_team(flask.g.client_id, team_id,
			prev_time, prev_match_id, next_time, next_match_id)
	return flask.render_template('team.html', team=team)

@app.route(_TEAM_DETAILS_ROUTE, methods=['POST'])
@login_required
def update_team_details(team_id):
	team_id = _get_id(team_id)
	starred = flask.request.form.get('starred', None)
	if starred is not None:
		if starred == 'true':
			db.add_star_team(flask.g.client_id, team_id)
		else:
			db.remove_star_team(flask.g.client_id, team_id)
		return flask.jsonify(starred=starred)
	return flask.abort(requests.codes.server_error)

@app.route('/users/twitch/<name>')
@login_optional
def twitch_user_by_name(name):
	args = flask.request.args
	prev_time = args.get('prev_time')
	prev_match_id = args.get('prev_match_id')
	next_time = args.get('next_time')
	next_match_id = args.get('next_match_id')

	streamer = db.get_displayed_streamer_by_twitch_name(
			flask.g.client_id, name,
			prev_time, prev_match_id, next_time, next_match_id)
	return flask.render_template('streamer.html', streamer=streamer)

@app.route('/users/twitch_id/<int:twitch_id>')
@login_optional
def twitch_user_by_id(twitch_id):
	args = flask.request.args
	prev_time = args.get('prev_time')
	prev_match_id = args.get('prev_match_id')
	next_time = args.get('next_time')
	next_match_id = args.get('next_match_id')

	streamer = db.get_displayed_streamer_by_twitch_id(
			flask.g.client_id, twitch_id,
			prev_time, prev_match_id, next_time, next_match_id)
	return flask.render_template('streamer.html', streamer=streamer)

