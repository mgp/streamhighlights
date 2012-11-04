from streamhighlights import app

import db
from db_test_case import DbTestCase
import flask
import json
import requests
import unittest
import views


class TestViews(DbTestCase):
	def _fake_download_twitch_video_by_archive_id(self, archive_id):
		self.assertFalse(self._returned_twitch_video)
		self._returned_twitch_video = True
		return self._twitch_video

	def _reset_twitch_video_download(self):
		self._twitch_video = None
		self._returned_twitch_video = False

	def setUp(self):
		DbTestCase.setUp(self)
		self._reset_twitch_video_download()
		# Replace the method to download a Twitch video with a stub.
		views.download_twitch_video_by_archive_id = self._fake_download_twitch_video_by_archive_id

	def tearDown(self):
		DbTestCase.tearDown(self)

	def _add_client_id(self, client, client_id):
		with client.session_transaction() as session:
			user = {
					'id': client_id
			}
			session['user'] = user

	def test_write_twitch_user_to_session(self):
		user_id = 'user_id'
		twitch_id = 'twitch_id'
		name = 'name'
		display_name = 'display_name'
		logo = 'logo'
		access_token = 'access_token'

		# Use a dictionary for the session since outside a request context.
		session = {}
		views._write_twitch_user_to_session(user_id,
				twitch_id, name, display_name, logo, access_token, session=session)
		# Assert that the user identifier is correct.
		session_user_id = views._read_client_id_from_session(session=session)
		self.assertEqual(user_id, session_user_id)
		# Assert that the Twitch user data is found, and the Steam user data is missing.
		steam_user, twitch_user = views._read_client_data_from_session(session=session)
		self.assertIsNone(steam_user)
		self.assertDictEqual({
				'id': twitch_id,
				'name': name,
				'display_name': display_name,
				'logo': logo,
				'access_token': access_token}, twitch_user)

	def test_write_steam_user_to_session(self):
		user_id = 'user_id'
		steam_id = 'steam_id'
		personaname = 'personaname'
		profile_url = 'profile_url'
		avatar = 'avatar'
		avatar_full = 'avatar_full'

		# Use a dictionary for the session since outside a request context.
		session = {}
		views._write_steam_user_to_session(user_id,
				steam_id, personaname, profile_url, avatar, avatar_full, session=session)
		# Assert that the user identifier is correct.
		session_user_id = views._read_client_id_from_session(session=session)
		self.assertEqual(user_id, session_user_id)
		# Assert that the Steam user data is found, and the Twitch user data is missing.
		steam_user, twitch_user = views._read_client_data_from_session(session=session)
		self.assertDictEqual({
				'id': steam_id,
				'personaname': personaname,
				'profile_url': profile_url,
				'avatar': avatar,
				'avatar_full': avatar_full}, steam_user)
		self.assertIsNone(twitch_user)

	def test_show_steam_user(self):
		# Create a new Steam user.
		steam_id = 456
		personaname = 'personaname'
		community_id = 'community_id'
		profile_url = 'steamcommunity.com/id/%s' % community_id
		avatar = 'avatar'
		avatar_full = 'avatar_full'
		user_id = db.steam_user_logged_in(
				steam_id, personaname, profile_url, avatar, avatar_full, self.now)

		# Get the user by its Steam identifier.
		with app.test_client() as client:
			response = client.get('/user/steam_id/%s' % steam_id)
			self.assertEqual(requests.codes.ok, response.status_code)

		# Get the user by its Steam name.
		with app.test_client() as client:
			response = client.get('/user/steam/%s' % community_id)
			self.assertEqual(requests.codes.ok, response.status_code)

	def test_show_missing_steam_user(self):
		missing_steam_id = 456
		missing_community_id = 'missing_community_id'

		# Get the missing user by its Steam identifier.
		with app.test_client() as client:
			response = client.get('/user/steam_id/%s' % missing_steam_id)
			self.assertEqual(requests.codes.ok, response.status_code)

		# Get the missing user by its Steam name.
		with app.test_client() as client:
			response = client.get('/user/steam/%s' % missing_community_id)
			self.assertEqual(requests.codes.ok, response.status_code)

	def test_show_twitch_user(self):
		# Create a new Twitch user.
		twitch_id = 123
		name = 'name'
		display_name = 'display_name'
		logo = 'logo_url'
		access_token = 'access_token'
		user_id = db.twitch_user_logged_in(
				twitch_id, name, display_name, logo, access_token, self.now)

		# Get the user by its Twitch identifier.
		with app.test_client() as client:
			response = client.get('/user/twitch_id/%s' % twitch_id)
			self.assertEqual(requests.codes.ok, response.status_code)

		# Get the user by its Twitch name.
		with app.test_client() as client:
			response = client.get('/user/twitch/%s' % name)
			self.assertEqual(requests.codes.ok, response.status_code)

	def test_show_missing_twitch_user(self):
		missing_twitch_id = 123
		missing_name = 'missing_name'

		# Get the missing user by its Twitch identifier.
		with app.test_client() as client:
			response = client.get('/user/twitch_id/%s' % missing_twitch_id)
			self.assertEqual(requests.codes.ok, response.status_code)

		# Get the missing user by its Twitch name.
		with app.test_client() as client:
			response = client.get('/user/twitch/%s' % missing_name)
			self.assertEqual(requests.codes.ok, response.status_code)

	def test_show_playlist(self):
		user_steam_id, user_id = self._create_steam_user('user_name')
		video_id = db.add_twitch_video(
				'video_name', 99, 'archive_id', 'video_file_url', 'link_url')
		bookmark_id = db.add_video_bookmark(user_id, video_id, 'comment', 33)
		playlist_id = db.create_playlist(user_id, 'playlist_name', now=self.now)
		db.add_playlist_bookmark(user_id, playlist_id, bookmark_id, now=self.now)

		# Get the playlist.
		with app.test_client() as client:
			response = client.get('/playlist/%s' % playlist_id)
			self.assertEqual(requests.codes.ok, response.status_code)

	def test_show_missing_playlist(self):
		missing_playlist_id = 789

		# Get the missing playlist.
		with app.test_client() as client:
			response = client.get('/playlist/%s' % missing_playlist_id)
			self.assertEqual(requests.codes.ok, response.status_code)

	"""Assert that the AJAX request succeeded.
	"""
	def _assert_ajax_success(self, response):
		self.assertEqual(requests.codes.ok, response.status_code)
		json_response = json.loads(response.data)
		self.assertTrue(json_response['success'])

	"""Assert that the AJAX request failed because the user was not logged in.
	"""
	def _assert_not_authorized(self, response):
		self.assertEqual(requests.codes.unauthorized, response.status_code)

	"""Assert that the AJAX request failed.
	"""
	def _assert_ajax_failure(self, response):
		self.assertEqual(requests.codes.ok, response.status_code)
		json_response = json.loads(response.data)
		self.assertFalse(json_response['success'])

	def test_add_playlist_bookmark(self):
		user_steam_id, user_id = self._create_steam_user('user_name')
		video_id = db.add_twitch_video(
				'video_name', 99, 'archive_id', 'video_file_url', 'link_url')
		bookmark_id = db.add_video_bookmark(user_id, video_id, 'comment', 33)
		playlist_id = db.create_playlist(user_id, 'playlist_name', now=self.now)

		with app.test_client() as client:
			self._add_client_id(client, user_id)
			response = client.post('/add_playlist_bookmark',
					data={'playlist_id': playlist_id, 'bookmark_id': bookmark_id})
			self._assert_ajax_success(response)

	def test_add_playlist_bookmark_bad_request(self):
		user_steam_id, user_id = self._create_steam_user('user_name')
		video_id = db.add_twitch_video(
				'video_name', 99, 'archive_id', 'video_file_url', 'link_url')
		bookmark_id = db.add_video_bookmark(user_id, video_id, 'comment', 33)
		playlist_id = db.create_playlist(user_id, 'playlist_name', now=self.now)

		# Assert that the request fails with a missing client identifier.
		with app.test_client() as client:
			response = client.post('/add_playlist_bookmark',
					data={'playlist_id': playlist_id, 'bookmark_id': bookmark_id})
			self._assert_not_authorized(response)

		# Assert that the request fails with a missing playlist identifier.
		with app.test_client() as client:
			self._add_client_id(client, user_id)
			response = client.post('/add_playlist_bookmark', data={'bookmark_id': bookmark_id})
			self._assert_ajax_failure(response)

		# Assert that the request fails with a missing bookmark identifier.
		with app.test_client() as client:
			self._add_client_id(client, user_id)
			response = client.post('/add_playlist_bookmark', data={'playlist_id': playlist_id})
			self._assert_ajax_failure(response)

	def test_remove_playlist_bookmark(self):
		user_steam_id, user_id = self._create_steam_user('user_name')
		video_id = db.add_twitch_video(
				'video_name', 99, 'archive_id', 'video_file_url', 'link_url')
		bookmark_id = db.add_video_bookmark(user_id, video_id, 'comment', 33)
		playlist_id = db.create_playlist(user_id, 'playlist_name', now=self.now)
		db.add_playlist_bookmark(user_id, playlist_id, bookmark_id, now=self.now)

		with app.test_client() as client:
			self._add_client_id(client, user_id)
			response = client.post('/remove_playlist_bookmark',
					data={'playlist_id': playlist_id, 'bookmark_id': bookmark_id})
			self._assert_ajax_success(response)

	def test_remove_playlist_bookmark_bad_request(self):
		user_steam_id, user_id = self._create_steam_user('user_name')
		video_id = db.add_twitch_video(
				'video_name', 99, 'archive_id', 'video_file_url', 'link_url')
		bookmark_id = db.add_video_bookmark(user_id, video_id, 'comment', 33)
		playlist_id = db.create_playlist(user_id, 'playlist_name', now=self.now)
		db.add_playlist_bookmark(user_id, playlist_id, bookmark_id, now=self.now)

		# Assert that the request fails with a missing client identifier.
		with app.test_client() as client:
			response = client.post('/remove_playlist_bookmark',
					data={'playlist_id': playlist_id, 'bookmark_id': bookmark_id})
			self._assert_not_authorized(response)

		# Assert that the request fails with a missing playlist identifier.
		with app.test_client() as client:
			self._add_client_id(client, user_id)
			response = client.post('/remove_playlist_bookmark', data={'bookmark_id': bookmark_id})
			self._assert_ajax_failure(response)

		# Assert that the request fails with a missing bookmark identifier.
		with app.test_client() as client:
			self._add_client_id(client, user_id)
			response = client.post('/remove_playlist_bookmark', data={'playlist_id': playlist_id})
			self._assert_ajax_failure(response)

	def test_vote_playlist_thumb_up(self):
		user_steam_id, user_id = self._create_steam_user('user_name')
		playlist_id = db.create_playlist(user_id, 'playlist_name', now=self.now)
		client_steam_id, client_id = self._create_steam_user('client_name')

		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/vote_playlist_thumb_up', data={'playlist_id': playlist_id})
			self._assert_ajax_success(response)

	def test_vote_playlist_thumb_up_bad_request(self):
		user_steam_id, user_id = self._create_steam_user('user_name')
		playlist_id = db.create_playlist(user_id, 'playlist_name', now=self.now)
		client_steam_id, client_id = self._create_steam_user('client_name')

		# Assert that the request fails with a missing client identifier.
		with app.test_client() as client:
			response = client.post('/vote_playlist_thumb_up', data={'playlist_id': playlist_id})
			self._assert_not_authorized(response)

		# Assert that the request fails with a missing playlist identifier.
		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/vote_playlist_thumb_up')
			self._assert_ajax_failure(response)

	def test_vote_playlist_thumb_down(self):
		user_steam_id, user_id = self._create_steam_user('user_name')
		playlist_id = db.create_playlist(user_id, 'playlist_name', now=self.now)
		client_steam_id, client_id = self._create_steam_user('client_name')
		db.vote_playlist_thumb_up(client_id, playlist_id)

		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/vote_playlist_thumb_down', data={'playlist_id': playlist_id})
			self._assert_ajax_success(response)

	def test_vote_playlist_thumb_down_bad_request(self):
		user_steam_id, user_id = self._create_steam_user('user_name')
		playlist_id = db.create_playlist(user_id, 'playlist_name', now=self.now)
		client_steam_id, client_id = self._create_steam_user('client_name')
		db.vote_playlist_thumb_up(client_id, playlist_id)

		# Assert that the request fails with a missing client identifier.
		with app.test_client() as client:
			response = client.post('/vote_playlist_thumb_down', data={'playlist_id': playlist_id})
			self._assert_not_authorized(response)

		# Assert that the request fails with a missing playlist identifier.
		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/vote_playlist_thumb_down')
			self._assert_ajax_failure(response)

	def test_remove_playlist_vote(self):
		user_steam_id, user_id = self._create_steam_user('user_name')
		playlist_id = db.create_playlist(user_id, 'playlist_name', now=self.now)
		client_steam_id, client_id = self._create_steam_user('client_name')
		db.vote_playlist_thumb_up(client_id, playlist_id)

		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/remove_playlist_vote', data={'playlist_id': playlist_id})
			self._assert_ajax_success(response)

	def test_remove_playlist_vote_bad_request(self):
		user_steam_id, user_id = self._create_steam_user('user_name')
		playlist_id = db.create_playlist(user_id, 'playlist_name', now=self.now)
		client_steam_id, client_id = self._create_steam_user('client_name')
		db.vote_playlist_thumb_up(client_id, playlist_id)

		# Assert that the request fails with a missing client identifier.
		with app.test_client() as client:
			response = client.post('/remove_playlist_vote', data={'playlist_id': playlist_id})
			self._assert_not_authorized(response)

		# Assert that the request fails with a missing playlist identifier.
		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/remove_playlist_vote')
			self._assert_ajax_failure(response)

	def test_remove_video_bookmark(self):
		user_steam_id, user_id = self._create_steam_user('user_name')
		video_id = db.add_twitch_video(
				'video_name', 99, 'archive_id', 'video_file_url', 'link_url')
		bookmark_id = db.add_video_bookmark(user_id, video_id, 'comment', 33)

		with app.test_client() as client:
			self._add_client_id(client, user_id)
			response = client.post('/remove_video_bookmark', data={'bookmark_id': bookmark_id})
			self._assert_ajax_success(response)

	def test_remove_video_bookmark_bad_request(self):
		user_steam_id, user_id = self._create_steam_user('user_name')
		video_id = db.add_twitch_video(
				'video_name', 99, 'archive_id', 'video_file_url', 'link_url')
		bookmark_id = db.add_video_bookmark(user_id, video_id, 'comment', 33)

		# Assert that the request fails with a missing client identifier.
		with app.test_client() as client:
			response = client.post('/remove_video_bookmark', data={'bookmark_id': bookmark_id})
			self._assert_not_authorized(response)

		# Assert that the request fails with a missing bookmark identifier.
		with app.test_client() as client:
			self._add_client_id(client, user_id)
			response = client.post('/remove_video_bookmark')
			self._assert_ajax_failure(response)

	def test_vote_bookmark_thumb_up(self):
		user_steam_id, user_id = self._create_steam_user('user_name')
		video_id = db.add_twitch_video(
				'video_name', 99, 'archive_id', 'video_file_url', 'link_url')
		bookmark_id = db.add_video_bookmark(user_id, video_id, 'comment', 33)
		client_steam_id, client_id = self._create_steam_user('client_name')

		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/vote_bookmark_thumb_up', data={'bookmark_id': bookmark_id})
			self._assert_ajax_success(response)

	def test_vote_bookmark_thumb_up_bad_request(self):
		user_steam_id, user_id = self._create_steam_user('user_name')
		video_id = db.add_twitch_video(
				'video_name', 99, 'archive_id', 'video_file_url', 'link_url')
		bookmark_id = db.add_video_bookmark(user_id, video_id, 'comment', 33)
		client_steam_id, client_id = self._create_steam_user('client_name')

		# Assert that the request fails with a missing client identifier.
		with app.test_client() as client:
			response = client.post('/vote_bookmark_thumb_up', data={'bookmark_id': bookmark_id})
			self._assert_not_authorized(response)

		# Assert that the request fails with a missing bookmark identifier.
		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/vote_bookmark_thumb_up')
			self._assert_ajax_failure(response)

	def test_vote_bookmark_thumb_down(self):
		user_steam_id, user_id = self._create_steam_user('user_name')
		video_id = db.add_twitch_video(
				'video_name', 99, 'archive_id', 'video_file_url', 'link_url')
		bookmark_id = db.add_video_bookmark(user_id, video_id, 'comment', 33)
		client_steam_id, client_id = self._create_steam_user('client_name')
		db.vote_bookmark_thumb_up(client_id, bookmark_id)

		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/vote_bookmark_thumb_down', data={'bookmark_id': bookmark_id})
			self._assert_ajax_success(response)

	def test_vote_bookmark_thumb_down_bad_request(self):
		user_steam_id, user_id = self._create_steam_user('user_name')
		video_id = db.add_twitch_video(
				'video_name', 99, 'archive_id', 'video_file_url', 'link_url')
		bookmark_id = db.add_video_bookmark(user_id, video_id, 'comment', 33)
		client_steam_id, client_id = self._create_steam_user('client_name')
		db.vote_bookmark_thumb_up(client_id, bookmark_id)

		# Assert that the request fails with a missing client identifier.
		with app.test_client() as client:
			response = client.post('/vote_bookmark_thumb_down', data={'bookmark_id': bookmark_id})
			self._assert_not_authorized(response)

		# Assert that the request fails with a missing bookmark identifier.
		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/vote_bookmark_thumb_down')
			self._assert_ajax_failure(response)

	def test_remove_bookmark_vote(self):
		user_steam_id, user_id = self._create_steam_user('user_name')
		video_id = db.add_twitch_video(
				'video_name', 99, 'archive_id', 'video_file_url', 'link_url')
		bookmark_id = db.add_video_bookmark(user_id, video_id, 'comment', 33)
		client_steam_id, client_id = self._create_steam_user('client_name')
		db.vote_bookmark_thumb_up(client_id, bookmark_id)

		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/remove_bookmark_vote', data={'bookmark_id': bookmark_id})
			self._assert_ajax_success(response)

	def test_remove_bookmark_vote_bad_request(self):
		user_steam_id, user_id = self._create_steam_user('user_name')
		video_id = db.add_twitch_video(
				'video_name', 99, 'archive_id', 'video_file_url', 'link_url')
		bookmark_id = db.add_video_bookmark(user_id, video_id, 'comment', 33)
		client_steam_id, client_id = self._create_steam_user('client_name')
		db.vote_bookmark_thumb_up(client_id, bookmark_id)

		# Assert that the request fails with a missing client identifier.
		with app.test_client() as client:
			response = client.post('/remove_bookmark_vote', data={'bookmark_id': bookmark_id})
			self._assert_not_authorized(response)

		# Assert that the request fails with a missing bookmark identifier.
		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/remove_bookmark_vote')
			self._assert_ajax_failure(response)

	def test_show_twitch_video(self):
		client_steam_id, client_id = self._create_steam_user('client_name')
		self._twitch_video = views.TwitchVideo(
				456,
				'title_value',
				33,
				'video_file_url_value',
				'link_url_value')
		with app.test_client() as client:
			# Request the Twitch video.
			self._add_client_id(client, client_id)
			response = client.get('/video/twitch/%s' % self._twitch_video.archive_id)
			# The video should have been returned and added to the database.
			self.assertTrue(self._returned_twitch_video)
			displayed_twitch_video = db.get_displayed_twitch_video(
					client_id, self._twitch_video.archive_id)
			self._assert_displayed_twitch_video(displayed_twitch_video,
					self._twitch_video.title,
					self._twitch_video.length,
					self._twitch_video.archive_id,
					self._twitch_video.video_file_url,
					self._twitch_video.link_url)

	def test_show_known_twitch_video(self):
		client_steam_id, client_id = self._create_steam_user('client_name')
		archive_id = 456
		self._twitch_video = views.TwitchVideo(
				archive_id,
				'title_value',
				33,
				'video_file_url_value',
				'link_url_value')
		with app.test_client() as client:
			# Request the Twitch video, putting it in the database.
			self._add_client_id(client, client_id)
			response = client.get('/video/twitch/%s' % archive_id)

		self._reset_twitch_video_download()
		with app.test_client() as client:
			# Request the Twitch video again.
			self._add_client_id(client, client_id)
			response = client.get('/video/twitch/%s' % archive_id)
		# Assert that only read from the database.
		self.assertFalse(self._returned_twitch_video)

	def test_start_twitch_auth(self):
		# Assert that a redirect is issued without a next_url parameter.
		with app.test_client() as client:
			response = client.get('/start_twitch_auth')
			self.assertEqual(requests.codes.found, response.status_code)
			self.assertEqual(views._TWITCH_OAUTH_AUTHORIZE_URL, response.headers['location'])
			self.assertNotIn('next_url', flask.session)

		# Assert that a redirect is issued with a next_url parameter.
		next_url = 'http://www.next-url.com'
		with app.test_client() as client:
			with client.session_transaction() as session:
				session['next_url'] = next_url
			response = client.get('/start_twitch_auth')
			self.assertEqual(requests.codes.found, response.status_code)
			self.assertEqual(views._TWITCH_OAUTH_AUTHORIZE_URL, response.headers['location'])
			# Assert that the next_url parameter was stored in the session.
			self.assertEqual(next_url, flask.session['next_url'])

	def _assert_get_steam_id_regex_success(self, url, steam_id):
		steam_id_match = views._GET_STEAM_ID_REGEX.search(url)
		self.assertIsNotNone(steam_id_match)
		self.assertEqual(steam_id, int(steam_id_match.group('steam_id')))

	def _assert_get_steam_id_regex_failure(self, url):
		self.assertFalse(views._GET_STEAM_ID_REGEX.search(url))

	def test_get_steam_id_regex_success(self):
		self._assert_get_steam_id_regex_success(
				'http://steamcommunity.com/openid/id/123', 123)
	
	def test_get_steam_id_regex_failure(self):
		self._assert_get_steam_id_regex_failure(
				'http://foo.steamcommunity.com/openid/id/123')
		self._assert_get_steam_id_regex_failure(
				'foo://steamcommunity.com/openid/id/123')
		self._assert_get_steam_id_regex_failure('http://steamcommunity.com/openid/id')
		self._assert_get_steam_id_regex_failure('http://steamcommunity.com/openid/id/')


