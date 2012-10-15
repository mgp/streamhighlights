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
	pass

@app.route('/user/<user_id>')
def show_user(user_id):
	pass

@app.route('/playlist/<playlist_id>')
def show_playlist(playlist_id):
	pass

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

@app.route('/video/twitchtv/<video_id>')
def show_twitchtv_video(video_id):
	try:
		displayed_video = get_displayed_video(video_id)
		return render_template('video.html')
	except Exception as e:
		pass

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

