from datetime import datetime, timedelta
import db
import unittest


"""Base class for test cases that use the database.
"""
class DbTestCase(unittest.TestCase):
	"""Utility method for creating a Steam user."""
	def _create_steam_user(self, name):
		steam_id = self._next_steam_id
		self._next_steam_id += 1
		user_id = db.steam_user_logged_in(steam_id, name, None, None, None)
		return steam_id, user_id

	def setUp(self):
		unittest.TestCase.setUp(self)
		self.now = datetime(2012, 10, 15, 12, 30, 45)
		self.session = db.session
		self._next_steam_id = 0
		db.create_all()
	
	def tearDown(self):
		db.drop_all()
		unittest.TestCase.tearDown(self)

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

	"""Utility method to assert the fields in a DisplayedUserPlaylist.
	"""
	def _assert_displayed_user_playlist(self,
			displayed_user_playlist, playlist_id, title, time_created,
			time_updated=None, num_thumbs_up=0, num_thumbs_down=0, user_vote=None,
			num_bookmarks=0):
		if time_updated is None:
			time_updated = time_created

		# Begin required arguments.
		self.assertIsNotNone(displayed_user_playlist)
		self.assertEqual(playlist_id, displayed_user_playlist.id)
		self.assertEqual(time_created, displayed_user_playlist.time_created)
		self.assertEqual(time_updated, displayed_user_playlist.time_updated)
		# Begin optional arguments.
		self.assertEqual(num_thumbs_up, displayed_user_playlist.num_thumbs_up)
		self.assertEqual(num_thumbs_down, displayed_user_playlist.num_thumbs_down)
		self.assertEqual(user_vote, displayed_user_playlist.user_vote)
		self.assertEqual(title, displayed_user_playlist.title)
		self.assertEqual(num_bookmarks, displayed_user_playlist.num_bookmarks)

	"""Utility method to assert the fields in a DisplayedPlaylist.
	"""
	def _assert_displayed_playlist(self,
			displayed_playlist, author_id, author_name, time_created, title,
			time_updated=None, num_thumbs_up=0, num_thumbs_down=0, user_vote=None,
			author_image_url_large=None, author_site_url=None, num_bookmarks=0):
		if time_updated is None:
			time_updated = time_created

		# Begin required arguments.
		self.assertIsNotNone(displayed_playlist)
		self.assertEqual(author_name, displayed_playlist.author_name)
		self.assertEqual(time_created, displayed_playlist.time_created)
		self.assertEqual(title, displayed_playlist.title)
		# Begin optional arguments.
		self.assertEqual(time_updated, displayed_playlist.time_updated)
		self.assertEqual(num_thumbs_up, displayed_playlist.num_thumbs_up)
		self.assertEqual(num_thumbs_down, displayed_playlist.num_thumbs_down)
		self.assertEqual(user_vote, displayed_playlist.user_vote)
		self.assertEqual(
				author_image_url_large, displayed_playlist.author_image_url_large)
		# TODO self.assertEqual(author_site_url, displayed_playlist.author_site_url)
		self.assertEqual(num_bookmarks, len(displayed_playlist.bookmarks))

	"""Utility method to assert the fields in a DisplayedPlaylistBookmark.
	"""
	def _assert_displayed_playlist_bookmark(self,
			displayed_playlist_bookmark, bookmark_id, video_title, comment,
			time_added, author_name, author_id,
			num_thumbs_up=0, num_thumbs_down=0, user_vote=None,
			author_image_url_small=None, author_site_url=None):

		# Begin required arguments.
		self.assertIsNotNone(displayed_playlist_bookmark)
		self.assertEqual(bookmark_id, displayed_playlist_bookmark.id)
		self.assertEqual(video_title, displayed_playlist_bookmark.video_title)
		self.assertEqual(comment, displayed_playlist_bookmark.comment)
		self.assertEqual(time_added, displayed_playlist_bookmark.time_added)
		self.assertEqual(author_name, displayed_playlist_bookmark.author_name)
		# Begin optional arguments.
		self.assertEqual(num_thumbs_up, displayed_playlist_bookmark.num_thumbs_up)
		self.assertEqual(num_thumbs_down, displayed_playlist_bookmark.num_thumbs_down)
		self.assertEqual(user_vote, displayed_playlist_bookmark.user_vote)
		self.assertEqual(
				author_image_url_small, displayed_playlist_bookmark.author_image_url_small)
		# TODO self.assertEqual(author_site_url, displayed_playlist_bookmark.author_site_url)

	"""Utility method to assert the fields in a DisplayedVideo.
	"""
	def _assert_displayed_video(self,
			displayed_video, title, length, num_bookmarks=0):
		# Begin required arguments.
		self.assertIsNotNone(displayed_video)
		self.assertEqual(title, displayed_video.title)
		self.assertEqual(length, displayed_video.length)
		# Begin optional arguments.
		self.assertEqual(num_bookmarks, len(displayed_video.bookmarks))

	"""Utility method to assert the fields in a DisplayedTwitchVideo.
	"""
	def _assert_displayed_twitch_video(self,
			displayed_twitch_video, title, length, archive_id, video_file_url, link_url,
			num_bookmarks=0):
		self._assert_displayed_video(displayed_twitch_video, title, length, num_bookmarks)
		self.assertEqual(archive_id, displayed_twitch_video.archive_id)
		self.assertEqual(video_file_url, displayed_twitch_video.video_file_url)
		self.assertEqual(link_url, displayed_twitch_video.link_url)

	"""Utility method to assert the fields in a DisplayedVideoBookmark.
	"""
	def _assert_displayed_video_bookmark(self,
			displayed_video_bookmark, bookmark_id, comment, time, time_created,
			author_name, author_id, 
			num_thumbs_up=0, num_thumbs_down=0, user_vote=None,
			author_image_url_small=None, author_site_url=None):

		# Begin required arguments.
		self.assertIsNotNone(displayed_video_bookmark)
		self.assertEqual(bookmark_id, displayed_video_bookmark.id)
		self.assertEqual(comment, displayed_video_bookmark.comment)
		self.assertEqual(time, displayed_video_bookmark.time)
		self.assertEqual(time_created, displayed_video_bookmark.time_created)
		self.assertEqual(author_name, displayed_video_bookmark.author_name)
		# Begin optional arguments.
		self.assertEqual(num_thumbs_up, displayed_video_bookmark.num_thumbs_up)
		self.assertEqual(num_thumbs_down, displayed_video_bookmark.num_thumbs_down)
		self.assertEqual(user_vote, displayed_video_bookmark.user_vote)
		self.assertEqual(
				author_image_url_small, displayed_video_bookmark.author_image_url_small)
		# TODO self.assertEqual(author_site_url, displayed_video_bookmark.author_site_url)