def _get_response(status_code, body):
	response = requests.models.Response()
	response.status_code = status_code
	if body:
		response._content = json.dumps(body)
	return response	

class TestCompleteTwitchAuth(DbTestCase):
	def _get_access_token(self, url, params={}):
		self.access_token_url = url
		self.access_token_params = params
		return self.access_token_response
	
	def _get_user_data(self, url, headers={}):
		self.user_data_url = url
		self.user_data_headers = headers
		return self.user_data_response
	
	def _set_access_token_response(self, status_code, body):
		self.access_token_response = _get_response(status_code, body)
	
	def _set_user_data_response(self, status_code, body):
		self.user_data_response = _get_response(status_code, body)

	def setUp(self):
		DbTestCase.setUp(self)
		self.code = 1234

		self.access_token_url = None
		self.access_token_params = None
		self.access_token_response = None

		self.user_data_url = None
		self.user_data_headers = None
		self.user_data_response = None

		# Replace the getter to return whatever response is created.
		views.requests.post = self._get_access_token
		views.requests.get = self._get_user_data
	
	def tearDown(self):
		# Reset the getter.
		views.requests.get = requests.get
		views.requests.post = requests.post
		DbTestCase.tearDown(self)

	def test_get_access_token_bad_response(self):
		with app.test_client() as client:
			self._set_access_token_response(requests.codes.server_error, None)
			client.get('/complete_twitch_auth?code=%s' % self.code)

			# Assert that a request for the access token was made.
			self.assertIsNotNone(self.access_token_url)
			# Assert that no request for the user was made.
			self.assertIsNone(self.user_data_url)

	def test_get_access_token_missing_scope(self):
		with app.test_client() as client:
			json_body = {
					'scope': []
			}
			self._set_access_token_response(requests.codes.ok, json_body)
			client.get('/complete_twitch_auth?code=%s' % self.code)

			# Assert that a request for the access token was made.
			self.assertIsNotNone(self.access_token_url)
			# Assert that no request for the user was made.
			self.assertIsNone(self.user_data_url)
	
	def test_get_user_data_bad_response(self):
		with app.test_client() as client:
			json_body = {
					'scope': [views._TWITCH_USER_READ_SCOPE],
					'access_token': 'access_token'
			}
			self._set_access_token_response(requests.codes.ok, json_body)
			self._set_user_data_response(requests.codes.server_error, None)
			client.get('/complete_twitch_auth?code=%s' % self.code)

			# Assert that a request for the access token was made.
			self.assertIsNotNone(self.access_token_url)
			# Assert that no request for the user was made.
			self.assertIsNotNone(self.user_data_url)
	
	def test_get_user_data_missing_user(self):
		with app.test_client() as client:
			json_body = {
					'scope': [views._TWITCH_USER_READ_SCOPE],
					'access_token': 'access_token'
			}
			self._set_access_token_response(requests.codes.ok, json_body)
			json_body = {
					'error': 'Not Found'
			}
			self._set_user_data_response(requests.codes.server_error, json_body)
			client.get('/complete_twitch_auth?code=%s' % self.code)

			# Assert that a request for the access token was made.
			self.assertIsNotNone(self.access_token_url)
			# Assert that no request for the user was made.
			self.assertIsNotNone(self.user_data_url)
		
	def test_complete_twitch_auth(self):
		access_token = 'access_token'
		twitch_id = 123
		name = 'name'
		display_name = 'display_name'
		logo = 'logo_url'

		with app.test_client() as client:
			json_body = {
					'scope': [views._TWITCH_USER_READ_SCOPE],
					'access_token': access_token
			}
			self._set_access_token_response(requests.codes.ok, json_body)
			json_body = {
					'twitch_id': twitch_id,
					'name': name,
					'display_name': display_name,
					'logo': logo
			}
			self._set_user_data_response(requests.codes.ok, json_body)
			client.get('/complete_twitch_auth?code=%s' % self.code)

			# Assert that a request for the access token was made.
			self.assertIsNotNone(self.access_token_url)
			# Assert that no request for the user was made.
			self.assertIsNotNone(self.user_data_url)
		
			# Assert that the user is logged in.
			session_user_id = views._read_client_id_from_session()
			expected_user_id = 1
			self.assertEqual(expected_user_id, session_user_id)
			# Assert that the Twitch user data is found, and the Steam user data is missing.
			steam_user, twitch_user = views._read_client_data_from_session()
			self.assertIsNone(steam_user)
			self.assertDictEqual({
					'id': twitch_id,
					'name': name,
					'display_name': display_name,
					'logo': logo,
					'access_token': access_token}, twitch_user)

			# Assert that the user was created.
			expected_link_url = 'http://www.twitch.tv/%s' % name
			for displayed_twitch_user in (
					db.get_displayed_twitch_user_by_id(None, twitch_id),
					db.get_displayed_twitch_user_by_name(None, name)):
				self._assert_displayed_twitch_user(displayed_twitch_user, expected_user_id,
						display_name, twitch_id, expected_link_url, image_url_large=logo)


