from datetime import datetime
import bookmarks_db
import unittest

class TestBookmarksDb(unittest.TestCase):
	"""Utility method for creating a user."""
	def _create_user(self, name):
		user = bookmarks_db.User(name, now=self.now)
		self.session.add(user)
		self.session.commit()
		return user.id

	"""Utility method for creating a video."""
	def _create_video(self):
		# TODO
		pass

	def setUp(self):
		unittest.TestCase.setUp(self)
		self.now = datetime(2012, 10, 15, 12, 30, 45)
		self.session = bookmarks_db.session
		bookmarks_db.create_all()
	
	def tearDown(self):
		unittest.TestCase.tearDown(self)
		bookmarks_db.drop_all()
	
	def _assert_displayed_playlist(displayed_playlist, playlist_id, name, time_created,
			time_updated=None, num_thumbs_up=0, num_thumbs_down=0, user_vote=None, num_bookmarks=0):
		if time_updated is None:
			time_updated = time_created

		self.assertEqual(playlist_id, displayed_playlist.id)
		self.assertEqual(time_created, displayed_playlist.time_created)
		self.assertEqual(time_updated, displayed_playlist.time_updated)
		self.assertEqual(num_thumbs_up, displayed_playlist.num_thumbs_up)
		self.assertEqual(num_thumbs_down, displayed_playlist.num_thumbs_down)
		self.assertEqual(user_vote, displayed_playlist.user_vote)
		self.assertEqual(name, displayed_playlist.name)
		self.assertEqual(num_bookmarks, displayed_playlist.num_bookmarks)

	#
	# Begin tests for users.
	# 

	"""Test that fails to return a displayed user because the user identifier is
	unknown.
	"""
	def test_get_displayed_user_unknown_user(self):
		missing_user_id = 'missing_user_id'
		with self.assertRaises(ValueError):
			bookmarks_db.get_displayed_user(missing_user_id)

	"""Test that fails to create a playlist because the user identifier is unknown.
	"""
	def test_create_playlist_unknown_user(self):
		missing_user_id = 'missing_user_id'
		playlist_name = 'playlist1'
		with self.assertRaises(ValueError):
			bookmarks_db.create_playlist(missing_user_id, playlist_name)

	"""Test that successfully creates and deletes a bookmark.
	"""
	def test_create_delete_playlist(self):
		# Create a playlist for a user.
		user_name = 'user_name1'
		user_id = self._create_user(user_name)
		playlist_name = 'playlist1'
		playlist_id = bookmarks_db.create_playlist(user_id, playlist_name, now=self.now)

		# Get the displayed user.
		displayed_user = bookmarks_db.get_displayed_user(user_id)
		self.assertIsNotNone(displayed_user)
		self.assertEqual(user_id, displayed_user.id)
		self.assertEqual(user_name, displayed_user.name)
		# Assert that the created playlist was returned.
		self.assertEqual(1, len(displayed_user.playlists))
		displayed_playlist = displayed_user.playlists[0]
		self._assert_displayed_playlist(displayed_playlist,
				playlist_id, playlist_name, self.now)

		# Delete the playlist.
		bookmarks_db.delete_playlist(user_id, playlist_id)

		# Get the displayed user.
		displayed_user = bookmarks_db.get_displayed_user(user_id)
		self.assertIsNotNone(displayed_user)
		self.assertEqual(user_id, displayed_user.id)
		self.assertEqual(user_name, displayed_user.name)
		# Assert that the playlist is not returned.
		self.assertEqual(0, len(displayed_user.playlists))

	"""Test that fails to delete a playlist that does not exist.
	"""
	def test_delete_missing_playlist(self):
		# Assert that deleting a missing playlist has no effect.
		user_name = 'user_name1'
		user_id = self._create_user(user_name)
		missing_playlist_id = 'missing_playlist_id'
		bookmarks_db.delete_playlist(user_id, missing_playlist_id)

		# Get the displayed user.
		displayed_user = bookmarks_db.get_displayed_user(user_id)
		self.assertIsNotNone(displayed_user)
		self.assertEqual(user_id, displayed_user.id)
		self.assertEqual(user_name, displayed_user.name)
		self.assertEqual(0, len(displayed_user.playlists))

	"""Test that fails to delete a playlist because the user identifier is not the
	creator.
	"""
	def test_delete_playlist_wrong_user(self):
		# Create a playlist for a user.
		user_name1 = 'user_name1'
		user_id1 = self._create_user(user_name1)
		playlist_name = 'playlist1'
		playlist_id = bookmarks_db.create_playlist(user_id1, playlist_name, now=self.now)
		# Create another user.
		user_name2 = 'user_name2'
		user_id2 = self._create_user(user_name2)

		# Attempt to delete the playlist with another user.
		with self.assertRaises(ValueError):
			bookmarks_db.delete_playlist(user_id2, playlist_id)

		# Get the user with the playlist.
		displayed_user = bookmarks_db.get_displayed_user(user_id1)
		self.assertIsNotNone(displayed_user)
		self.assertEqual(user_id1, displayed_user.id)
		self.assertEqual(user_name, displayed_user.name)
		# Assert that the created playlist still exists.
		self.assertEqual(1, len(displayed_user.playlists))
		displayed_playlist = displayed_user.playlists[0]
		self._assert_displayed_playlist(displayed_playlist,
				playlist_id, playlist_name, self.now)


	# 
	# Begin tests for playlists.
	# 

	"""Test that fails to return a displayed playlist because the playlist identifier
	is unknown.
	"""
	def test_get_displayed_playlist_unknown_playlist(self):
		# TODO
		pass

	"""Test that fails to add a bookmark to a playlist because the user identifier
	is unknown.
	"""
	def test_add_playlist_bookmark_unknown_user(self):
		# TODO
		pass
	
	"""Test that fails to add a bookmark to a playlist because the playlist identifier
	is unknown.
	"""
	def test_add_playlist_bookmark_unknown_playlist(self):
		# TODO
		pass
	
	"""Test that fails to add a bookmark to a playlist becuase the bookmark identifier
	is unknown.
	"""
	def test_add_playlist_bookmark_unknown_bookmark(self):
		# TODO
		pass
	
	"""Test that successfully adds a bookmark to and removes a bookmark from a
	playlist.
	"""
	def test_add_remove_playlist_bookmark(self):
		# TODO: test adding twice, removing twice
		pass
	
	"""Test that fails to add a bookmark to a playlist because the user identifier is
	not the playlist creator.
	"""
	def test_add_playlist_bookmark_wrong_user(self):
		# TODO
		pass

	"""Test that fails to remove a bookmark from a playlist because the user identifier
	is not the playlist creator.
	"""
	def test_remove_playlist_bookmark_wrong_user(self):
		# TODO
		pass

	"""Test that fails to vote a bookmark up or down because the user identifier is
	unknown.
	"""
	def test_vote_playlist_unknown_user(self):
		# TODO: test vote up, vote down, remove vote
		pass

	"""Test that fails to vote a playlist up or down because the playlist identifier
	is unknown.
	"""
	def test_vote_playlist_unknown_playlist(self):
		# TODO: test vote up, vote down, remove vote
		pass

	"""Test that successfully votes up a playlist.
	"""
	def test_up_vote_playlist(self):
		# TODO
		pass

	"""Test that successfully votes down a playlist.
	"""
	def test_down_vote_playlist(self):
		# TODO
		pass

	"""Test that successfully changes the vote of a playlist.
	"""
	def test_change_vote_playlist(self):
		# TODO
		pass


	# 
	# Begin tests for videos.
	# 

	"""Test that fails to return a displayed video because the video identifier is
	unknown.
	"""
	def test_get_displayed_video_unknown_video(self):
		# TODO
		pass

	"""Test that fails to create a bookmark because the user identifier is unknown.
	"""
	def test_create_bookmark_unknown_user(self):
		# TODO
		pass
	
	"""Test that fails to create a bookmark because the video identifier is unknown.
	"""
	def test_create_bookmark_unknown_video(self):
		# TODO
		pass

	"""Test that successfully creates and deletes a bookmark.
	"""
	def test_create_delete_bookmark(self):
		# TODO
		pass
	
	"""Test that fails to delete a bookmark that does not exist.
	"""
	def test_delete_missing_bookmark(self):
		# TODO: return success
		pass

	"""Test that fails to delete a bookmark because the user identifier is not
	the creator.
	"""
	def test_delete_bookmark_wrong_user(self):
		# TODO
		pass

	"""Test that fails to vote a bookmark up or down because the user identifier is
	unknown.
	"""
	def test_vote_bookmark_unknown_user(self):
		# TODO: test vote up, vote down, remove vote
		pass
	
	"""Test that fails to vote a bookmark up or down because the bookmark identifier is
	unknown.
	"""
	def test_vote_bookmark_unknown_bookmark(self):
		# TODO: test vote up, vote down, remove vote
		pass

	"""Test that successfully votes up a bookmark.
	"""
	def test_up_vote_bookmark(self):
		# test vote up, then vote up again, then remove
		# TODO
		pass

	"""Test that successfully votes down a bookmark.
	"""
	def test_down_vote_bookmark(self):
		# test vote down, then vote down again, then remove
		# TODO
		pass

	"""Test that successfully changes the vote of a bookmark.
	"""
	def test_change_vote_bookmark(self):
		# test vote up, then down, then up, then remove
		# TODO
		pass
	

if __name__ == '__main__':
	unittest.main()

