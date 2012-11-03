from streamhighlights import app

from collections import namedtuple
import db
import flask
import functools
import re
import requests
import urllib
from flask_openid import OpenID
from urlparse import urlparse

oid = OpenID(app)

"""Reads the client's user identifier from the session.
"""
def _read_client_id_from_session():
	user = flask.session.get('user', None)
	if user is None:
		return None
	return user['id']

"""Writes information for a Twitch user to the session.
"""
def _write_twitch_user_to_session(user_id,
		twitch_id, name, display_name, logo, access_token):
	twitch_user = {
			'id': twitch_id,
			'name': name,
			'display_name': display_name,
			'logo': logo,
			'access_token': access_token
	}
	user = {
			'id': user_id,
			'twitch': twitch_user
	}
	flask.session['user'] = user

"""Writes information for a Steam user to the session.
"""
def _write_steam_user_to_session(user_id,
		steam_id, personaname, profile_url, avatar, avatar_full):
	steam_user = {
			'id': steam_id,
			'personaname': personaname,
			'profile_url': profile_url,
			'avatar': avatar,
			'avatar_full': avatar_full
	}
	user = {
			'id': user_id,
			'steam': steam_user
	}
	flask.session['user'] = user

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
			flask.g.logged_in = False
		else:
			flask.g.logged_in = True
			flask.g.client_id = client_id

		return f(*pargs, **kwargs)
	return decorated_function

def _get_client_id():
	if flask.g.logged_in:
		return flask.g.client_id
	return None

@app.route('/')
@login_optional
def show_home():
	return flask.render_template('home.html')

def _show_user(getter, getter_arg, template_filename):
	displayed_user = None
	try:
		client_id = _get_client_id()
		displayed_user = getter(client_id, getter_arg)
	except db.DbException as e:
		# If displayed_user is None then the template will show an error message.
		# TODO: Log Exception.
		pass

	return flask.render_template(template_filename, displayed_user=displayed_user)

_STEAM_USER_TEMPLATE_FILENAME = 'steam_user.html'
_TWITCH_USER_TEMPLATE_FILENAME = 'twitch_user.html'

@app.route('/user/steam/<name>')
@login_optional
def show_steam_user_by_name(name):
	return _show_user(
			db.get_displayed_steam_user_by_name, name, _STEAM_USER_TEMPLATE_FILENAME)

@app.route('/user/steam_id/<int:steam_id>')
@login_optional
def show_steam_user_by_id(steam_id):
	return _show_user(
			db.get_displayed_steam_user_by_id, steam_id, _STEAM_USER_TEMPLATE_FILENAME)

@app.route('/user/twitch/<name>')
@login_optional
def show_twitch_user_by_name(name):
	return _show_user(
			db.get_displayed_twitch_user_by_name, name, _TWITCH_USER_TEMPLATE_FILENAME)

@app.route('/user/twitch_id/<int:twitch_id>')
@login_optional
def show_twitch_user_by_id(twitch_id):
	return _show_user(
			db.get_displayed_twitch_user_by_id, twitch_id, _TWITCH_USER_TEMPLATE_FILENAME)

@app.route('/playlist/<int:playlist_id>')
@login_optional
def show_playlist(playlist_id):
	displayed_playlist = None
	try:
		client_id = _get_client_id()
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
	except db.DbException as e:
		# If displayed_playlist is None then the template will show an error message.
		pass
	
	return flask.render_template('playlist.html', displayed_playlist=displayed_playlist)

_MATCH_HOST_REGEX = re.compile('(?:twitchtv\.com|twitch\.tv|justintv\.com|justin\.tv)$')
_GET_ARCHIVE_ID_REGEX = re.compile('/b/(?P<archive_id>\d+)$')

"""Details about a video on Twitch.
"""
TwitchVideo = namedtuple('TwitchVideo', [
		'archive_id', 'title', 'length', 'video_file_url', 'link_url'])

"""Returns a TwitchVideo given its archive identifier.
"""
def download_twitch_video_by_archive_id(archive_id):
	url = 'http://api.justin.tv/api/broadcast/by_archive/%s.json' % archive_id
	response = requests.get(url)
	if response.status_code != requests.codes.ok:
		raise ValueError

	title = response.json['title']
	length = response.json['length']
	video_file_url = response.json['video_file_url']
	link_url = response.json['link_url']
	return TwitchVideo(archive_id, title, length, video_file_url, link_url)

