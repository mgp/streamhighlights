from streamfinder import app

from collections import defaultdict
import common_db
from datetime import datetime, timedelta
import db
import flask
import functools
from flask_openid import OpenID
from iso3166 import countries
import json
import pytz
import regex as re
import requests
import string
import urllib

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

# http://en.wikipedia.org/wiki/Mapping_of_Unicode_characters#General_Category
_CONNECTORS_REGEX = re.compile(ur"[\p{Pc}||\p{Pd}||\p{Zs}]", flags=re.V1)
_LETTERS_REGEX = re.compile(ur"[\P{L}--\p{N}--[_]]+", flags=re.V1)

def _get_indexed_name(displayed_name):
	s = displayed_name.lower()
	s = _CONNECTORS_REGEX.sub("_", s)
	s = _LETTERS_REGEX.sub("", s)
	return s

def _url_format(s):
	return _PUNCTUATION_REGEX.sub('', s.lower())

_URL_SEPARATOR = '-'
_PUNCTUATION_REGEX = re.compile(ur"\p{P}+")

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

def _get_match_url_part(match):
	return _get_match_url_part_team_names(
			match.match_id, match.team1.name,  match.team2.name)

_TEAM_URL_SEPARATOR = ':'

def _get_team_external_url(team):
	prefix, remainder = team.fingerprint.split(_TEAM_URL_SEPARATOR, 1)
	if prefix == 'esea':
		return 'http://play.esea.net/teams/%s' % remainder

_MATCH_URL_SEPARATOR = ':'

def _get_match_external_url(match):
	prefix, remainder = match.fingerprint.split(_TEAM_URL_SEPARATOR, 1)
	if prefix == 'esea':
		return 'http://play.esea.net/index.php?s=stats&d=match&id=%s' % remainder


_DATETIME_FORMAT_12_HOUR_LOCALIZED = '%a %b %d %I:%M%p'
_DATETIME_FORMAT_24_HOUR_LOCALIZED = '%a %b %d %H:%M'
_DATETIME_FORMAT_12_HOUR_UTC = '%a %b %d %I:%M%p %Z'
_DATETIME_FORMAT_24_HOUR_UTC = '%a %b %d %H:%M %Z'

def _get_readable_datetime(dt):
	"""Returns the datetime as a string, using the user's timezone if logged in."""
	utc_datetime = pytz.utc.localize(dt)
	time_zone = flask.g.time_zone
	if time_zone:
		localized_datetime = utc_datetime.astimezone(time_zone)
		if flask.g.time_format == '12_hour':
			datetime_format = _DATETIME_FORMAT_12_HOUR_LOCALIZED
		else:
			datetime_format = _DATETIME_FORMAT_24_HOUR_LOCALIZED
		return localized_datetime.strftime(datetime_format)
	else:
		if flask.g.time_format == '12_hour':
			datetime_format = _DATETIME_FORMAT_12_HOUR_UTC
		else:
			datetime_format = _DATETIME_FORMAT_24_HOUR_UTC
		return utc_datetime.strftime(datetime_format)

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
	elif hours:
		parts.append('1 hour')
	# Append the minutes if needed.
	if minutes > 1:
		parts.append('%s minutes' % minutes)
	elif minutes:
		parts.append('1 minute')

	return ', '.join(parts)

def _get_time_until(dt, now):
	days, hours, minutes = _get_time_between(dt, now)
	return 'starting in %s' % _get_time_between_string(days, hours, minutes)

def _get_time_since(dt, now):
	days, hours, minutes = _get_time_between(now, dt)
	return 'started %s ago' % _get_time_between_string(days, hours, minutes)

_ONE_MINUTE = timedelta(minutes=1)

def _get_readable_timedelta(dt, now=None):
	"""Returns the time until or time since the given datetime as a string."""
	if now is None:
		now = datetime.utcnow().replace(microsecond=0)
	if dt >= now + _ONE_MINUTE:
		return _get_time_until(dt, now)
	elif dt <= now - _ONE_MINUTE:
		return _get_time_since(dt, now)
	else:
		return 'starting now'

_DATETIME_QUERY_PARAM_FORMAT = '%Y-%m-%dT%H:%M'

