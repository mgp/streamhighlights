from streamhighlights import app

import db
import flask
import functools

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