"""Returns a TwitchVideo given its archived URL on Twitch.
"""
def download_twitch_video_by_url(url):
	parsed_url = urlparse(url)
	if not _MATCH_HOST_REGEX.search(parsed_url.netloc):
		raise ValueError
	archive_id_match = _GET_ARCHIVE_ID_REGEX.search(parsed_url.path)
	if not archive_id_match:
		raise ValueError
	archive_id = int(archive_id_match.group('archive_id'))
	return download_twitch_video_by_archive_id(archive_id)

@app.route('/video/twitch/<int:archive_id>')
@login_optional
def show_twitch_video(archive_id):
	try:
		client_id = _get_client_id()
		displayed_video = db.get_displayed_twitch_video(client_id, archive_id)
		return flask.render_template('twitch_video.html', displayed_video=displayed_video)
	except db.DbException as e:
		# The video was not found, so go retrieve its JSON from Twitch.
		pass
	
	try:
		twitch_video = download_twitch_video_by_archive_id(archive_id)
	except Exception as e:
		# The video could not be retrieved, so display an error message.
		return flask.render_template('twitch_video.html', displayed_video=None)

	video_id = db.add_twitch_video(
			twitch_video.title,
			twitch_video.length,
			twitch_video.archive_id,
			twitch_video.video_file_url,
			twitch_video.link_url)
	displayed_video = db.DisplayedTwitchVideo(
			video_id,
			twitch_video.title,
			twitch_video.length,
			(),
			twitch_video.archive_id,
			twitch_video.video_file_url,
			twitch_video.link_url)
	return flask.render_template('twitch_video.html', displayed_video=displayed_video)


_TWITCH_CLIENT_ID = ''
_TWITCH_CLIENT_SECRET = ''
_TWITCH_API_URI_PREFIX = 'https://api.twitch.tv/kraken'

_TWITCH_REDIRECT_URI = 'https://streamhighlights.com/complete_twitch_auth'
_TWITCH_USER_READ_SCOPE = 'user_read'
_TWITCH_OAUTH_AUTHORIZE_URL = ('%s/oauth2/authorize?%s' % (
		_TWITCH_API_URI_PREFIX,
		urllib.urlencode({
			'client_id': _TWITCH_CLIENT_ID,
			'redirect_uri': _TWITCH_REDIRECT_URI,
			'response_type': 'code',
			'scope': _TWITCH_USER_READ_SCOPE,
		})
))

@app.route('/start_twitch_auth')
def start_twitch_auth():
	# TODO: Remove any user from the session.
	# Store the URL that the user came from; redirect here when auth completes.
	next_url = flask.request.args.get('next_url', None)
	if next_url is not None:
		flask.session['next_url'] = next_url
	# Redirect the user.
	return flask.redirect(_TWITCH_OAUTH_AUTHORIZE_URL)

_TWITCH_OAUTH_ACCESS_TOKEN_URL = '%s/oauth2/token' % _TWITCH_API_URI_PREFIX
_TWITCH_AUTHENTICATED_USER_URL = '%s/user' % _TWITCH_API_URI_PREFIX

@app.route('/complete_twitch_auth')
def complete_twitch_auth():
	# Given the code, get the access token for this user.
	code = request.args['code']
	params = {
			'client_id': _TWITCH_CLIENT_ID,
			'redirect_uri': _TWITCH_REDIRECT_URI,
			'client_secret': _TWITCH_CLIENT_SECRET,
			'grant_type': 'authorization_code',
			'code': code
	}
	response = requests.post(_TWITCH_OAUTH_ACCESS_TOKEN_URL, params)
	if response.status != requests.codes.ok:
		# TODO
		return
	elif _TWITCH_USER_READ_SCOPE not in response.json.get('scope', ()):
		# The client did not grant read-only access for basic information.
		# TODO
		return
	access_token = response.json['access_token']

	# Given the access code for this user, get the user's information.
	headers['accept'] = 'application/vnd.twitchtv.v1+json'
	headers['authorization'] = 'OAuth %s' % access_token
	response = requests.get(_TWITCH_AUTHENTICATED_USER_URL, headers=headers)
	if response.status != requests.codes.ok:
		# TODO
		return
	twitch_id = response.json['twitch_id']
	name = response.json['name']
	display_name = response.json['display_name']
	logo = response.json['logo']
	access_token = response.json['access_token']
	
	# Log in the Twitch user.
	user_id = db.twitch_user_logged_in(
			twitch_id, name, display_name, logo, access_token, datetime.utcnow())
	# Write the Twitch user to the session.
	_write_twitch_user_to_session(
			user_id, twitch_id, name, display_name, logo, access_token)