def _get_datetime_query_param(datetime):
	return datetime.strftime(_DATETIME_QUERY_PARAM_FORMAT)


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
jinja_env.filters['datetime_query_param'] = _get_datetime_query_param

# Filters for rendering leagues and divisions.
jinja_env.filters['league_id'] = _get_league_id
jinja_env.filters['division_name'] = _get_division_name
jinja_env.filters['division_external_url'] = _get_division_external_url


def _get_client_values(client):
	flask.g.logged_in = True
	flask.g.client_id = client['id']
	flask.g.client_name = client['name']
	flask.g.client_auth = client['auth']
	flask.g.time_format = client['time_format']
	time_zone = client.get('time_zone')
	flask.g.time_zone = pytz.timezone(time_zone) if time_zone else None

def login_required(f):
	page_name = f.__name__

	@functools.wraps(f)
	def decorated_function(*pargs, **kwargs):
		client = flask.session.get('client', None)
		if client is None:
			flask.abort(requests.codes.unauthorized)

		_get_client_values(client)
		flask.g.page_name = page_name
		return f(*pargs, **kwargs)
	return decorated_function

def login_optional(f):
	page_name = f.__name__

	@functools.wraps(f)
	def decorated_function(*pargs, **kwargs):
		client = flask.session.get('client', None)
		if client:
			_get_client_values(client)
		else:
			flask.g.logged_in = False
			flask.g.client_id = None
			flask.g.time_format = db._DEFAULT_SETTINGS_TIME_FORMAT
			flask.g.time_zone = None
		flask.g.page_name = page_name
		return f(*pargs, **kwargs)
	return decorated_function


@app.route('/')
@login_optional
def home():
	return flask.render_template('home.html')

def _get_int(args, key):
	"""Returns the value under the given key as an integer.

	Raises ValueError if the value cannot be converted to an integer. If the key
	is missing, returns None.
	"""
	value = args.get(key)
	return None if value is None else int(value)

def _get_datetime(args, key):
	"""Returns the value under the given key as a datetime.

	Raises ValueError if the value cannot be converted to a datetime. If the key
	is missing, returns None.
	"""
	value = args.get(key)
	if value is None:
		return None
	return datetime.strptime(value, _DATETIME_QUERY_PARAM_FORMAT)


def _render_calendar(db_getter, template_name):
	args = flask.request.args
	prev_time = _get_datetime(args, 'prev_time')
	prev_match_id = _get_int(args, 'prev_match_id')
	next_time = _get_datetime(args, 'next_time')
	next_match_id = _get_int(args, 'next_match_id')

	calendar = db_getter(flask.g.client_id,
			prev_time, prev_match_id, next_time, next_match_id)
	assert calendar is not None
	return flask.render_template(template_name, calendar=calendar)

@app.route('/calendar/viewer')
@login_required
def viewer_calendar():
	return _render_calendar(db.get_displayed_viewer_calendar, 'calendar_viewer.html')

@app.route('/calendar/streamer')
@login_required
def streamer_calendar():
	return _render_calendar(db.get_displayed_streamer_calendar, 'calendar_streamer.html')


def _render_matches_list(db_getter, template_name):
	args = flask.request.args
	prev_time = _get_datetime(args, 'prev_time')
	prev_match_id = _get_int(args, 'prev_match_id')
	next_time = _get_datetime(args, 'next_time')
	next_match_id = _get_int(args, 'next_match_id')

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
	prev_team_id = _get_int(args, 'prev_team_id')
	next_name = args.get('next_name')
	next_team_id = _get_int(args, 'next_team_id')

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
	prev_streamer_id = _get_int(args, 'prev_streamer_id')
	next_name = args.get('next_name')
	next_streamer_id = _get_int(args, 'next_streamer_id')

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
	return _render_matches_list(db.get_starred_matches, 'matches_starred.html')

@app.route('/starred/teams')
@login_required
def starred_teams():
	return _render_teams_list(db.get_starred_teams, 'teams_starred.html')

@app.route('/starred/streamers')
@login_required
def starred_streamers():
	return _render_streamers_list(db.get_starred_streamers, 'streamers_starred.html')


