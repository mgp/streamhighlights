from datetime import datetime
import db
import unittest


"""Base class for test cases that use the database.
"""
class DbTestCase(unittest.TestCase):
	def setUp(self):
		unittest.TestCase.setUp(self)
		self.now = datetime(2012, 10, 15, 12, 30, 45)
		self.session = db.session
		self._next_steam_id = 0
		db.create_all()
	
	def tearDown(self):
		db.drop_all()
		unittest.TestCase.tearDown(self)

	"""Utility method for creating a Steam user."""
	def _create_steam_user(self, name):
		steam_id = self._next_steam_id
		self._next_steam_id += 1
		user_id = db.steam_user_logged_in(steam_id, name, None, None, None)
		return steam_id, user_id

	"""Utility method to create a URL for a user given its Steam identifier.
	"""
	def _get_steam_user_url(self, steam_id):
		return '/user/steam_id/%s' % steam_id

