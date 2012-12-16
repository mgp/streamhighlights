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
		self.session = common_db.session
		self._next_steam_id = 0
		self._next_twitch_id = 0
		db.create_all()
	
	def tearDown(self):
		db.drop_all()
		unittest.TestCase.tearDown(self)

	def _create_steam_user(self, name):
		"""Utility method for creating a Steam user."""
		steam_id = self._next_steam_id
		self._next_steam_id += 1
		profile_url = 'http://steamcommunity.com/id/%s' % name
		user_id = common_db.steam_user_logged_in(
				db.User, db.Users, steam_id, name, profile_url, None, None)
		return steam_id, user_id

	def _create_twitch_user(self, name):
		"""Utility method for creating a Twitch user."""
		twitch_id = self._next_twitch_id
		self._next_twitch_id += 1
		display_name = name
		user_class_extra_kwargs = {'can_stream': True}
		user_id = common_db.twitch_user_logged_in(
				db.User, db.Users, twitch_id, name, display_name, None, None,
				user_class_extra_kwargs=user_class_extra_kwargs)
		return twitch_id, user_id

	def _get_steam_user_url(self, steam_id):
		"""Utility method to create a URL for a user given its Steam identifier."""
		return '/user/steam_id/%s' % steam_id