@app.route('/matches')
@login_optional
def all_matches():
	return _render_matches_list(db.get_all_matches, 'matches_all.html')

@app.route('/teams')
@login_optional
def all_teams():
	return _render_teams_list(db.get_all_teams, 'teams_all.html')

@app.route('/streamers')
@login_optional
def all_streamers():
	return _render_streamers_list(db.get_all_streamers, 'streamers_all.html')


def _get_id(url_part):
	parts = url_part.split(_URL_SEPARATOR)
	return int(parts[0])

_MATCH_DETAILS_ROUTE = '/matches/<match_id>'

@app.route(_MATCH_DETAILS_ROUTE)
@login_optional
def match_details(match_id):
	try:
		match_id = _get_id(match_id)
		args = flask.request.args
		prev_time = _get_datetime(args, 'prev_time')
		prev_streamer_id = _get_int(args, 'prev_streamer_id')
		next_time = _get_datetime(args, 'next_time')
		next_streamer_id = _get_int(args, 'next_streamer_id')

		match = db.get_displayed_match(flask.g.client_id, match_id,
				prev_time, prev_streamer_id, next_time, next_streamer_id)
		return flask.render_template('match.html', match=match)
	except ValueError:
		# Raised if any value is not the expected type.
		flask.abort(requests.codes.not_found)
	except common_db.DbException:
		flask.abort(requests.codes.not_found)

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
	flask.abort(requests.codes.server_error)

_TEAM_DETAILS_ROUTE = '/teams/<team_id>'

@app.route(_TEAM_DETAILS_ROUTE)
@login_optional
def team_details(team_id):
	try:
		team_id = _get_id(team_id)
		args = flask.request.args
		prev_time = _get_datetime(args, 'prev_time')
		prev_match_id = _get_int(args, 'prev_match_id')
		next_time = _get_datetime(args, 'next_time')
		next_match_id = _get_int(args, 'next_match_id')

		team = db.get_displayed_team(flask.g.client_id, team_id,
				prev_time, prev_match_id, next_time, next_match_id)
		return flask.render_template('team.html', team=team)
	except ValueError:
		# Raised if any value is not the expected type.
		flask.abort(requests.codes.not_found)
	except common_db.DbException:
		flask.abort(requests.codes.not_found)

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
	flask.abort(requests.codes.server_error)

@app.route('/users/twitch/<name>')
@login_optional
def twitch_user_by_name(name):
	try:
		args = flask.request.args
		prev_time = _get_datetime(args, 'prev_time')
		prev_match_id = _get_int(args, 'prev_match_id')
		next_time = _get_datetime(args, 'next_time')
		next_match_id = _get_int(args, 'next_match_id')

		streamer = db.get_displayed_streamer_by_twitch_name(
				flask.g.client_id, name,
				prev_time, prev_match_id, next_time, next_match_id)
		return flask.render_template('streamer.html', streamer=streamer)
	except ValueError:
		# Raised if any value is not the expected type.
		flask.abort(requests.codes.not_found)
	except common_db.DbException:
		flask.abort(requests.codes.not_found)

@app.route('/users/twitch_id/<twitch_id>')
@login_optional
def twitch_user_by_id(twitch_id):
	try:
		twitch_id = int(twitch_id)
		args = flask.request.args
		prev_time = _get_datetime(args, 'prev_time')
		prev_match_id = _get_int(args, 'prev_match_id')
		next_time = _get_datetime(args, 'next_time')
		next_match_id = _get_int(args, 'next_match_id')

		streamer = db.get_displayed_streamer_by_twitch_id(
				flask.g.client_id, twitch_id,
				prev_time, prev_match_id, next_time, next_match_id)
		return flask.render_template('streamer.html', streamer=streamer)
	except ValueError:
		# Raised if any value is not the expected type.
		flask.abort(requests.codes.not_found)
	except common_db.DbException:
		flask.abort(requests.codes.not_found)


_TIME_FORMAT_TO_VALUE_MAP = {
		'12 hour': '12_hour',
		'24 hour': '24_hour',
}

_SORTED_COUNTRY_NAMES = tuple((country.name, country.alpha2) for country in countries)