_STEAM_WEB_API_KEY = '52F753EAA320784E9CD999A78997B5D1'
_STEAM_OPEN_ID_URL = 'http://steamcommunity.com/openid'

@app.route('/start_steam_auth')
@oid.loginhandler
def _start_steam_auth():
	# TODO: Remove any user from the session.
	return oid.try_login(_STEAM_OPEN_ID_URL)

_GET_STEAM_ID_REGEX = re.compile('steamcommunity.com/openid/id/(?P<steam_id>.*?)$')
_STEAM_PLAYER_SUMMARY_URL = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002'

@oid.after_login
def complete_steam_auth(response):
	# Get the user's Steam identifier from the OpenID response.
	steam_id_match = _GET_STEAM_ID_REGEX.search(response.identity_url)
	if not steam_id_match:
		# TODO
		return
	steam_id = steam_id_match.group('steam_id')
	
	# Given the user's Steam ID, get the user's information.
	user_url = ('%s/?%s' % (
			_STEAM_PLAYER_SUMMARY_URL,
			urllib.urlencode({
					'key': _STEAM_WEB_API_KEY,
					'steamids': steam_id
			})
	))
	response = requests.get(user_url)
	if response.status != requests.codes.ok:
		# TODO
		return
	if ('response' not in response.json) or not response.json['response']['players']:
 		# TODO
		return
	player = response.json['response']['players'][0]
	personaname = player['personaname']
	profile_url = player.get('profileurl', None)
	avatar = player.get('avatar', None)
	avatar_full = player.get('avatarfull', None)

	# Log in the Steam user.
	user_id = db.steam_user_logged_in(
			steam_id, personaname, profile_url, avatar, avatar_full)
	# Write the Steam user to the session.
	_write_steam_user_to_session(
			user_id, steam_id, personaname, profile_url, avatar, avatar_full)


_AJAX_SUCCESS = {'success': True}
_AJAX_FAILURE = {'success': False}

def ajax_request(f):
	@functools.wraps(f)
	def decorated_function(*pargs, **kwargs):
		# Raise an exception if the session is missing the client identifier.
		client_id = _read_client_id_from_session()
		if client_id is None:
			# Return status code 401 if user is not logged in.
			flask.abort(requests.codes.unauthorized)

		try:
			flask.g.client_id = client_id
			f(*pargs, **kwargs)
			return flask.jsonify(_AJAX_SUCCESS)
		except Exception as e:
			# Any error is assumed to be from db, return as failure.
			return flask.jsonify(_AJAX_FAILURE)
	return decorated_function

@app.route('/add_playlist_bookmark', methods=['POST'])
@ajax_request
def add_playlist_bookmark():
	db.add_playlist_bookmark(
			flask.g.client_id, flask.request.form['playlist_id'], flask.request.form['bookmark_id'])

@app.route('/remove_playlist_bookmark', methods=['POST'])
@ajax_request
def remove_playlist_bookmark():
	db.remove_playlist_bookmark(
			flask.g.client_id, flask.request.form['playlist_id'], flask.request.form['bookmark_id'])

@app.route('/vote_playlist_thumb_up', methods=['POST'])
@ajax_request
def vote_playlist_thumb_up():
	db.vote_playlist_thumb_up(flask.g.client_id, flask.request.form['playlist_id'])

@app.route('/vote_playlist_thumb_down', methods=['POST'])
@ajax_request
def vote_playlist_thumb_down():
	db.vote_playlist_thumb_down(flask.g.client_id, flask.request.form['playlist_id'])

@app.route('/remove_playlist_vote', methods=['POST'])
@ajax_request
def remove_playlist_vote():
	db.remove_playlist_vote(flask.g.client_id, flask.request.form['playlist_id'])

@app.route('/remove_video_bookmark', methods=['POST'])
@ajax_request
def remove_video_bookmark():
	db.remove_video_bookmark(flask.g.client_id, flask.request.form['bookmark_id'])

@app.route('/vote_bookmark_thumb_up', methods=['POST'])
@ajax_request
def vote_bookmark_thumb_up():
	db.vote_bookmark_thumb_up(flask.g.client_id, flask.request.form['bookmark_id'])

@app.route('/vote_bookmark_thumb_down', methods=['POST'])
@ajax_request
def vote_bookmark_thumb_down():
	db.vote_bookmark_thumb_down(flask.g.client_id, flask.request.form['bookmark_id'])

@app.route('/remove_bookmark_vote', methods=['POST'])
@ajax_request
def remove_bookmark_vote():
	db.remove_bookmark_vote(flask.g.client_id, flask.request.form['bookmark_id'])

