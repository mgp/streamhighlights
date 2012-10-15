from streamhighlights import app

from datetime import datetime
import json
import requests
import unittest

import db
import views

class Foo:
	"""Utility method for creating a user."""
	def _create_user(self, name):
		user = db.User(name, self.now)
		self.session.add(user)
		self.session.commit()
		return user.id

	"""Utility method for creating a video."""
	def _create_video(self, name, length):
		video = db.Video(name, length)
		self.session.add(video)
		self.session.commit()
		return video.id

	"""Utility method for creating a bookmark."""
	def _create_bookmark(self, user_id, video_id, comment, time):
		bookmark = db.Bookmark(
				comment, time, self.now, user_id=user_id, video_id=video_id)
		self.session.add(bookmark)
		self.session.commit()
		return bookmark.id


class TestViews(unittest.TestCase, Foo):
	def setUp(self):
		unittest.TestCase.setUp(self)
		self.now = datetime(2012, 10, 15, 12, 30, 45)
		self.session = db.session
		db.create_all()

	def tearDown(self):
		unittest.TestCase.tearDown(self)
		db.drop_all()

	def _add_client_id(self, client, client_id):
		with client.session_transaction() as session:
			session['client_id'] = client_id

	"""Assert that the AJAX request succeeded.
	"""
	def _assert_ajax_success(self, response):
		self.assertEqual(requests.codes.ok, response.status_code)
		json_response = json.loads(response.data)
		self.assertTrue(json_response['success'])

	"""Assert that the AJAX request failed.
	"""
	def _assert_ajax_failure(self, response):
		self.assertEqual(requests.codes.ok, response.status_code)
		json_response = json.loads(response.data)
		self.assertFalse(json_response['success'])

	def test_add_playlist_bookmark(self):
		user_id = self._create_user('user_name')
		video_id = self._create_video('video_name', 99)
		bookmark_id = self._create_bookmark(user_id, video_id, 'comment', 33)
		playlist_id = db.create_playlist(user_id, 'playlist_name', now=self.now)

		with app.test_client() as client:
			self._add_client_id(client, user_id)
			response = client.post('/add_playlist_bookmark',
					data={'playlist_id': playlist_id, 'bookmark_id': bookmark_id})
			self._assert_ajax_success(response)

	def test_add_playlist_bookmark_bad_request(self):
		user_id = self._create_user('user_name')
		video_id = self._create_video('video_name', 99)
		bookmark_id = self._create_bookmark(user_id, video_id, 'comment', 33)
		playlist_id = db.create_playlist(user_id, 'playlist_name', now=self.now)

		# Assert that the request fails with a missing client identifier.
		with app.test_client() as client:
			response = client.post('/add_playlist_bookmark',
					data={'playlist_id': playlist_id, 'bookmark_id': bookmark_id})
			self._assert_ajax_failure(response)

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
		user_id = self._create_user('user_name')
		video_id = self._create_video('video_name', 99)
		bookmark_id = self._create_bookmark(user_id, video_id, 'comment', 33)
		playlist_id = db.create_playlist(user_id, 'playlist_name', now=self.now)
		db.add_playlist_bookmark(user_id, playlist_id, bookmark_id, now=self.now)

		with app.test_client() as client:
			self._add_client_id(client, user_id)
			response = client.post('/remove_playlist_bookmark',
					data={'playlist_id': playlist_id, 'bookmark_id': bookmark_id})
			self._assert_ajax_success(response)

	def test_remove_playlist_bookmark_bad_request(self):
		user_id = self._create_user('user_name')
		video_id = self._create_video('video_name', 99)
		bookmark_id = self._create_bookmark(user_id, video_id, 'comment', 33)
		playlist_id = db.create_playlist(user_id, 'playlist_name', now=self.now)
		db.add_playlist_bookmark(user_id, playlist_id, bookmark_id, now=self.now)

		# Assert that the request fails with a missing client identifier.
		with app.test_client() as client:
			response = client.post('/remove_playlist_bookmark',
					data={'playlist_id': playlist_id, 'bookmark_id': bookmark_id})
			self._assert_ajax_failure(response)

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
		user_id = self._create_user('user_name')
		playlist_id = db.create_playlist(user_id, 'playlist_name', now=self.now)
		client_id = self._create_user('client_name')

		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/vote_playlist_thumb_up', data={'playlist_id': playlist_id})
			self._assert_ajax_success(response)

	def test_vote_playlist_thumb_up_bad_request(self):
		user_id = self._create_user('user_name')
		playlist_id = db.create_playlist(user_id, 'playlist_name', now=self.now)
		client_id = self._create_user('client_name')

		# Assert that the request fails with a missing client identifier.
		with app.test_client() as client:
			response = client.post('/vote_playlist_thumb_up', data={'playlist_id': playlist_id})
			self._assert_ajax_failure(response)

		# Assert that the request fails with a missing playlist identifier.
		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/vote_playlist_thumb_up')
			self._assert_ajax_failure(response)

	def test_vote_playlist_thumb_down(self):
		user_id = self._create_user('user_name')
		playlist_id = db.create_playlist(user_id, 'playlist_name', now=self.now)
		client_id = self._create_user('client_name')
		db.vote_playlist_thumb_up(client_id, playlist_id)

		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/vote_playlist_thumb_down', data={'playlist_id': playlist_id})
			self._assert_ajax_success(response)

	def test_vote_playlist_thumb_down_bad_request(self):
		user_id = self._create_user('user_name')
		playlist_id = db.create_playlist(user_id, 'playlist_name', now=self.now)
		client_id = self._create_user('client_name')
		db.vote_playlist_thumb_up(client_id, playlist_id)

		# Assert that the request fails with a missing client identifier.
		with app.test_client() as client:
			response = client.post('/vote_playlist_thumb_down', data={'playlist_id': playlist_id})
			self._assert_ajax_failure(response)

		# Assert that the request fails with a missing playlist identifier.
		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/vote_playlist_thumb_down')
			self._assert_ajax_failure(response)

	def test_remove_playlist_vote(self):
		user_id = self._create_user('user_name')
		playlist_id = db.create_playlist(user_id, 'playlist_name', now=self.now)
		client_id = self._create_user('client_name')
		db.vote_playlist_thumb_up(client_id, playlist_id)

		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/remove_playlist_vote', data={'playlist_id': playlist_id})
			self._assert_ajax_success(response)

	def test_remove_playlist_vote_bad_request(self):
		user_id = self._create_user('user_name')
		playlist_id = db.create_playlist(user_id, 'playlist_name', now=self.now)
		client_id = self._create_user('client_name')
		db.vote_playlist_thumb_up(client_id, playlist_id)

		# Assert that the request fails with a missing client identifier.
		with app.test_client() as client:
			response = client.post('/remove_playlist_vote', data={'playlist_id': playlist_id})
			self._assert_ajax_failure(response)

		# Assert that the request fails with a missing playlist identifier.
		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/remove_playlist_vote')
			self._assert_ajax_failure(response)

	def test_remove_video_bookmark(self):
		user_id = self._create_user('user_name')
		video_id = self._create_video('video_name', 99)
		bookmark_id = self._create_bookmark(user_id, video_id, 'comment', 33)

		with app.test_client() as client:
			self._add_client_id(client, user_id)
			response = client.post('/remove_video_bookmark', data={'bookmark_id': bookmark_id})
			self._assert_ajax_success(response)

	def test_remove_video_bookmark_bad_request(self):
		user_id = self._create_user('user_name')
		video_id = self._create_video('video_name', 99)
		bookmark_id = self._create_bookmark(user_id, video_id, 'comment', 33)

		# Assert that the request fails with a missing client identifier.
		with app.test_client() as client:
			response = client.post('/remove_video_bookmark', data={'bookmark_id': bookmark_id})
			self._assert_ajax_failure(response)

		# Assert that the request fails with a missing bookmark identifier.
		with app.test_client() as client:
			self._add_client_id(client, user_id)
			response = client.post('/remove_video_bookmark')
			self._assert_ajax_failure(response)

	def test_vote_bookmark_thumb_up(self):
		user_id = self._create_user('user_name')
		video_id = self._create_video('video_name', 99)
		bookmark_id = self._create_bookmark(user_id, video_id, 'comment', 33)
		client_id = self._create_user('client_name')

		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/vote_bookmark_thumb_up', data={'bookmark_id': bookmark_id})
			self._assert_ajax_success(response)

	def test_vote_bookmark_thumb_up_bad_request(self):
		user_id = self._create_user('user_name')
		video_id = self._create_video('video_name', 99)
		bookmark_id = self._create_bookmark(user_id, video_id, 'comment', 33)
		client_id = self._create_user('client_name')

		# Assert that the request fails with a missing client identifier.
		with app.test_client() as client:
			response = client.post('/vote_bookmark_thumb_up', data={'bookmark_id': bookmark_id})
			self._assert_ajax_failure(response)

		# Assert that the request fails with a missing bookmark identifier.
		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/vote_bookmark_thumb_up')
			self._assert_ajax_failure(response)

	def test_vote_bookmark_thumb_down(self):
		user_id = self._create_user('user_name')
		video_id = self._create_video('video_name', 99)
		bookmark_id = self._create_bookmark(user_id, video_id, 'comment', 33)
		client_id = self._create_user('client_name')
		db.vote_bookmark_thumb_up(client_id, bookmark_id)

		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/vote_bookmark_thumb_down', data={'bookmark_id': bookmark_id})
			self._assert_ajax_success(response)

	def test_vote_bookmark_thumb_down_bad_request(self):
		user_id = self._create_user('user_name')
		video_id = self._create_video('video_name', 99)
		bookmark_id = self._create_bookmark(user_id, video_id, 'comment', 33)
		client_id = self._create_user('client_name')
		db.vote_bookmark_thumb_up(client_id, bookmark_id)

		# Assert that the request fails with a missing client identifier.
		with app.test_client() as client:
			response = client.post('/vote_bookmark_thumb_down', data={'bookmark_id': bookmark_id})
			self._assert_ajax_failure(response)

		# Assert that the request fails with a missing bookmark identifier.
		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/vote_bookmark_thumb_down')
			self._assert_ajax_failure(response)

	def test_remove_bookmark_vote(self):
		user_id = self._create_user('user_name')
		video_id = self._create_video('video_name', 99)
		bookmark_id = self._create_bookmark(user_id, video_id, 'comment', 33)
		client_id = self._create_user('client_name')
		db.vote_bookmark_thumb_up(client_id, bookmark_id)

		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/remove_bookmark_vote', data={'bookmark_id': bookmark_id})
			self._assert_ajax_success(response)

	def test_remove_bookmark_vote_bad_request(self):
		user_id = self._create_user('user_name')
		video_id = self._create_video('video_name', 99)
		bookmark_id = self._create_bookmark(user_id, video_id, 'comment', 33)
		client_id = self._create_user('client_name')
		db.vote_bookmark_thumb_up(client_id, bookmark_id)

		# Assert that the request fails with a missing client identifier.
		with app.test_client() as client:
			response = client.post('/remove_bookmark_vote', data={'bookmark_id': bookmark_id})
			self._assert_ajax_failure(response)

		# Assert that the request fails with a missing bookmark identifier.
		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/remove_bookmark_vote')
			self._assert_ajax_failure(response)


class TestRequestTwitchVideo(unittest.TestCase):
	def _get_twitch_video(self, url):
		self.url = url
		return self.twitch_video_response

	def setUp(self):
		unittest.TestCase.setUp(self)
		# Create the Response object containing the Twitch video JSON.
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
		self.url = None
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