_COUNTRY_CODE_TO_TIME_ZONE_MAP = {
	'AQ': {
		'Palmer': 'Antarctica/Palmer',
		'Rothera': 'Antarctica/Rothera',
		'Syowa': 'Antarctica/Syowa',
		'Mawson': 'Antarctica/Mawson',
		'Vostok': 'Antarctica/Vostok',
		'Davis': 'Antarctica/Davis',
		'Casey': 'Antarctica/Casey',
		"Dumont D'Urville": 'Antarctica/DumontDUrville',
	},
	'AR': {
  	'Buenos Aires': 'America/Argentina/Buenos_Aires',
	},
	'AU': {
		'Western Time - Perth': 'Australia/Perth',
		'Central Time - Adelaide': 'Australia/Adelaide',
		'Central Time - Darwin': 'Australia/Darwin',
		'Eastern Time - Brisbane': 'Australia/Brisbane',
		'Eastern Time - Hobart': 'Australia/Hobart',
		'Eastern Time - Melbourne, Sydney': 'Australia/Melbourne',
	},
	'BR': {
		'Boa Vista': 'America/Boa_Vista',
		'Campo Grande': 'America/Campo_Grande',
		'Cuiaba': 'America/Cuiaba',
		'Manaus': 'America/Manaus',
		'Porto Velho': 'America/Porto_Velho',
		'Rio Branco': 'America/Rio_Branco',
		'Araguaina': 'America/Araguaina',
		'Belem': 'America/Belem',
		'Fortaleza': 'America/Fortaleza',
		'Maceio': 'America/Maceio',
		'Recife': 'America/Recife',
		'Sao Paulo': 'America/Sao_Paulo',
		'Noronha': 'America/Noronha',
	},
	'CA': {
		'Pacific Time - Vancouver': 'America/Vancouver',
		'Pacific Time - Whitehorse': 'America/Whitehorse',
		'Mountain Time - Dawson Creek': 'America/Dawson_Creek',
		'Mountain Time - Edmonton': 'America/Edmonton',
		'Mountain Time - Yellowknife': 'America/Yellowknife',
		'Central Time - Regina': 'America/Regina',
		'Central Time - Winnipeg': 'America/Winnipeg',
		'Eastern Time - Iqaluit': 'America/Iqaluit',
		'Eastern Time - Montreal': 'America/Montreal',
		'Eastern Time - Toronto': 'America/Toronto',
		'Atlantic Time - Halifax': 'America/Halifax',
		'Newfoundland Time - St Johns': 'America/St_Johns',
	},
	'CD': {
		'Kinshasa': 'Africa/Kinshasa',
		'Lubumbashi': 'Africa/Lubumbashi',
	},
	'CL': {
  	'Easter Island': 'Pacific/Easter',
		'Santiago': 'America/Santiago',
	},
	'CN': {
		'Shanghai': 'Asia/Shanghai',
	},
	'EC': {
		'Galapagos': 'Pacific/Galapagos',
		'Guayaquil': 'America/Guayaquil',
	},
	'ES': {
		'Canary Islands': 'Atlantic/Canary',
		'Ceuta': 'Africa/Ceuta',
		'Madrid': 'Europe/Madrid',
	},
	'FM': {
		'Chuuk': 'Pacific/Chuuk',
		'Kosrae': 'Pacific/Kosrae',
		'Pohnpei': 'Pacific/Ponape',
	},
	'GL': {
		'Thule': 'America/Thule',
		'Godthab': 'America/Godthab',
		'Scoresbysund': 'America/Scoresbysund',
		'Danmarkshavn': 'America/Danmarkshavn',
	},
	'ID': {
		'Jakarta': 'Asia/Jakarta',
		'Makassar': 'Asia/Makassar',
		'Jayapura': 'Asia/Jayapura',
	},
	'KI': {
		'Tarawa': 'Pacific/Tarawa',
		'Kiritimati': 'Pacific/Kiritimati',
	},
	'KZ': {
		'Aqtau': 'Asia/Aqtau',
		'Aqtobe': 'Asia/Aqtobe',
		'Almaty': 'Asia/Almaty',
	},
	'MH': {
		'Kwajalein': 'Pacific/Kwajalein',
		'Majuro': 'Pacific/Majuro',
	},
	'MN': {
		'Hovd': 'Asia/Hovd',
		'Choibalsan': 'Asia/Choibalsan',
		'Ulaanbaatar': 'Asia/Ulaanbaatar',
	},
	'MX': {
		'Pacific Time - Tijuana': 'America/Tijuana',
		'Mountain Time - Hermosillo': 'America/Hermosillo',
		'Mountain Time - Chihuahua, Mazatlan': 'America/Chihuahua',
		'Central Time - Mexico City': 'America/Mexico_City',
	},
	'MY': {
		'Kuala_Lumpur': 'Asia/Kuala_Lumpur',
	},
	'NZ': {
		'Auckland': 'Pacific/Auckland',
	},
	'PF': {
		'Tahiti': 'Pacific/Tahiti',
		'Marquesas': 'Pacific/Marquesas',
		'Gambier': 'Pacific/Gambier',
	},
	'PS': {
		'Gaza': 'Asia/Gaza',
	},
	'PT': {
		'Azores': 'Atlantic/Azores',
		'Lisbon': 'Europe/Lisbon',
	},
	'RU': {
		'Moscow-01 - Kaliningrad': 'Europe/Kaliningrad',
		'Moscow+00': 'Europe/Moscow',
		'Moscow+00 - Samara': 'Europe/Samara',
		'Moscow+02 - Yekaterinburg': 'Asia/Yekaterinburg',
		'Moscow+03 - Omsk, Novosibirsk': 'Asia/Omsk',
		'Moscow+04 - Krasnoyarsk': 'Asia/Krasnoyarsk',
		'Moscow+05 - Irkutsk': 'Asia/Irkutsk',
		'Moscow+06 - Yakutsk': 'Asia/Yakutsk',
		'Moscow+07 - Yuzhno-Sakhalinsk': 'Asia/Sakhalin',
		'Moscow+08 - Petropavlovsk-Kamchatskiy': 'Asia/Kamchatka',
		'Moscow+08 - Magadan': 'Asia/Magadan',
	},
	'UA': {
		'Kiev': 'Europe/Kiev',
	},
	'UM': {
		'Johnston': 'Pacific/Johnston',
		'Midway': 'Pacific/Midway',
		'Wake': 'Pacific/Wake',
	},
	'US': {
		'Hawaii Time': 'Pacific/Honolulu',
		'Alaska Time': 'America/Anchorage',
		'Pacific Time': 'America/Los_Angeles',
		'Mountain Time': 'America/Denver',
		'Mountain Time - Arizona': 'America/Phoenix',
		'Central Time': 'America/Chicago',
		'Eastern Time': 'America/New_York', 
	},
	'UZ': {
		'Tashkent': 'Asia/Tashkent',
	}
}

