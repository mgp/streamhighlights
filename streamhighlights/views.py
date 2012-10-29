from streamhighlights import app

from collections import namedtuple
import db
import flask
import functools
import re
import requests
import urllib
from urlparse import urlparse

def login_required(f):
	@functools.wraps(f)
	def decorated_function(*pargs, **kwargs):
		client_id = flask.session.get('client_id', None)
		if client_id is None:
			# Return status code 401 if user is not logged in.
			flask.abort(requests.codes.unauthorized)

		flask.g.client_id = client_id
		return f(*pargs, **kwargs)
	return decorated_function

def login_optional(f):
	@functools.wraps(f)
	def decorated_function(*pargs, **kwargs):
		client_id = flask.session.get('client_id', None)
		if client_id is None:
			flask.g.logged_in = False
		else:
			flask.g.logged_in = True
			flask.g.client_id = client_id

		return f(*pargs, **kwargs)
	return decorated_function

@app.route('/')
@login_optional
def show_home():
	return flask.render_template('home.html')

def _show_user(getter, getter_arg, template_filename):
	displayed_user = None
	try:
		displayed_user = user_getter(flask.g.client_id, getter_arg)
	except Exception as e:
		# If displayed_user is None then the template will show an error message.
		# TODO: Log Exception.
		pass

	return flask.render_template(template_filename, displayed_user=displayed_user)

_STEAM_USER_TEMPLATE_FILENAME = 'steam_user.html'
_TWITCH_USER_TEMPLATE_FILENAME = 'twitch_user.html'

@app.route('/user/steam/<name>')
def show_steam_user_by_name(name):
	return _show_user(
			db.get_displayed_steam_user_by_name, name, _STEAM_USER_TEMPLATE_FILENAME)

@app.route('/user/steam_id/<steam_id>')
@login_optional
def show_steam_user_by_id(steam_id):
	return _show_user(
			db.get_displayed_steam_user_by_id, steam_id, _STEAM_USER_TEMPLATE_FILENAME)

@app.route('/user/twitch/<name>')
@login_optional
def show_twitch_user_by_name(name):
	return _show_user(
			db.get_displayed_twitch_user_by_name, name, _TWITCH_USER_TEMPLATE_FILENAME)

@app.route('/user/twitch_id/<twitch_id>')
@login_optional
def show_twitch_user_by_id(twitch_id):
	return _show_user(
			db.get_displayed_twitch_user_by_id, twitch_id, _TWITCH_USER_TEMPLATE_FILENAME)

@app.route('/playlist/<playlist_id>')
@login_optional
def show_playlist(playlist_id):
	displayed_playlist = None
	try:
		displayed_playlist = db.get_displayed_playlist(flask.g.client_id, playlist_id)
	except Exception as e:
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
		client_id = flask.g.client_id if flask.g.logged_in else None
		displayed_video = db.get_displayed_twitch_video(client_id, archive_id)
		return flask.render_template('twitch_video.html', displayed_video=displayed_video)
	except Exception as e:
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
_TWITCH_REDIRECT_URI = 'https://streamhighlights.com/complete_twitch_auth'
_TWITCH_USER_READ_SCOPE = 'user_read'

_TWITCH_OAUTH_AUTHORIZE_URL = ('https://api.twitch.tv/kraken/oauth2/authorize?%s' %
		urllib.urlencode({
			'client_id': _TWITCH_CLIENT_ID,
			'redirect_uri': _TWITCH_REDIRECT_URI,
			'response_type': 'code',
			'scope': _TWITCH_USER_READ_SCOPE,
		})
)

@app.route('/start_twitch_auth')
def start_twitch_auth():
	# Store the URL that the user came from; redirect here when auth completes.
	next_url = flask.request.args.get('next_url', None)
	if next_url is not None:
		flask.session['next_url'] = next_url
	# Redirect the user.
	return flask.redirect(_TWITCH_OAUTH_AUTHORIZE_URL)

_TWITCH_OAUTH_ACCESS_TOKEN_URL = 'https://api.twitch.tv/kraken/oauth2/token'
_TWITCH_CLIENT_SECRET = ''

@app.route('/complete_twitch_auth')
def complete_twitch_auth():
	code = request.args['code']
	params = {
			'client_id': _TWITCH_CLIENT_ID,
			'redirect_uri': _TWITCH_REDIRECT_URI,
			'client_secret': _TWITCH_CLIENT_SECRET,
			'grant_type': 'authorization_code',
			'code': code
	}
	response = requests.post(_TWITCH_OAUTH_ACCESS_TOKEN_URL, params)
	if _TWITCH_USER_READ_SCOPE not in response.json.get('scope', ()):
		# The client did not grant read-only access for basic information.
		# TODO
		return

	twitch_user_json = {
			'id': response.json['twitch_id'],
			'name': response.json['name'],
			'display_name': response.json['display_name'],
			'logo': response.json['logo'],
			'access_token': response.json['access_token']
	}
	session['twitch_user'] = twitch_user_json
	# TODO: db.insert_or_update_twitch_user()

def _add_twitch_api_header(headers):
	headers['accept'] = 'application/vnd.twitchtv.v1+json'

def _add_oauth_header(headers, oauth_token):
	headers['authorization'] = 'OAuth %s' % oauth_token

def _get_authenticated_twitch_user(self, ):
	authenticated_user_url = 'https://api.twitch.tv/kraken/user'
	response = requests.get(authenticated_user_url)
	status = response.json.get('status', 200)
	if status != 200:
		# There was an error; the token is likely invalid or expired.
		return None
	return response.json['name']


_AJAX_SUCCESS = {'success': True}
_AJAX_FAILURE = {'success': False}

def ajax_request(f):
	@functools.wraps(f)
	def decorated_function(*pargs, **kwargs):
		# Raise an exception if the session is missing the client identifier.
		client_id = flask.session.get('client_id')
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

