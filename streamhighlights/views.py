from streamhighlights import app

from collections import namedtuple
import db
import flask
import functools
import re
import requests
from urlparse import urlparse

_AJAX_SUCCESS = {'success': True}
_AJAX_FAILURE = {'success': False}

def ajax_request(f):
	@functools.wraps(f)
	def decorated_function(*pargs, **kwargs):
		try:
			# Raise an exception if the session is missing the client identifier.
			flask.g.client_id = flask.session['client_id']
			f(*pargs, **kwargs)
			return flask.jsonify(_AJAX_SUCCESS)
		except Exception as e:
			return flask.jsonify(_AJAX_FAILURE)
	return decorated_function

@app.route('/')
def show_home():
	return flask.render_template('home.html')

@app.route('/user/steam/<user_id>')
def show_steam_user(user_id):
	displayed_user = None
	try:
		displayed_user = db.get_displayed_steam_user(flask.g.client_id, user_id)
	except Exception as e:
		# If displayed_user is None then the template will show an error message.
		pass

	return flask.render_template('steam_user.html', displayed_user=displayed_user)

@app.route('/user/twitch/<user_id>')
def show_twitch_user(user_id):
	displayed_user = None
	try:
		displayed_user = db.get_displayed_twitch_user(flask.g.client_id, user_id)
	except Exception as e:
		# If displayed_user is None then the template will show an error message.
		pass
	
	return flask.render_template('twitch_user.html', displayed_user=displayed_user)

@app.route('/playlist/<playlist_id>')
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

@app.route('/video/twitch/<video_id>')
def show_twitch_video(video_id):
	try:
		displayed_video = get_displayed_video(video_id)
		return flask.render_template('twitch_video.html', displayed_video=displayed_video)
	except Exception as e:
		# The video was not found, so go retrieve its JSON from Twitch.
		pass
	
	try:
		twitch_video = download_twitch_video_by_archive_id(video_id)
	except Exception as e:
		# The video could not be retrieved, so display an error message.
		return flask.render_template('twitch_video.html', displayed_video=None)

	video_id = db.add_twitch_video(
			twitch_video.archive_id,
			twitch_video.title,
			twitch_video.length,
			twitch_video.video_file_url,
			twitch_video.link_url)
	# TODO: return video_file_url, link_url
	displayed_video = db.DisplayedVideo(
			video_id, twitch_video.title, twitch_video.length, ())
	return flask.render_template('twitch_video.html', displayed_video=displayed_video)

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