_TRANSLATION_TABLE = string.maketrans("_", " ")
def _get_time_zone_name(time_zone):
	return str(time_zone.rsplit('/', 1)[1]).translate(_TRANSLATION_TABLE)

def _init_time_zone_map():
	"""Creates a mapping from country codes to time zones.

	A country can contain multiple time zones, therefore the value of a country
	code is also a mapping, where time zones are mapped to by their displayed
	names.
	"""

	for time_zone_map in _COUNTRY_CODE_TO_TIME_ZONE_MAP.itervalues():
		for name, time_zone in time_zone_map.iteritems():
			time_zone_map[name] = pytz.timezone(time_zone)

	for country_name, country_code in _SORTED_COUNTRY_NAMES:
		country_code = country_code.upper()

		if country_code not in pytz.country_timezones:
			continue
		time_zones = pytz.country_timezones[country_code]
		if len(time_zones) > 1:
			assert country_code in _COUNTRY_CODE_TO_TIME_ZONE_MAP
		else:
			time_zone = time_zones[0]
			time_zone_name = _get_time_zone_name(time_zone)
			time_zone_map = {
				time_zone_name: pytz.timezone(time_zone),
			}
			_COUNTRY_CODE_TO_TIME_ZONE_MAP[country_code] = time_zone_map
	