class FakeOpenIdResponse:
	def __init__(self, identity_url):
		self.identity_url = identity_url

class TestCompleteSteamAuth(DbTestCase):
	def _get_user_summary(self, url):
		self.url = url
		return self.user_summary_response

	def _set_user_summary_response(self, status_code, body):
		self.user_summary_response = _get_response(status_code, body)

	def setUp(self):
		DbTestCase.setUp(self)
		# Replace the getter to return whatever response is created.
		self.url = None
		self.user_summary_response = None
		views.requests.get = self._get_user_summary
	
	def tearDown(self):
		# Reset the getter.
		views.requests.get = requests.get
		DbTestCase.tearDown(self)

	def test_complete_steam_auth_invalid_steam_id(self):
		# Return an OpenID response with no Steam identifier.
		open_id_response = FakeOpenIdResponse('http://steamcommunity.com/openid/id/')
		views.complete_steam_auth(open_id_response)

		# Assert that no request was made.
		self.assertIsNone(self.url)
	
	def test_complete_steam_auth_bad_response(self):
		# Return an OpenID response with a HTTP status codes that is not 200.
		self._set_user_summary_response(requests.codes.server_error, None)
		open_id_response = FakeOpenIdResponse('http://steamcommunity.com/openid/id/123')
		views.complete_steam_auth(open_id_response)

		# Assert that no request was made.
		self.assertIsNotNone(self.url)
	
	def test_complete_steam_auth_missing_user(self):
		# Return an OpenID response with no Steam user data.
		json_body = {
				'response': {
						'players': []
				}
		}
		self._set_user_summary_response(requests.codes.ok, json_body)
		open_id_response = FakeOpenIdResponse('http://steamcommunity.com/openid/id/123')
		views.complete_steam_auth(open_id_response)

		# Assert that no request was made.
		self.assertIsNotNone(self.url)
	
	def test_complete_steam_auth(self):
		# Return an OpenID response with Steam user data.
		steam_id = 123
		personaname = 'personaname1'
		community_id = 'community_id'
		profile_url = 'steamcommunity.com/id/%s' % community_id
		avatar = 'avatar1'
		avatar_full = 'avatar_full1'
		json_body = {
				'response': {
						'players': [{
								'personaname': personaname,
								'profileurl': profile_url,
								'avatar': avatar,
								'avatarfull': avatar_full
						}]
				}
		}
		self._set_user_summary_response(requests.codes.ok, json_body)
		open_id_response = FakeOpenIdResponse('http://steamcommunity.com/openid/id/%s' % steam_id)
		session = {}
		views.complete_steam_auth(open_id_response, session)

		# Assert that a request was made.
		self.assertIsNotNone(self.url)

		# Assert that the user is logged in.
		session_user_id = views._read_client_id_from_session(session=session)
		expected_user_id = 1
		self.assertEqual(expected_user_id, session_user_id)
		# Assert that the Twitch user data is found, and the Steam user data is missing.
		steam_user, twitch_user = views._read_client_data_from_session(session=session)
		self.assertDictEqual({
				'id': steam_id,
				'personaname': personaname,
				'profile_url': profile_url,
				'avatar': avatar,
				'avatar_full': avatar_full}, steam_user)
		self.assertIsNone(twitch_user)

		# Assert that the user was created.
		for displayed_steam_user in (
				db.get_displayed_steam_user_by_id(None, steam_id),
				db.get_displayed_steam_user_by_name(None, community_id)):
			self._assert_displayed_steam_user(displayed_steam_user,
					expected_user_id, personaname, steam_id, profile_url,
					image_url_small=avatar, image_url_large=avatar_full)


