from datetime import datetime, timedelta
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

	"""Utility method to assert the fields in a DisplayedUser.
	"""
	def _assert_displayed_user(self, displayed_user, user_id, name,
			image_url_small=None, image_url_large=None, num_playlists=0):
		# Begin required arguments.
		self.assertIsNotNone(displayed_user)
		self.assertEqual(user_id, displayed_user.id)
		self.assertEqual(name, displayed_user.name)
		self.assertEqual(image_url_small, displayed_user.image_url_small)
		self.assertEqual(image_url_large, displayed_user.image_url_large)
		self.assertEqual(num_playlists, len(displayed_user.playlists))

	"""Utility method to assert the fields in a DisplayedTwitchUser.
	"""
	def _assert_displayed_twitch_user(self, displayed_twitch_user,
			user_id, name, twitch_id, link_url,
			image_url_small=None, image_url_large=None, num_playlists=0):
		self._assert_displayed_user(displayed_twitch_user, user_id, name,
				image_url_small, image_url_large, num_playlists)
		self.assertEqual(twitch_id, displayed_twitch_user.twitch_id)
		self.assertEqual(link_url, displayed_twitch_user.link_url)

	"""Utility method to assert the fields in a DisplayedSteamUser.
	"""
	def _assert_displayed_steam_user(self, displayed_steam_user,
			user_id, name, steam_id, link_url=None,
			image_url_small=None, image_url_large=None, num_playlists=0):
		if link_url is None:
			link_url = 'http://steamcommunity.com/profiles/%s' % steam_id

		self._assert_displayed_user(displayed_steam_user, user_id, name,
				image_url_small, image_url_large, num_playlists)
		self.assertEqual(steam_id, displayed_steam_user.steam_id)
		self.assertEqual(link_url, displayed_steam_user.link_url)