_init_time_zone_map()

_MINUTES_PER_DAY = 1440
_SECONDS_PER_MINUTE = 60

def _get_offset_minutes(now, time_zone):
	utc_offset = time_zone.utcoffset(now, is_dst=False)
	offset_minutes = 0
	offset_minutes += (utc_offset.days * _MINUTES_PER_DAY)
	offset_minutes += (utc_offset.seconds / _SECONDS_PER_MINUTE)
	return offset_minutes

def _get_offset_minutes_map(now):
	"""Given the current time, extends the mapping from country codes to time zones
	to also include the UTC offset for each time zone.

	Each displayed time zone name maps to a pair containing the time zone and its
	UTC offset in minutes.
	"""

	offset_minutes_set = set()
	country_offset_minutes_map = {}
	for country_code, time_zone_map in _COUNTRY_CODE_TO_TIME_ZONE_MAP.iteritems():
		name_offset_minutes_list = []
		for name, time_zone in time_zone_map.iteritems():
			offset_minutes = _get_offset_minutes(now, time_zone)
			offset_minutes_set.add(offset_minutes)
			name_offset_minutes_list.append((name, time_zone.zone, offset_minutes))

		country_offset_minutes_map[country_code] = sorted(
				name_offset_minutes_list, key=lambda e: (e[2], e[0]))

	return country_offset_minutes_map, offset_minutes_set

def _get_displayed_offset(offset_minutes):
	if offset_minutes < 0:
		offset_prefix = 'UTC-'
		offset_minutes = abs(offset_minutes)
	elif offset_minutes > 0:
		offset_prefix = 'UTC+'
	else:
		return 'UTC'
	return '%s%02d:%02d' % (offset_prefix, offset_minutes / 60, offset_minutes % 60)

def _get_displayed_offset_map(now, offset_minutes_set):
	"""Given all UTC offsets, returns a map from each offset to a tuple containing
	the displayed offset, the current time in 12-hour format after applying the
	offset, and the current time in 24-hour format after applying the offset.
	"""

	displayed_offset_map = {}
	for offset_minutes in sorted(offset_minutes_set):
		displayed_offset = _get_displayed_offset(offset_minutes)
		now_offset = now + timedelta(minutes=offset_minutes)

		displayed_offset_map[offset_minutes] = (
				displayed_offset, 
				now_offset.strftime(_DATETIME_FORMAT_12_HOUR_LOCALIZED),
				now_offset.strftime(_DATETIME_FORMAT_24_HOUR_LOCALIZED))
	return displayed_offset_map


_SETTINGS_ROUTE = '/settings'

def _render_settings(
		selected_time_format, selected_country_code, selected_time_zone,
		errors={}, saved=None):
	now = datetime.utcnow()
	datetime_12_hour = now.strftime(_DATETIME_FORMAT_12_HOUR_UTC)
	datetime_24_hour = now.strftime(_DATETIME_FORMAT_24_HOUR_UTC)
	country_offset_minutes_map, offset_minutes_set = _get_offset_minutes_map(now)
	displayed_offset_map = _get_displayed_offset_map(now, offset_minutes_set)

	return flask.render_template('settings.html',
			# The current user settings.
			selected_time_format=selected_time_format,
			selected_country_code=selected_country_code,
			selected_time_zone=selected_time_zone,
			# The time format and country options.
			time_formats_map=_TIME_FORMAT_TO_VALUE_MAP,
			sorted_country_names=_SORTED_COUNTRY_NAMES,
			# Data for changing the time zone.
			server_time_12_hour=datetime_12_hour,
			server_time_24_hour=datetime_24_hour,
			country_offset_minutes_map=json.dumps(country_offset_minutes_map),
			displayed_offset_map=json.dumps(displayed_offset_map),
			errors=errors,
			saved=saved)

@app.route(_SETTINGS_ROUTE)
@login_required
def get_settings():
	settings = db.get_settings(flask.g.client_id)
	return _render_settings(
			settings.time_format, settings.country, settings.time_zone)

_TIME_FORMAT_ERROR = 'time_format'
_COUNTRY_ERROR = 'country'
_TIME_ZONE_ERROR = 'time_zone'

