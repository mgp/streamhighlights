import json
import requests
import unittest
import views

class TestViews(unittest.TestCase):
	def setUp(self):
		self.client_id = 'client_id'
	
	def tearDown(self):
		pass
	
	def _add_client_id(self, client):
		with client.session_transaction() as session
			session['client_id'] = self.client_id

	def _assert_ajax_success(self, response):
		self.assertEqual(requests.codes.ok, response.status_code)
		json_response = json.loads(response.data)
		self.assertTrue(json_response['success'])
	
	def _assert_ajax_failure(self, response):
		self.assertEqual(requests.codes.ok, response.status_code)
		json_response = json.loads(response.data)
		self.assertFalse(json_response['success'])
	
	def test_add_playlist_bookmark(self):
		playlist_id = 'playlist_id'
		bookmark_id = 'bookmark_id'

		with app.test_client() as client:
			self._add_client_id(client)
			response = client.post('/add_playlist_bookmark',
					data={'playlist_id': playlist_id, 'bookmark_id': bookmark_id})
			self._assert_ajax_success(response)
	
	def test_add_playlist_bookmark_bad_request(self):
		# Assert that the request fails with a missing client identifier.
		# TODO

		# Assert that the request fails with a missing playlist identifier.
		# TODO
	
	def test_remove_playlist_bookmark(self):
		pass
	
	def test_remove_playlist_bookmark_bad_request(self):
		pass
	
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


