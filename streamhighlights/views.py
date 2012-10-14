from streamhighlights import app

import db

_AJAX_SUCCESS = {'success': True}
_AJAX_FAILURE = {'success': False}

def ajax_request(f):
	@wraps(f)
	def decorated_function(*pargs, **kwargs):
		try:
			# Raise an exception if the session is missing the client identifier.
			g.client_id = session['client_id']
			f(*pargs, **kwargs)
			return jsonify(_AJAX_SUCCESS)
		except Exception:
			return jsonify(_AJAX_FAILURE)
	return decorated_function

@app.route('/add_playlist_bookmark')
@ajax_request
def add_playlist_bookmark():
	db.add_playlist_bookmark(
			g.client_id, request.form['playlist_id'], request.form['bookmark_id'])

@app.route('/remove_playlist_bookmark')
@ajax_request
def remove_playlist_bookmark():
	db.remove_playlist_bookmark(
				g.client_id, request.form['playlist_id'], request.form['bookmark_id'])

@app.route('/vote_playlist_thumb_up')
@ajax_request
def vote_playlist_thumb_up():
	db.vote_playlist_thumb_up(g.client_id, request.form['playlist_id'])

@app.route('/vote_playlist_thumb_down')
@ajax_request
def vote_playlist_thumb_down():
	db.vote_playlist_thumb_down(g.client_id, request.form['playlist_id'])

@app.route('/remove_playlist_vote')
@ajax_request
def remove_playlist_vote():
	db.remove_playlist_vote(g.client_id, request.form['playlist_id'])

@app.route('/vote_bookmark_thumb_up')
@ajax_request
def vote_bookmark_thumb_up():
	db.vote_bookmark_thumb_up(g.client_id, request.form['bookmark_id'])

@app.route('/vote_bookmark_thumb_down')
@ajax_request
def vote_bookmark_thumb_down():
	db.vote_bookmark_thumb_down(g.client_id, request.form['bookmark_id'])

@app.route('/remove_bookmark_vote')
@ajax_request
def remove_bookmark_vote():
	db.remove_bookmark_vote(g.client_id, request.form['bookmark_id'])