@app.route(_SETTINGS_ROUTE, methods=['POST'])
@login_required
def save_settings():
	errors = defaultdict(list)

	# Validate the time format.
	time_format = flask.request.form['time_format']
	if time_format is None:
		errors[_TIME_FORMAT_ERROR].append('missing')
	elif time_format not in db._SETTINGS_TIME_FORMATS:
		errors[_TIME_FORMAT_ERROR].append('invalid')

	# Validate the country code.
	country = flask.request.form.get('country', None)
	if not country:
		country = None
	if country:
		if (len(country) != 2) or (country not in _COUNTRY_CODE_TO_TIME_ZONE_MAP):
			errors[_COUNTRY_ERROR].append('invalid')

	# Validate the time zone.
	time_zone = flask.request.form.get('time_zone', None)
	if not time_zone:
		time_zone = None
	if time_zone:
		if not country:
			# Cannot have a time zone without a country specified.
			errors[_COUNTRY_ERROR].append('missing')
		else:
			# Validate the time zone in the selected country.
			country_time_zones = (time_zone.zone
					for time_zone in _COUNTRY_CODE_TO_TIME_ZONE_MAP[country].itervalues())
			if time_zone not in country_time_zones:
				errors[_TIME_ZONE_ERROR].append('invalid')

	# Update the client settings if there are no errors.
	if not errors:
		# Save the settings in the database.
		db.save_settings(flask.g.client_id, time_format, country, time_zone)
		# Store the settings in the session.
		client = flask.session['client']
		client['time_format'] = time_format
		if time_zone:
			client['time_zone'] = time_zone
		else:
			client.pop('time_zone', None)
		# Changes to mutable data are not picked up automatically.
		flask.session.modified = True
	saved = not errors

	return _render_settings(time_format, country, time_zone, errors, saved)


@app.route('/privacy')
@login_optional
def privacy():
	return flask.render_template('privacy.html')

@app.route('/terms')
@login_optional
def terms():
	return flask.render_template('terms.html')

@app.route('/about')
@login_optional
def about():
	return flask.render_template('about.html')


@app.errorhandler(requests.codes.unauthorized)
def unauthorized(e):
	response = 'unauthorized'
	status = requests.codes.unauthorized
	headers = {
		'Content-Type': 'text/plain; charset=utf-8',
	}
	return flask.make_response((response, status, headers))

@app.errorhandler(requests.codes.not_found)
@login_optional
def page_not_found(e):
	return flask.render_template('error_404.html'), 404

@app.errorhandler(requests.codes.server_error)
@login_optional
def internal_server_error(e):
	return flask.render_template('error_500.html'), 500


def _finish_login(client_id, client_name, auth):
	settings = db.get_settings(client_id)
	client = {
		'id': client_id,
		'name': client_name,
		'auth': auth,
		'time_format': settings.time_format,
	}
	if settings.time_zone:
		client['time_zone'] = settings.time_zone
	flask.session['client'] = client
	# Default session lifetime is 31 days.
	flask.session.permanent = True

	# Redirect to the URL that the user came from.
	next_url = flask.session.pop('next_url', None)
	if next_url is None:
		next_url = flask.url_for('home')
	return flask.redirect(next_url)


_STEAM_OPEN_ID_URL = 'http://steamcommunity.com/openid'

@app.route('/login/steam')
@oid.loginhandler
def log_in_steam():
	return oid.try_login('http://steamcommunity.com/openid')

_GET_STEAM_ID_REGEX = re.compile('http://steamcommunity.com/openid/id/(?P<steam_id>\d+)$')
_STEAM_PLAYER_SUMMARY_URL = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002'
_STEAM_WEB_API_KEY = '52F753EAA320784E9CD999A78997B5D1'

