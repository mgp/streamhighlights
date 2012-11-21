from datetime import timedelta
import db
from db_test_case import DbTestCase
import sqlalchemy.orm as sa_orm


class TestDb(DbTestCase):

	"""Test that creates user URLs by id.
	"""
	def test_get_url_by_id(self):
		# Assert the URL by name given a Steam identifier.
		steam_id = 456
		steam_url_by_id = db._get_steam_url_by_id(steam_id)
		self.assertEqual('s:456', steam_url_by_id)

		# Assert the URL by name given a Twitch identifier.
		twitch_id = 123
		twitch_url_by_id = db._get_twitch_url_by_id(twitch_id)
		self.assertEqual('t:123', twitch_url_by_id)

	def _assert_get_community_id_regex_success(self, url, community_id):
		community_id_match = db._GET_COMMUNITY_ID_REGEX.search(url)
		self.assertIsNotNone(community_id_match)
		self.assertEqual(community_id, community_id_match.group('community_id'))

	def _assert_get_community_id_regex_failure(self, url):
		self.assertFalse(db._GET_COMMUNITY_ID_REGEX.search(url))

	"""Test that extracts community IDs from profile URLs.
	"""
	def test_get_community_id_regex_success(self):
		self._assert_get_community_id_regex_success('steamcommunity.com/id/foo', 'foo')
		self._assert_get_community_id_regex_success(
				'http://www.steamcommunity.com/id/b4z', 'b4z')
		self._assert_get_community_id_regex_success(
				'https://www.steamcommunity.com/id/456', '456')

	"""Test that fails to extract community IDs from invalid profile URLs.
	"""
	def test_get_community_id_regex_failure(self):
		self._assert_get_community_id_regex_failure('/id/foo')
		self._assert_get_community_id_regex_failure('steampowered.com/id/foo')
		self._assert_get_community_id_regex_failure('steamcommunity.net/id/bar')
		self._assert_get_community_id_regex_failure('steamcommunity.com/profile/123456')

	"""Test that creates user URLs by name.
	"""
	def test_get_url_by_name(self):
		# Assert no URL by name for a missing Steam profile URL.
		profile_url = None
		self.assertIsNone(db._get_steam_url_by_name_from_profile_url(profile_url))
		# Assert no URL by name for a Steam profile URL without a community identifier.
		profile_url = 'http://steamcommunity.com/profiles/123'
		self.assertIsNone(db._get_steam_url_by_name_from_profile_url(profile_url))
		# Assert the URL by name for a Steam profile URL with a community identifier.
		profile_url = 'http://steamcommunity.com/id/mgp'
		steam_url_by_name = db._get_steam_url_by_name_from_profile_url(profile_url)
		self.assertEqual('s:mgp', steam_url_by_name)

		# Assert the URL by name for a Twitch name.
		twitch_name = 'mgp'
		twitch_url_by_name = db._get_twitch_url_by_name(twitch_name)
		self.assertEqual('t:mgp', twitch_url_by_name)

	def test_get_user_url(self):
		# Assert that a URL can be built from a Steam name.
		user_url = db._get_user_url(url_by_id='s:123', url_by_name='s:mgp1')
		self.assertEqual('/user/steam/mgp1', user_url)

		# Assert that a URL can be built from a Steam identifier.
		user_url = db._get_user_url(url_by_id='s:456', url_by_name=None)
		self.assertEqual('/user/steam_id/456', user_url)

		# Assert that a URL can be built from a Twitch name.
		user_url = db._get_user_url(url_by_id='t:234', url_by_name='t:mgp2')
		self.assertEqual('/user/twitch/mgp2', user_url)

		# Assert that a URL can be built from a Twitch identifier.
		user_url = db._get_user_url(url_by_id='t:567', url_by_name=None)
		self.assertEqual('/user/twitch_id/567', user_url)

		# Assert that an URL cannot be built from an invalid identifier.
		with self.assertRaises(ValueError):
			user_url = db._get_user_url(url_by_id='z:007', url_by_name=None)

	def _get_twitch_user(self, twitch_id):
		twitch_user = self.session.query(db.TwitchUser)\
				.options(sa_orm.joinedload(db.TwitchUser.user))\
				.filter(db.TwitchUser.twitch_id == twitch_id).one()
		self.session.close()
		return twitch_user

	"""Test that creates and updates a Twitch user.
	"""
	def test_twitch_user_logged_in(self):
		# Create a new Twitch user.
		twitch_id = 123
		name = 'name'
		display_name = 'display_name'
		logo = 'logo_url'
		access_token = 'access_token'
		user_id = db.twitch_user_logged_in(
				twitch_id, name, display_name, logo, access_token, self.now)
		self.assertIsNotNone(user_id)

		# XXX
		"""
		# Get the Twitch user by both ID and by name.
		expected_link_url = 'http://www.twitch.tv/%s' % name
		for displayed_twitch_user in (
				db.get_displayed_twitch_user_by_id(None, twitch_id),
				db.get_displayed_twitch_user_by_name(None, name)):
			# Assert that the created Twitch user was returned.
			self._assert_displayed_twitch_user(displayed_twitch_user,
					user_id, display_name, twitch_id, expected_link_url, image_url_large=logo)
		"""

		# Assert that the fields not returned in a DisplayedTwitchUser are correct.
		twitch_user = self._get_twitch_user(twitch_id)
		self.assertEqual('t:%s' % twitch_id, twitch_user.user.url_by_id)
		self.assertEqual('t:%s' % name, twitch_user.user.url_by_name)
		self.assertEqual(self.now, twitch_user.user.created)
		self.assertEqual(self.now, twitch_user.user.last_seen)
		self.assertEqual(access_token, twitch_user.access_token)

		# Update the Twitch user by both ID and by updated name.
		updated_name = 'updated_name'
		updated_display_name = 'updated_display_name'
		updated_logo = 'updated_logo_url'
		updated_access_token = 'updated_access_token'
		updated_time = self.now + timedelta(minutes=10)
		updated_user_id = db.twitch_user_logged_in(
				twitch_id, updated_name, updated_display_name,
				updated_logo, updated_access_token, updated_time)
		self.assertEqual(updated_user_id, user_id)

		# XXX
		"""
		# Get the Twitch user.
		updated_expected_link_url = 'http://www.twitch.tv/%s' % updated_name
		for displayed_twitch_user in (
				db.get_displayed_twitch_user_by_id(None, twitch_id),
				db.get_displayed_twitch_user_by_name(None, updated_name)):
			# Assert that the updated Twitch user was returned.
			self._assert_displayed_twitch_user(displayed_twitch_user,
					user_id, updated_display_name, twitch_id,
					updated_expected_link_url, image_url_large=updated_logo)
		"""

		# Assert that the fields not returned in a DisplayedTwitchUser are correct.
		twitch_user = self._get_twitch_user(twitch_id)
		self.assertEqual('t:%s' % twitch_id, twitch_user.user.url_by_id)
		self.assertEqual('t:%s' % updated_name, twitch_user.user.url_by_name)
		self.assertEqual(self.now, twitch_user.user.created)
		self.assertEqual(updated_time, twitch_user.user.last_seen)
		self.assertEqual(updated_access_token, twitch_user.access_token)

		# XXX
		"""
		# Assert that the Twitch user cannot be found by its old name.
		with self.assertRaises(db.DbException):
			db.get_displayed_twitch_user_by_name(None, name)
		"""

	def _get_steam_user(self, steam_id):
		steam_user = self.session.query(db.SteamUser)\
				.options(sa_orm.joinedload(db.SteamUser.user))\
				.filter(db.SteamUser.steam_id == steam_id).one()
		self.session.close()
		return steam_user

	"""Test that creates and updates a Steam user.
	"""
	def test_steam_user_logged_in(self):
		# Create a new Steam user.
		steam_id = 456
		personaname = 'personaname'
		community_id = 'community_id'
		profile_url = 'steamcommunity.com/id/%s' % community_id
		avatar = 'avatar'
		avatar_full = 'avatar_full'
		user_id = db.steam_user_logged_in(
				steam_id, personaname, profile_url, avatar, avatar_full, self.now)
		self.assertIsNotNone(user_id)

		# XXX
		"""
		# Get the Steam user by both Steam ID and by name.
		for displayed_steam_user in (
				db.get_displayed_steam_user_by_id(None, steam_id),
				db.get_displayed_steam_user_by_name(None, community_id)):
			# Assert that the created Steam user was returned.
			self._assert_displayed_steam_user(displayed_steam_user,
					user_id, personaname, steam_id, profile_url,
					image_url_small=avatar, image_url_large=avatar_full)
		"""

		# Assert that the fields not returned in a DisplayedSteamUser are correct.
		steam_user = self._get_steam_user(steam_id)
		self.assertEqual('s:%s' % steam_id, steam_user.user.url_by_id)
		self.assertEqual('s:%s' % community_id, steam_user.user.url_by_name)
		self.assertEqual(self.now, steam_user.user.created)
		self.assertEqual(self.now, steam_user.user.last_seen)

		# Update the Steam user.
		updated_personaname = 'updated_personaname'
		updated_community_id = 'updated_community_id'
		updated_profile_url = 'steamcommunity.com/id/%s' % updated_community_id
		updated_avatar = 'updated_avatar'
		updated_avatar_full = 'updated_avatar_full'
		updated_time = self.now + timedelta(minutes=10)
		updated_user_id = db.steam_user_logged_in(
				steam_id, updated_personaname,
				updated_profile_url, updated_avatar, updated_avatar_full, updated_time)
		self.assertEqual(updated_user_id, user_id)

		# XXX
		"""
		# Get the Steam user by both Steam ID and by updated name.
		for displayed_steam_user in (
				db.get_displayed_steam_user_by_id(None, steam_id),
				db.get_displayed_steam_user_by_name(None, updated_community_id)):
			# Assert that the updated Steam user was returned.
			self._assert_displayed_steam_user(displayed_steam_user,
					user_id, updated_personaname, steam_id, updated_profile_url,
					image_url_small=updated_avatar, image_url_large=updated_avatar_full)
		"""

		# Assert that the fields not returned in a DisplayedSteamUser are correct.
		steam_user = self._get_steam_user(steam_id)
		self.assertEqual('s:%s' % steam_id, steam_user.user.url_by_id)
		self.assertEqual('s:%s' % updated_community_id, steam_user.user.url_by_name)
		self.assertEqual(self.now, steam_user.user.created)
		self.assertEqual(updated_time, steam_user.user.last_seen)

		# XXX
		"""
		# Assert that the Steam user cannot be found by its old name.
		with self.assertRaises(db.DbException):
			db.get_displayed_steam_user_by_name(None, community_id)
		"""

	"""Test that the name associated with a Twitch user is unique.
	"""
	def test_twitch_user_name_is_unique(self):
		name = 'name'
		expected_link_url = 'http://www.twitch.tv/%s' % name

		# Create the first Twitch user.
		add_time1 = self.now + timedelta(minutes=10)
		twitch_id1 = 123
		display_name1 = 'display_name1'
		logo1 = 'logo_url1'
		access_token1 = 'access_token1'
		user_id1 = db.twitch_user_logged_in(
				twitch_id1, name, display_name1, logo1, access_token1, add_time1)

		# Create the second Twitch user.
		add_time2 = self.now + timedelta(minutes=20)
		twitch_id2 = 456
		display_name2 = 'display_name2'
		logo2 = 'logo_url2'
		access_token2 = 'access_token2'
		user_id2 = db.twitch_user_logged_in(
				twitch_id2, name, display_name2, logo2, access_token2, add_time2)

		# XXX
		"""
		# Assert that the second Twitch user is returned by the shared name.
		displayed_twitch_user = db.get_displayed_twitch_user_by_name(None, name)
		self._assert_displayed_twitch_user(displayed_twitch_user,
				user_id2, display_name2, twitch_id2, expected_link_url, image_url_large=logo2)
		"""

		# Assert that the first Twitch user is no longer associated with the shared name.
		twitch_user = self._get_twitch_user(twitch_id1)
		self.assertEqual('t:%s' % twitch_id1, twitch_user.user.url_by_id)
		self.assertIsNone(twitch_user.user.url_by_name)
		self.assertEqual(add_time1, twitch_user.user.created)
		self.assertEqual(add_time1, twitch_user.user.last_seen)
		self.assertEqual(access_token1, twitch_user.access_token)
		# Assert that the second Twitch user is associated with the shared name.
		twitch_user = self._get_twitch_user(twitch_id2)
		self.assertEqual('t:%s' % twitch_id2, twitch_user.user.url_by_id)
		self.assertEqual('t:%s' % name, twitch_user.user.url_by_name)
		self.assertEqual(add_time2, twitch_user.user.created)
		self.assertEqual(add_time2, twitch_user.user.last_seen)
		self.assertEqual(access_token2, twitch_user.access_token)

		# Log in the first Twitch user again with the same name.
		add_time3 = self.now + timedelta(minutes=30)
		db.twitch_user_logged_in(
				twitch_id1, name, display_name1, logo1, access_token1, add_time3)

		# XXX
		"""
		# Assert that the second Twitch user is returned by the shared name.
		displayed_twitch_user = db.get_displayed_twitch_user_by_name(None, name)
		self._assert_displayed_twitch_user(displayed_twitch_user,
				user_id1, display_name1, twitch_id1, expected_link_url, image_url_large=logo1)
		"""

		# Assert that the first Twitch user is associated with the shared name.
		twitch_user = self._get_twitch_user(twitch_id1)
		self.assertEqual('t:%s' % twitch_id1, twitch_user.user.url_by_id)
		self.assertEqual('t:%s' % name, twitch_user.user.url_by_name)
		self.assertEqual(add_time1, twitch_user.user.created)
		self.assertEqual(add_time3, twitch_user.user.last_seen)
		self.assertEqual(access_token1, twitch_user.access_token)
		# Assert that the second Twitch user is no longer associated with the shared name.
		twitch_user = self._get_twitch_user(twitch_id2)
		self.assertEqual('t:%s' % twitch_id2, twitch_user.user.url_by_id)
		self.assertIsNone(twitch_user.user.url_by_name)
		self.assertEqual(add_time2, twitch_user.user.created)
		self.assertEqual(add_time2, twitch_user.user.last_seen)
		self.assertEqual(access_token2, twitch_user.access_token)

	"""Test that the name associated with a Steam user is unique.
	"""
	def test_steam_user_name_is_unique(self):
		community_id = 'community_id'
		profile_url = 'steamcommunity.com/id/%s' % community_id

		# Create the first Steam user.
		add_time1 = self.now + timedelta(minutes=10)
		steam_id1 = 123
		personaname1 = 'personaname1'
		avatar1 = 'avatar1'
		avatar_full1 = 'avatar_full1'
		user_id1 = db.steam_user_logged_in(
				steam_id1, personaname1, profile_url, avatar1, avatar_full1, add_time1)

		# Create the second Steam user with the same name.
		add_time2 = self.now + timedelta(minutes=20)
		steam_id2 = 456
		personaname2 = 'personaname2'
		avatar2 = 'avatar2'
		avatar_full2 = 'avatar_full2'
		user_id2 = db.steam_user_logged_in(
				steam_id2, personaname2, profile_url, avatar2, avatar_full2, add_time2)

		# XXX
		"""
		# Assert that the second Steam user is returned by the shared name.
		displayed_steam_user = db.get_displayed_steam_user_by_name(None, community_id)
		self._assert_displayed_steam_user(displayed_steam_user,
				user_id2, personaname2, steam_id2, profile_url,
				image_url_small=avatar2, image_url_large=avatar_full2)
		"""

		# Assert that the first Steam user is no longer associated with the shared name.
		steam_user = self._get_steam_user(steam_id1)
		self.assertEqual('s:%s' % steam_id1, steam_user.user.url_by_id)
		self.assertIsNone(steam_user.user.url_by_name)
		self.assertEqual(add_time1, steam_user.user.created)
		self.assertEqual(add_time1, steam_user.user.last_seen)
		# Assert that the second Steam user is associated with the shared name.
		steam_user = self._get_steam_user(steam_id2)
		self.assertEqual('s:%s' % steam_id2, steam_user.user.url_by_id)
		self.assertEqual('s:%s' % community_id, steam_user.user.url_by_name)
		self.assertEqual(add_time2, steam_user.user.created)
		self.assertEqual(add_time2, steam_user.user.last_seen)

		# Log in the first Steam user again with the same name.
		add_time3 = self.now + timedelta(minutes=30)
		db.steam_user_logged_in(
				steam_id1, personaname1, profile_url, avatar1, avatar_full1, add_time3)

		# XXX
		"""
		# Assert that the first Steam user is returned by the shared name.
		displayed_steam_user = db.get_displayed_steam_user_by_name(None, community_id)
		self._assert_displayed_steam_user(displayed_steam_user,
				user_id1, personaname1, steam_id1, profile_url,
				image_url_small=avatar1, image_url_large=avatar_full1)
		"""

		# Assert that the first Steam user is associated with the shared name.
		steam_user = self._get_steam_user(steam_id1)
		self.assertEqual('s:%s' % steam_id1, steam_user.user.url_by_id)
		self.assertEqual('s:%s' % community_id, steam_user.user.url_by_name)
		self.assertEqual(add_time1, steam_user.user.created)
		self.assertEqual(add_time3, steam_user.user.last_seen)
		# Assert that the second Steam user is no longer associated with the shared name.
		steam_user = self._get_steam_user(steam_id2)
		self.assertEqual('s:%s' % steam_id2, steam_user.user.url_by_id)
		self.assertIsNone(steam_user.user.url_by_name)
		self.assertEqual(add_time2, steam_user.user.created)
		self.assertEqual(add_time2, steam_user.user.last_seen)

