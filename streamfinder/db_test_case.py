from datetime import datetime, timedelta
import db
import unittest

import common_db

"""Base class for test cases that use the database.
"""
class DbTestCase(unittest.TestCase):
	def setUp(self):
		unittest.TestCase.setUp(self)
		self.now = datetime(2012, 10, 15, 12, 30, 45)
		self._next_steam_id = 0
		self._next_twitch_id = 0
		db.create_all()
		self.session = common_db.session
	
	def tearDown(self):
		db.drop_all()
		unittest.TestCase.tearDown(self)

	def _create_steam_user(self, display_name, indexed_name):
		"""Utility method for creating a Steam user."""
		steam_id = self._next_steam_id
		self._next_steam_id += 1
		profile_url = 'http://steamcommunity.com/id/%s' % display_name
		user_id = db.steam_user_logged_in(
				steam_id, display_name, indexed_name, profile_url, None, None)
		return steam_id, user_id

	def _create_twitch_user(self, display_name, indexed_name):
		"""Utility method for creating a Twitch user."""
		twitch_id = self._next_twitch_id
		self._next_twitch_id += 1
		name = display_name
		user_id = db.twitch_user_logged_in(
				twitch_id, name, display_name, indexed_name, None)
		return twitch_id, user_id

	def _get_steam_user_url(self, steam_id):
		"""Utility method to create a URL for a user given its Steam identifier."""
		return '/user/steam_id/%s' % steam_id