@oid.after_login
def complete_log_in_steam(response):
	# Get the user's Steam identifier from the OpenID response.
	steam_id_match = _GET_STEAM_ID_REGEX.search(response.identity_url)
	if not steam_id_match:
		flask.abort(requests.codes.server_error)
	steam_id = int(steam_id_match.group('steam_id'))

	# Given the user's Steam ID, get the user's information.
	user_url = ('%s/?%s' % (
			_STEAM_PLAYER_SUMMARY_URL,
			urllib.urlencode({
					'key': _STEAM_WEB_API_KEY,
					'format': 'json',
					'steamids': steam_id
			})
	))
	response = requests.get(user_url)
	if response.status_code != requests.codes.ok:
		flask.abort(requests.codes.server_error)
	elif ('response' not in response.json) or not response.json['response']['players']:
		flask.abort(requests.codes.server_error)
	player = response.json['response']['players'][0]
	personaname = player['personaname']
	profile_url = player.get('profileurl', None)
	avatar = player.get('avatar', None)
	avatar_full = player.get('avatarfull', None)

	# Get the user's identifier and update the session so logged in.
	user_id = db.steam_user_logged_in(
			steam_id, personaname, profile_url, avatar, avatar_full)
	return _finish_login(user_id, personaname, 'steam')


_TWITCH_CLIENT_ID = 'd2wc1690jmvteanst3guuwu0wbcg2by'
_TWITCH_CLIENT_SECRET = 'ms71l6svzlus4xwpbmbgogh4ux88gyf'
_TWITCH_REDIRECT_URI = 'http://localhost:5000/complete-login/twitch'

_TWITCH_API_URI_PREFIX = 'https://api.twitch.tv/kraken'
_TWITCH_OAUTH_AUTHORIZE_URL = ('%s/oauth2/authorize?%s' % (
		_TWITCH_API_URI_PREFIX,
		urllib.urlencode({
			'client_id': _TWITCH_CLIENT_ID,
			'redirect_uri': _TWITCH_REDIRECT_URI,
			'response_type': 'code',
			'scope': 'user_read',
		})
))

@app.route('/login/twitch')
def log_in_twitch():
	# Store the URL that the user came from; redirect here when auth completes.
	next_url = flask.request.args.get('next_url')
	if next_url is not None:
		flask.session['next_url'] = next_url
	else:
		# Don't use a previous stored value.
		flask.session.pop('next_url', None)
	# Redirect the user.
	return flask.redirect(_TWITCH_OAUTH_AUTHORIZE_URL)

_TWITCH_OAUTH_ACCESS_TOKEN_URL = '%s/oauth2/token' % _TWITCH_API_URI_PREFIX
_TWITCH_AUTHENTICATED_USER_URL = '%s/user' % _TWITCH_API_URI_PREFIX

@app.route('/complete-login/twitch')
def complete_log_in_twitch():
	# Given the code, get the access token for this user.
	code = flask.request.args['code']
	params = {
		'client_id': _TWITCH_CLIENT_ID,
		'client_secret': _TWITCH_CLIENT_SECRET,
		'grant_type': 'authorization_code',
		'redirect_uri': _TWITCH_REDIRECT_URI,
		'code': code,
	}
	response = requests.post(_TWITCH_OAUTH_ACCESS_TOKEN_URL, params)
	if response.status_code != requests.codes.ok:
		flask.abort(requests.codes.server_error)
	access_token = response.json['access_token']

	# Given the access code for this user, get the user's information.
	headers = {
		'accept': 'application/vnd.twitchtv.v1+json',
		'authorization': 'OAuth %s' % access_token
	}
	response = requests.get(_TWITCH_AUTHENTICATED_USER_URL, headers=headers)
	if response.status_code != requests.codes.ok:
		flask.abort(requests.codes.server_error)
	elif 'error' in response.json:
		flask.abort(requests.codes.server_error)
	twitch_id = response.json['_id']
	name = response.json['name']
	display_name = response.json['display_name']
	logo = response.json['logo']
	
	# Get the user's identifier and update the session so logged in.
	user_id = db.twitch_user_logged_in(twitch_id, name, display_name, logo)
	return _finish_login(user_id, display_name, 'twitch')

@app.route('/logout')
def logout():
	# Remove all client data from the session.
	flask.session.pop('client', None)
	# Redirect to the URL that the user came from.
	next_url = flask.request.args.get('next_url')
	if next_url is None:
		next_url = flask.url_for('home')
	return flask.redirect(next_url)