class TestRequestTwitchVideo(unittest.TestCase):
	def _get_twitch_video(self, url):
		self.url = url
		return self.twitch_video_response

	def setUp(self):
		unittest.TestCase.setUp(self)
		# Create the Response object containing the Twitch video JSON.
		self.url = None
		self.twitch_video_json = {
				'title': 'title_value',
				'length': 33,
				'video_file_url': 'video_file_url_value',
				'link_url': 'link_url_value'
		}
		self.twitch_video_response = requests.models.Response()
		self.twitch_video_response.status_code = requests.codes.ok
		self.twitch_video_response._content = json.dumps(self.twitch_video_json)
		# Replace the getter to return this JSON.
		views.requests.get = self._get_twitch_video
	
	def tearDown(self):
		# Reset the getter.
		views.requests.get = requests.get
		unittest.TestCase.tearDown(self)

	def _assert_match_host_regex_success(self, url):
		self.assertTrue(views._MATCH_HOST_REGEX.search(url))

	def _assert_match_host_regex_failure(self, url):
		self.assertFalse(views._MATCH_HOST_REGEX.search(url))

	def test_match_host_regex_success(self):
		self._assert_match_host_regex_success('twitch.tv')
		self._assert_match_host_regex_success('www.twitch.tv')
		self._assert_match_host_regex_success('twitchtv.com')
		self._assert_match_host_regex_success('www.twitchtv.com')
		self._assert_match_host_regex_success('justin.tv')
		self._assert_match_host_regex_success('www.justin.tv')
		self._assert_match_host_regex_success('justintv.com')
		self._assert_match_host_regex_success('www.justintv.com')

	def test_match_host_regex_failure(self):
		self._assert_match_host_regex_failure('foo.com')
		self._assert_match_host_regex_failure('twitch')
		self._assert_match_host_regex_failure('twitch.tv.com')
		self._assert_match_host_regex_failure('justin')
		self._assert_match_host_regex_failure('justin.tv.com')

	def _assert_get_archive_id_regex_success(self, url, archive_id):
		archive_id_match = views._GET_ARCHIVE_ID_REGEX.search(url)
		self.assertIsNotNone(archive_id_match)
		self.assertEqual(archive_id, int(archive_id_match.group('archive_id')))

	def _assert_get_archive_id_regex_failure(self, url):
		self.assertFalse(views._GET_ARCHIVE_ID_REGEX.search(url))

	def test_get_archive_id_regex_success(self):
		self._assert_get_archive_id_regex_success('/b/123', 123)
		self._assert_get_archive_id_regex_success('/foo/b/456', 456)
	
	def test_get_archive_id_regex_failure(self):
		self._assert_get_archive_id_regex_failure('/123')
		self._assert_get_archive_id_regex_failure('/x/123')
		self._assert_get_archive_id_regex_failure('/b')
		self._assert_get_archive_id_regex_failure('/b/')
		self._assert_get_archive_id_regex_failure('/b/foo')
		self._assert_get_archive_id_regex_failure('/b/123/456')

	def _assert_twitch_video(self, archive_id, twitch_video):
		# Assert that the URL requested was correct.
		self.assertEqual(
				'http://api.justin.tv/api/broadcast/by_archive/%s.json' % archive_id,
				self.url)
		# Assert that the TwitchVideo returned is correct.
		self.assertIsNotNone(twitch_video)
		self.assertEqual(archive_id, twitch_video.archive_id)
		self.assertEqual(self.twitch_video_json['title'], twitch_video.title)
		self.assertEqual(self.twitch_video_json['length'], twitch_video.length)
		self.assertEqual(
				self.twitch_video_json['video_file_url'], twitch_video.video_file_url)
		self.assertEqual(self.twitch_video_json['link_url'], twitch_video.link_url)

	def test_download_twitch_video_by_archive_id(self):
		archive_id = 123
		twitch_video = views.download_twitch_video_by_archive_id(123)
		self._assert_twitch_video(archive_id, twitch_video)

	def test_download_twitch_video_by_url(self):
		archive_id = 123
		url = 'http://www.twitch.tv/channel_name/b/%s' % archive_id
		twitch_video = views.download_twitch_video_by_url(url)
		self._assert_twitch_video(archive_id, twitch_video)

