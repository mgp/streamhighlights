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
		client_id = self._create_user('user_name')
		video_id = self._create_video('video_name', 99)
		bookmark_id = self._create_bookmark(client_id, video_id, 'comment', 33)
		playlist_id = db.create_playlist(client_id, 'playlist_name', now=self.now)

		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/add_playlist_bookmark',
					data={'playlist_id': playlist_id, 'bookmark_id': bookmark_id})
			self._assert_ajax_success(response)
	
	def test_add_playlist_bookmark_bad_request(self):
		client_id = self._create_user('user_name')
		video_id = self._create_video('video_name', 99)
		bookmark_id = self._create_bookmark(client_id, video_id, 'comment', 33)
		playlist_id = db.create_playlist(client_id, 'playlist_name', now=self.now)

		# Assert that the request fails with a missing client identifier.
		with app.test_client() as client:
			response = client.post('/add_playlist_bookmark',
					data={'playlist_id': playlist_id, 'bookmark_id': bookmark_id})
			self._assert_ajax_failure(response)

		# Assert that the request fails with a missing playlist identifier.
		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/add_playlist_bookmark', data={'bookmark_id': bookmark_id})
			self._assert_ajax_failure(response)
	
		# Assert that the request fails with a missing bookmark identifier.
		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/add_playlist_bookmark', data={'playlist_id': playlist_id})
			self._assert_ajax_failure(response)

	def test_remove_playlist_bookmark(self):
		client_id = self._create_user('user_name')
		video_id = self._create_video('video_name', 99)
		bookmark_id = self._create_bookmark(client_id, video_id, 'comment', 33)
		playlist_id = db.create_playlist(client_id, 'playlist_name', now=self.now)
		db.add_playlist_bookmark(client_id, playlist_id, bookmark_id, now=self.now)

		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/remove_playlist_bookmark',
					data={'playlist_id': playlist_id, 'bookmark_id': bookmark_id})
			self._assert_ajax_success(response)
		
	def test_remove_playlist_bookmark_bad_request(self):
		client_id = self._create_user('user_name')
		video_id = self._create_video('video_name', 99)
		bookmark_id = self._create_bookmark(client_id, video_id, 'comment', 33)
		playlist_id = db.create_playlist(client_id, 'playlist_name', now=self.now)
		db.add_playlist_bookmark(client_id, playlist_id, bookmark_id, now=self.now)

		# Assert that the request fails with a missing client identifier.
		with app.test_client() as client:
			response = client.post('/remove_playlist_bookmark',
					data={'playlist_id': playlist_id, 'bookmark_id': bookmark_id})
			self._assert_ajax_failure(response)

		# Assert that the request fails with a missing playlist identifier.
		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/remove_playlist_bookmark', data={'bookmark_id': bookmark_id})
			self._assert_ajax_success(response)

		# Assert that the request fails with a missing bookmark identifier.
		with app.test_client() as client:
			self._add_client_id(client, client_id)
			response = client.post('/remove_playlist_bookmark', data={'playlist_id': playlist_id})
			self._assert_ajax_failure(response)
	
	def test_vote_playlist_thumb_up(self):
		pass
	
	def test_vote_playlist_thumb_up_bad_request(self):
		pass
	
	def test_vote_playlist_thumb_down(self):
		pass
	
	def test_vote_playlist_thumb_down_bad_request(self):
		pass
	
	def test_remove_playlist_vote(self):
		pass
	
	def test_remove_playlist_vote_bad_request(self):
		pass
	
	def test_vote_bookmark_thumb_up(self):
		pass
	
	def test_vote_bookmark_thumb_up_bad_request(self):
		pass
	
	def test_vote_bookmark_thumb_down(self):
		pass
	
	def test_vote_bookmark_thumb_down_bad_request(self):
		pass
	
	def test_remove_bookmark_vote(self):
		pass

	def test_remove_bookmark_vote_bad_request(self):
		pass

