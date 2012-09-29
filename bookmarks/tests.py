from datetime import datetime, timedelta
import bookmarks_db
import unittest

class TestBookmarksDb(unittest.TestCase):
	"""Utility method for creating a user."""
	def _create_user(self, name):
		user = bookmarks_db.User(name, self.now)
		self.session.add(user)
		self.session.commit()
		return user.id

	"""Utility method for creating a video."""
	def _create_video(self, name, length):
		video = bookmarks_db.Video(name, length)
		self.session.add(video)
		self.session.commit()
		return video.id

	"""Utility method for creating a bookmark."""
	def _create_bookmark(self, user_id, video_id, comment, time):
		bookmark = bookmarks_db.Bookmark(
				comment, time, self.now, user_id=user_id, video_id=video_id)
		self.session.add(bookmark)
		self.session.commit()
		return bookmark.id

	def setUp(self):
		unittest.TestCase.setUp(self)
		self.now = datetime(2012, 10, 15, 12, 30, 45)
		self.session = bookmarks_db.session
		bookmarks_db.create_all()
	
	def tearDown(self):
		unittest.TestCase.tearDown(self)
		bookmarks_db.drop_all()
	
	"""Utility method to assert the fields in a DisplayedUser.
	"""
	def _assert_displayed_user(self, displayed_user, user_id, name, num_playlists=0):
		# Begin required arguments.
		self.assertIsNotNone(displayed_user)
		self.assertEqual(user_id, displayed_user.id)
		self.assertEqual(name, displayed_user.name)
		self.assertEqual(num_playlists, len(displayed_user.playlists))

	"""Utility method to assert the fields in a DisplayedUserPlaylist.
	"""
	def _assert_displayed_user_playlist(self,
			displayed_user_playlist, playlist_id, name, time_created,
			time_updated=None, num_thumbs_up=0, num_thumbs_down=0, user_vote=None, num_bookmarks=0):
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
		self.assertEqual(name, displayed_user_playlist.name)
		self.assertEqual(num_bookmarks, displayed_user_playlist.num_bookmarks)

	"""Utility method to assert the fields in a DisplayedPlaylist.
	"""
	def _assert_displayed_playlist(self,
			displayed_playlist, author_id, author_name, time_created, name,
			time_updated=None, num_thumbs_up=0, num_thumbs_down=0, user_vote=None,
			playlist_map={}, num_bookmarks=0):
		if time_updated is None:
			time_updated = time_created

		# Begin required arguments.
		self.assertIsNotNone(displayed_playlist)
		self.assertEqual(author_id, displayed_playlist.author_id)
		# XXX self.assertEqual(author_name, displayed_playlist.author_name)
		self.assertEqual(time_created, displayed_playlist.time_created)
		self.assertEqual(name, displayed_playlist.name)
		# Begin optional arguments.
		self.assertEqual(time_updated, displayed_playlist.time_updated)
		self.assertEqual(num_thumbs_up, displayed_playlist.num_thumbs_up)
		self.assertEqual(num_thumbs_down, displayed_playlist.num_thumbs_down)
		self.assertEqual(user_vote, displayed_playlist.user_vote)
		self.assertDictEqual(playlist_map, displayed_playlist.playlist_map)
		self.assertEqual(num_bookmarks, len(displayed_playlist.bookmarks))

	"""Utility method to assert the fields in a DisplayedPlaylistBookmark.
	"""
	def _assert_displayed_playlist_bookmark(self,
			displayed_playlist_bookmark, bookmark_id, video_name, comment,
			time_added, author_name, author_id,
			num_thumbs_up=0, num_thumbs_down=0, user_vote=None, playlist_ids=[]):
		# Begin required arguments.
		self.assertIsNotNone(displayed_playlist_bookmark)
		self.assertEqual(bookmark_id, displayed_playlist_bookmark.id)
		# self.assertEqual(video_name, displayed_playlist_bookmark.video_name)
		self.assertEqual(comment, displayed_playlist_bookmark.comment)
		self.assertEqual(time_added, displayed_playlist_bookmark.time_added)
		# self.assertEqual(author_name, displayed_playlist_bookmark.author_name)
		self.assertEqual(author_id, displayed_playlist_bookmark.author_id)
		# Begin optional arguments.
		self.assertEqual(num_thumbs_up, displayed_playlist_bookmark.num_thumbs_up)
		self.assertEqual(num_thumbs_down, displayed_playlist_bookmark.num_thumbs_down)
		# XXX self.assertEqual(user_vote, displayed_playlist_bookmark.user_vote)
		# XXX self.assertSequenceEqual(
		#		sorted(playlist_ids), sorted(displayed_playlist_bookmark.playlist_ids))

	"""Utility method to assert the fields in a DisplayedVideo.
	"""
	def _assert_displayed_video(self,
			displayed_video, name, length, playlist_map={}, num_bookmarks=0):
		# Begin required arguments.
		self.assertIsNotNone(displayed_video)
		self.assertEqual(name, displayed_video.name)
		self.assertEqual(length, displayed_video.length)
		# Begin optional arguments.
		self.assertDictEqual(playlist_map, displayed_video.playlist_map)
		self.assertEqual(num_bookmarks, len(displayed_video.bookmarks))

	"""Utility method to assert the fields in a DisplayedVideoBookmark.
	"""
	def _assert_displayed_video_bookmark(self,
			displayed_video_bookmark, bookmark_id, comment, time, time_created, author_name, author_id, 
			num_thumbs_up=0, num_thumbs_down=0, user_vote=None, playlist_ids=[]):
		# Begin required arguments.
		self.assertIsNotNone(displayed_video_bookmark)
		self.assertEqual(bookmark_id, displayed_video_bookmark.id)
		self.assertEqual(comment, displayed_video_bookmark.comment)
		self.assertEqual(time, displayed_video_bookmark.time)
		self.assertEqual(time_created, displayed_video_bookmark.time_created)
		"""
		self.assertEqual(author_name, displayed_video_bookmark.author_name)
		"""
		self.assertEqual(author_id, displayed_video_bookmark.author_id)
		# Begin optional arguments.
		self.assertEqual(num_thumbs_up, displayed_video_bookmark.num_thumbs_up)
		self.assertEqual(num_thumbs_down, displayed_video_bookmark.num_thumbs_down)
		self.assertEqual(user_vote, displayed_video_bookmark.user_vote)
		self.assertSequenceEqual(
				sorted(playlist_ids), sorted(displayed_video_bookmark.playlist_ids))

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
			bookmarks_db.create_playlist(missing_user_id, playlist_name, now=self.now)

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
		self._assert_displayed_user(displayed_user, user_id, user_name, num_playlists=1)
		# Assert that the created playlist was returned.
		displayed_user_playlist = displayed_user.playlists[0]
		self._assert_displayed_user_playlist(displayed_user_playlist,
				playlist_id, playlist_name, self.now)

		# Delete the playlist.
		bookmarks_db.delete_playlist(user_id, playlist_id)

		# Assert that the playlist is no longer returned.
		displayed_user = bookmarks_db.get_displayed_user(user_id)
		self._assert_displayed_user(displayed_user, user_id, user_name)

	"""Test that fails to delete a playlist that does not exist.
	"""
	def test_delete_missing_playlist(self):
		# Create a user.
		user_name = 'user_name1'
		user_id = self._create_user(user_name)
		# Delete a missing playlist.
		missing_playlist_id = 'missing_playlist_id'
		bookmarks_db.delete_playlist(user_id, missing_playlist_id)

		# Assert that this had no effect.
		displayed_user = bookmarks_db.get_displayed_user(user_id)
		self._assert_displayed_user(displayed_user, user_id, user_name)

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

		# Assert that this had no effect.
		displayed_user = bookmarks_db.get_displayed_user(user_id1)
		self._assert_displayed_user(displayed_user, user_id1, user_name1, num_bookmarks=1)
		displayed_user_playlist = displayed_user.bookmarks[0]
		self._assert_displayed_user_playlist(displayed_user_playlist,
				playlist_id, playlist_name, self.now)


	# 
	# Begin tests for playlists.
	# 

	"""Test that fails to return a displayed playlist because the playlist identifier
	is unknown.
	"""
	def test_get_displayed_playlist_unknown_playlist(self):
		missing_playlist_id = 'missing_playlist_id'
		with self.assertRaises(ValueError):
			bookmarks_db.get_displayed_playlist(missing_playlist_id)

	"""Test that fails to add a bookmark to a playlist because the user identifier
	is unknown.
	"""
	def test_add_playlist_bookmark_unknown_user(self):
		# Create a user with a playlist.
		user_name1 = 'user_name1'
		user_id1 = self._create_user(user_name1)
		playlist_name = 'playlist1'
		playlist_id = bookmarks_db.create_playlist(user_id1, playlist_name, now=self.now)
		# Create a video with a bookmark by another user.
		video_name = 'video1'
		video_length = 61
		video_id = self._create_video(video_name, video_length)
		user_name2 = 'user_name2'
		user_id2 = self._create_user(user_name2)
		bookmark_comment = 'comment1'
		bookmark_time = 33
		bookmark_id = self._create_bookmark(user_id2, video_id, bookmark_comment, bookmark_time)

		# Assert that adding the bookmark by a missing user fails.
		missing_user_id = 'missing_user_id'
		add_bookmark_time = self.now + timedelta(minutes=10)
		with self.assertRaises(ValueError):
			bookmarks_db.add_playlist_bookmark(
					missing_user_id, playlist_id, bookmark_id, now=add_bookmark_time)
		# Assert that this had no effect.
		displayed_playlist = bookmarks_db.get_displayed_playlist(playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_name)

	"""Test that fails to add a bookmark to a playlist because the playlist identifier
	is unknown.
	"""
	def test_add_playlist_bookmark_unknown_playlist(self):
		# Create a user without playlists.
		user_name1 = 'user_name1'
		user_id1 = self._create_user(user_name1)
		# Create a video with a bookmark by another user.
		video_name = 'video1'
		video_length = 61
		video_id = self._create_video(video_name, video_length)
		user_name2 = 'user_name2'
		user_id2 = self._create_user(user_name2)
		bookmark_comment = 'comment1'
		bookmark_time = 33
		bookmark_id = self._create_bookmark(user_id2, video_id, bookmark_comment, bookmark_time)

		# Assert that adding the bookmark to a missing playlist fails.
		missing_playlist_id = 'missing_playlist_id'
		with self.assertRaises(ValueError):
			bookmarks_db.add_playlist_bookmark(
					user_id1, missing_playlist_id, bookmark_id, now=self.now)
	
	"""Test that fails to add a bookmark to a playlist becuase the bookmark identifier
	is unknown.
	"""
	def test_add_playlist_bookmark_unknown_bookmark(self):
		# Create a user with a playlist.
		user_name1 = 'user_name1'
		user_id1 = self._create_user(user_name1)
		playlist_name = 'playlist1'
		playlist_id = bookmarks_db.create_playlist(user_id1, playlist_name, now=self.now)

		# Assert that adding a missing bookmark to a playlist fails.
		missing_bookmark_id = 'missing_bookmark_id'
		add_bookmark_time = self.now + timedelta(minutes=10)
		with self.assertRaises(ValueError):
			bookmarks_db.add_playlist_bookmark(
					user_id1, playlist_id, missing_bookmark_id, now=add_bookmark_time)
		# Assert that this had no effect.
		displayed_playlist = bookmarks_db.get_displayed_playlist(playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_name)
	
	"""Test that successfully adds a bookmark to and removes a bookmark from a
	playlist.
	"""
	def test_add_remove_playlist_bookmark(self):
		# Create a user with a playlist.
		user_name1 = 'user_name1'
		user_id1 = self._create_user(user_name1)
		playlist_name = 'playlist1'
		playlist_id = bookmarks_db.create_playlist(user_id1, playlist_name, now=self.now)
		# Create a video with a bookmark by another user.
		video_name = 'video1'
		video_length = 61
		video_id = self._create_video(video_name, video_length)
		user_name2 = 'user_name2'
		user_id2 = self._create_user(user_name2)
		bookmark_comment = 'comment1'
		bookmark_time = 33
		bookmark_id = self._create_bookmark(user_id2, video_id, bookmark_comment, bookmark_time)

		# Add the bookmark to the playlist.
		add_bookmark_time = self.now + timedelta(minutes=10)
		bookmarks_db.add_playlist_bookmark(user_id1, playlist_id, bookmark_id,
				now=add_bookmark_time)
		# Assert that the playlist has a bookmark.
		displayed_playlist = bookmarks_db.get_displayed_playlist(playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_name,
				time_updated=add_bookmark_time, num_bookmarks=1)
		# Assert that the bookmark is correct.
		displayed_playlist_bookmark = displayed_playlist.bookmarks[0]
		self._assert_displayed_playlist_bookmark(displayed_playlist_bookmark,
				bookmark_id, video_name, bookmark_comment, add_bookmark_time, user_name2, user_id2)

		# Add the bookmark to the playlist again.
		add_bookmark_again_time = self.now + timedelta(minutes=20)
		bookmarks_db.add_playlist_bookmark(user_id1, playlist_id, bookmark_id,
				now=add_bookmark_again_time)
		# Assert that this had no effect.
		displayed_playlist = bookmarks_db.get_displayed_playlist(playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_name,
				time_updated=add_bookmark_time, num_bookmarks=1)
		displayed_playlist_bookmark = displayed_playlist.bookmarks[0]
		self._assert_displayed_playlist_bookmark(displayed_playlist_bookmark,
				bookmark_id, video_name, bookmark_comment, add_bookmark_time, user_name2, user_id2)

		# Remove the bookmark from the playlist.
		remove_bookmark_time = self.now + timedelta(minutes=30)
		bookmarks_db.remove_playlist_bookmark(user_id1, playlist_id, bookmark_id,
				now=remove_bookmark_time)
		# Assert that the playlist has no bookmarks.
		displayed_playlist = bookmarks_db.get_displayed_playlist(playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_name,
				time_updated=remove_bookmark_time, num_bookmarks=0)

		# Remove the bookmark from the playlist again.
		remove_bookmark_again_time = self.now + timedelta(minutes=40)
		bookmarks_db.remove_playlist_bookmark(user_id1, playlist_id, bookmark_id,
				now=remove_bookmark_again_time)
		# Assert that this had no effect.
		displayed_playlist = bookmarks_db.get_displayed_playlist(playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_name,
				time_updated=remove_bookmark_time, num_bookmarks=0)

	"""Test that fails to add a bookmark to a playlist because the user identifier is
	not the playlist creator.
	"""
	def test_add_playlist_bookmark_wrong_user(self):
		# Create a user with a playlist.
		user_name1 = 'user_name1'
		user_id1 = self._create_user(user_name1)
		playlist_name = 'playlist1'
		playlist_id = bookmarks_db.create_playlist(user_id1, playlist_name, now=self.now)
		# Create a video with a bookmark by another user.
		video_name = 'video1'
		video_length = 61
		video_id = self._create_video(video_name, video_length)
		user_name2 = 'user_name2'
		user_id2 = self._create_user(user_name2)
		bookmark_comment = 'comment1'
		bookmark_time = 33
		bookmark_id = self._create_bookmark(user_id2, video_id, bookmark_comment, bookmark_time)

		# Assert that adding the bookmark by a user not the playlist creator fails.
		user_name3 = 'user_name3'
		user_id3 = self._create_user(user_name3)
		add_bookmark_time = self.now + timedelta(minutes=10)
		with self.assertRaises(ValueError):
			bookmarks_db.add_playlist_bookmark(user_id3, playlist_id, bookmark_id,
					now=add_bookmark_time)
		# Assert that this had no effect.
		displayed_playlist = bookmarks_db.get_displayed_playlist(playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_name)

	"""Test that fails to remove a bookmark from a playlist because the user identifier
	is not the playlist creator.
	"""
	def test_remove_playlist_bookmark_wrong_user(self):
		# Create a user with a playlist.
		user_name1 = 'user_name1'
		user_id1 = self._create_user(user_name1)
		playlist_name = 'playlist1'
		playlist_id = bookmarks_db.create_playlist(user_id1, playlist_name, now=self.now)
		# Create a video with a bookmark by another user.
		video_name = 'video1'
		video_length = 61
		video_id = self._create_video(video_name, video_length)
		user_name2 = 'user_name2'
		user_id2 = self._create_user(user_name2)
		bookmark_comment = 'comment1'
		bookmark_time = 33
		bookmark_id = self._create_bookmark(user_id2, video_id, bookmark_comment, bookmark_time)

		# Add the bookmark to the playlist.
		add_bookmark_time = self.now + timedelta(minutes=10)
		bookmarks_db.add_playlist_bookmark(user_id1, playlist_id, bookmark_id,
				now=add_bookmark_time)

		# Assert that removing the bookmark by a user not the playlist creator fails.
		user_name3 = 'user_name3'
		user_id3 = self._create_user(user_name3)
		remove_bookmark_time = self.now + timedelta(minutes=20)
		with self.assertRaises(ValueError):
			bookmarks_db.remove_playlist_bookmark(user_id3, playlist_id, bookmark_id,
					now=remove_bookmark_time)
		# Assert that this had no effect.
		displayed_playlist = bookmarks_db.get_displayed_playlist(playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_name,
				time_updated=add_bookmark_time, num_bookmarks=1)
		displayed_playlist_bookmark = displayed_playlist.bookmarks[0]
		self._assert_displayed_playlist_bookmark(displayed_playlist_bookmark,
				bookmark_id, video_name, bookmark_comment, self.now, user_name2, user_id2)

	"""Test that fails to vote a bookmark up or down because the user identifier is
	unknown.
	"""
	def test_vote_playlist_unknown_user(self):
		# Create a user with a playlist.
		user_name = 'user_name1'
		user_id = self._create_user(user_name)
		playlist_name = 'playlist1'
		playlist_id = bookmarks_db.create_playlist(user_id, playlist_name, now=self.now)
		
		missing_user_id = 'missing_user_id'

		# Assert that voting up the playlist with a missing user fails.
		with self.assertRaises(ValueError):
			bookmarks_db.vote_playlist_thumb_up(missing_user_id, playlist_id)
		# Assert that this had no effect.
		displayed_playlist = bookmarks_db.get_displayed_playlist(playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id, user_name, self.now, playlist_name)

		# Assert that voting down the playlist with a missing user fails.
		with self.assertRaises(ValueError):
			bookmarks_db.vote_playlist_thumb_down(missing_user_id, playlist_id)
		# Assert that this had no effect.
		displayed_playlist = bookmarks_db.get_displayed_playlist(playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id, user_name, self.now, playlist_name)

		# Assert that removing the playlist vote with a missing user fails.
		with self.assertRaises(ValueError):
			bookmarks_db.remove_playlist_vote(missing_user_id, playlist_id)
		# Assert that this had no effect.
		displayed_playlist = bookmarks_db.get_displayed_playlist(playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id, user_name, self.now, playlist_name)

	"""Test that fails to vote a bookmark up or down because the user identifier is
	the creator.
	"""
	def test_vote_playlist_by_creator(self):
		# Create a user with a playlist.
		user_name = 'user_name1'
		user_id = self._create_user(user_name)
		playlist_name = 'playlist1'
		playlist_id = bookmarks_db.create_playlist(user_id, playlist_name, now=self.now)
			
		# Assert that the creator voting up the playlist fails.
		with self.assertRaises(ValueError):
			bookmarks_db.vote_playlist_thumb_up(user_id, playlist_id)
		# Assert that this had no effect.
		displayed_playlist = bookmarks_db.get_displayed_playlist(playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id, user_name, self.now, playlist_name)

		# Assert that the creator voting down the playlist fails.
		with self.assertRaises(ValueError):
			bookmarks_db.vote_playlist_thumb_down(user_id, playlist_id)
		# Assert that this had no effect.
		displayed_playlist = bookmarks_db.get_displayed_playlist(playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id, user_name, self.now, playlist_name)

		# Assert that the creator removing the playlist vote fails.
		with self.assertRaises(ValueError):
			bookmarks_db.remove_playlist_vote(user_id, playlist_id)
		# Assert that this had no effect.
		displayed_playlist = bookmarks_db.get_displayed_playlist(playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id, user_name, self.now, playlist_name)

	"""Test that fails to vote a playlist up or down because the playlist identifier
	is unknown.
	"""
	def test_vote_playlist_unknown_playlist(self):
		# Create a user.
		user_name = 'user_name1'
		user_id = self._create_user(user_name)

		missing_playlist_id = 'missing_playlist_id'

		# Assert that voting up a missing playlist fails.
		with self.assertRaises(ValueError):
			bookmarks_db.vote_playlist_thumb_up(user_id, missing_playlist_id)
		# Assert that this had no effect.
		with self.assertRaises(ValueError):
			bookmarks_db.get_displayed_playlist(missing_playlist_id)

		# Assert that voting down a missing playlist fails.
		with self.assertRaises(ValueError):
			bookmarks_db.vote_playlist_thumb_down(user_id, missing_playlist_id)
		# Assert that this had no effect.
		with self.assertRaises(ValueError):
			bookmarks_db.get_displayed_playlist(missing_playlist_id)

		# Assert that removing the vote for a missing playlist fails.
		with self.assertRaises(ValueError):
			bookmarks_db.remove_playlist_vote(user_id, missing_playlist_id)
		# Assert that this had no effect.
		with self.assertRaises(ValueError):
			bookmarks_db.get_displayed_playlist(missing_playlist_id)

	"""Test that successfully votes up a playlist.
	"""
	def test_up_vote_playlist(self):
		# Create a user with a playlist.
		user_name1 = 'user_name1'
		user_id1 = self._create_user(user_name1)
		playlist_name = 'playlist1'
		playlist_id = bookmarks_db.create_playlist(user_id1, playlist_name, now=self.now)
		# Create another user to vote up the playlist.
		user_name2 = 'user_name2'
		user_id2 = self._create_user(user_name2)

		# Vote up the playlist.
		bookmarks_db.vote_playlist_thumb_up(user_id2, playlist_id, now=self.now)
		# Assert that the playlist has been voted on.
		displayed_playlist = bookmarks_db.get_displayed_playlist(playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_name, num_thumbs_up=1)

		# Vote up the playlist again.
		bookmarks_db.vote_playlist_thumb_up(user_id2, playlist_id)
		# Assert that this had no effect.
		displayed_playlist = bookmarks_db.get_displayed_playlist(playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_name, num_thumbs_up=1)

		# Remove the vote for the playlist.
		bookmarks_db.remove_playlist_vote(user_id2, playlist_id)
		# Assert that the playlist is no longer voted on.
		displayed_playlist = bookmarks_db.get_displayed_playlist(playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_name)

		# Remove the vote for the playlist again.
		bookmarks_db.remove_playlist_vote(user_id2, playlist_id)
		# Assert that this had no effect.
		displayed_playlist = bookmarks_db.get_displayed_playlist(playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_name)

	"""Test that successfully votes down a playlist.
	"""
	def test_down_vote_playlist(self):
		# Create a user with a playlist.
		user_name1 = 'user_name1'
		user_id1 = self._create_user(user_name1)
		playlist_name = 'playlist1'
		playlist_id = bookmarks_db.create_playlist(user_id1, playlist_name, now=self.now)
		# Create another user to vote down the playlist.
		user_name2 = 'user_name2'
		user_id2 = self._create_user(user_name2)

		# Vote down the playlist.
		bookmarks_db.vote_playlist_thumb_down(user_id2, playlist_id, now=self.now)
		# Assert that the playlist has been voted on.
		displayed_playlist = bookmarks_db.get_displayed_playlist(playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_name, num_thumbs_down=1)

		# Vote down the playlist again.
		bookmarks_db.vote_playlist_thumb_down(user_id2, playlist_id)
		# Assert that this had no effect.
		displayed_playlist = bookmarks_db.get_displayed_playlist(playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_name, num_thumbs_down=1)

		# Remove the vote for the playlist.
		bookmarks_db.remove_playlist_vote(user_id2, playlist_id)
		# Assert that the playlist is no longer voted on.
		displayed_playlist = bookmarks_db.get_displayed_playlist(playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_name)

		# Remove the vote for the playlist again.
		bookmarks_db.remove_playlist_vote(user_id2, playlist_id)
		# Assert that this had no effect.
		displayed_playlist = bookmarks_db.get_displayed_playlist(playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_name)

	"""Test that successfully changes the vote of a playlist.
	"""
	def test_change_vote_playlist(self):
		# Create a user with a playlist.
		user_name1 = 'user_name1'
		user_id1 = self._create_user(user_name1)
		playlist_name = 'playlist1'
		playlist_id = bookmarks_db.create_playlist(user_id1, playlist_name, now=self.now)
		# Create another user to vote on the playlist.
		user_name2 = 'user_name2'
		user_id2 = self._create_user(user_name2)

		# Vote up the playlist.
		bookmarks_db.vote_playlist_thumb_up(user_id2, playlist_id, now=self.now)
		# Assert that the playlist has been voted on.
		displayed_playlist = bookmarks_db.get_displayed_playlist(playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_name, num_thumbs_up=1)

		# Vote down the playlist.
		bookmarks_db.vote_playlist_thumb_down(user_id2, playlist_id, now=self.now)
		# Assert that the playlist has been voted on.
		displayed_playlist = bookmarks_db.get_displayed_playlist(playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_name, num_thumbs_down=1)

		# Vote up the playlist again.
		bookmarks_db.vote_playlist_thumb_up(user_id2, playlist_id, now=self.now)
		# Assert that the playlist has been voted on.
		displayed_playlist = bookmarks_db.get_displayed_playlist(playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_name, num_thumbs_up=1)

		# Remove the vote for the playlist.
		bookmarks_db.remove_playlist_vote(user_id2, playlist_id)
		# Assert that the playlist is no longer voted on.
		displayed_playlist = bookmarks_db.get_displayed_playlist(playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_name)

	# 
	# Begin tests for videos.
	# 

	"""Test that fails to return a displayed video because the video identifier is
	unknown.
	"""
	def test_get_displayed_video_unknown_video(self):
		# TODO: actually, this should implicitly create the video
		pass

	"""Test that fails to create a bookmark because the user identifier is unknown.
	"""
	def test_create_bookmark_unknown_user(self):
		# Create a video.
		video_name = 'video1'
		video_length = 61
		video_id = self._create_video(video_name, video_length)

		# Assert that creating a bookmark by a missing user fails.
		bookmark_comment = 'comment1'
		bookmark_time = 33
		missing_user_id = 'missing_user_id'
		with self.assertRaises(ValueError):
			bookmarks_db.add_video_bookmark(missing_user_id, video_id,
					bookmark_comment, bookmark_time, now=self.now)
		# Assert that this had no effect.
		displayed_video = bookmarks_db.get_displayed_video(video_id)
		self._assert_displayed_video(displayed_video, video_name, video_length)
	
	"""Test that fails to create a bookmark because the video identifier is unknown.
	"""
	def test_create_bookmark_unknown_video(self):
		# Create a user.
		user_name = 'user_name1'
		user_id = self._create_user(user_name)

		# Assert that creating a bookmark for a missing video fails.
		bookmark_comment = 'comment1'
		bookmark_time = 33
		missing_video_id = 'missing_video_id'
		with self.assertRaises(ValueError):
			bookmarks_db.add_video_bookmark(user_id, missing_video_id,
					bookmark_comment, bookmark_time, now=self.now)

	"""Test that successfully creates and deletes a bookmark.
	"""
	def test_create_delete_bookmark(self):
		# Create a user.
		user_name = 'user_name1'
		user_id = self._create_user(user_name)
		# Create a video.
		video_name = 'video1'
		video_length = 61
		video_id = self._create_video(video_name, video_length)

		# Add the bookmark to the video.
		add_bookmark_time = self.now + timedelta(minutes=10)
		bookmark_comment = 'comment1'
		bookmark_time = 33
		bookmark_id = bookmarks_db.add_video_bookmark(
				user_id, video_id, bookmark_comment, bookmark_time, now=add_bookmark_time)
		# Assert that the video has a bookmark.
		displayed_video = bookmarks_db.get_displayed_video(video_id)
		self._assert_displayed_video(displayed_video,
				video_name, video_length, num_bookmarks=1)
		# Assert that the bookmark is correct.
		displayed_video_bookmark = displayed_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, add_bookmark_time,
				user_name, user_id)

		# Remove the bookmark from the video.
		remove_bookmark_time = self.now + timedelta(minutes=20)
		bookmarks_db.remove_video_bookmark(user_id, bookmark_id, now=remove_bookmark_time)
		# Assert that the video has no bookmarks.
		displayed_video = bookmarks_db.get_displayed_video(video_id)
		self._assert_displayed_video(displayed_video, video_name, video_length)

		# Remove the bookmark from the video again.
		remove_bookmark_again_time = self.now + timedelta(minutes=30)
		bookmarks_db.remove_video_bookmark(
				user_id, bookmark_id, now=remove_bookmark_again_time)
		# Assert that this had no effect.
		displayed_video = bookmarks_db.get_displayed_video(video_id)
		self._assert_displayed_video(displayed_video, video_name, video_length)
	
	"""Test that fails to delete a bookmark that does not exist.
	"""
	def test_delete_missing_bookmark(self):
		# Create a user.
		user_name = 'user_name1'
		user_id = self._create_user(user_name)
		# Create a video.
		video_name = 'video1'
		video_length = 61
		video_id = self._create_video(video_name, video_length)
		# Delete a missing bookmark.
		remove_bookmark_time = self.now + timedelta(minutes=10)
		missing_bookmark_id = 'missing_bookmark_id'
		bookmarks_db.remove_video_bookmark(
				user_id, missing_bookmark_id, now=remove_bookmark_time)

		# Assert that this had no effect.
		displayed_video = bookmarks_db.get_displayed_video(video_id)
		self._assert_displayed_video(displayed_video, video_name, video_length)

	"""Test that fails to delete a bookmark because the user identifier is not
	the creator.
	"""
	def test_delete_bookmark_wrong_user(self):
		# Create a video with a bookmark by a user.
		video_name = 'video1'
		video_length = 61
		video_id = self._create_video(video_name, video_length)
		user_name1 = 'user_name1'
		user_id1 = self._create_user(user_name1)
		bookmark_comment = 'comment1'
		bookmark_time = 33
		bookmark_id = self._create_bookmark(user_id1, video_id, bookmark_comment, bookmark_time)

		# Assert that a user removing the bookmark who is not the creator fails.
		user_name2 = 'user_name2'
		user_id2 = self._create_user(user_name2)
		remove_bookmark_time = self.now + timedelta(minutes=10)
		with self.assertRaises(ValueError):
			bookmarks_db.remove_video_bookmark(
					user_id2, bookmark_id, now=remove_bookmark_time)

		# Assert that this had no effect.
		displayed_video = bookmarks_db.get_displayed_video(video_id)
		self._assert_displayed_video(displayed_video,
				video_name, video_length, num_bookmarks=1)
		displayed_video_bookmark = displayed_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name1, user_id1)

	"""Test that fails to vote a bookmark up or down because the user identifier is
	unknown.
	"""
	def test_vote_bookmark_unknown_user(self):
		# Create a video with a bookmark by a user.
		video_name = 'video1'
		video_length = 61
		video_id = self._create_video(video_name, video_length)
		user_name = 'user_name1'
		user_id = self._create_user(user_name)
		bookmark_comment = 'comment1'
		bookmark_time = 33
		bookmark_id = self._create_bookmark(user_id, video_id, bookmark_comment, bookmark_time)

		missing_user_id = 'missing_user_id'

		# Assert that voting up the bookmark with a missing user fails.
		with self.assertRaises(ValueError):
			bookmarks_db.vote_bookmark_thumb_up(missing_user_id, bookmark_id)
		# Assert that this had no effect.
		displayed_video = bookmarks_db.get_displayed_video(video_id)
		self._assert_displayed_video(displayed_video,
				video_name, video_length, num_bookmarks=1)
		displayed_video_bookmark = displayed_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name, user_id)

		# Assert that voting up the bookmark with a missing user fails.
		with self.assertRaises(ValueError):
			bookmarks_db.vote_bookmark_thumb_down(missing_user_id, bookmark_id)
		# Assert that this had no effect.
		displayed_video = bookmarks_db.get_displayed_video(video_id)
		self._assert_displayed_video(displayed_video,
				video_name, video_length, num_bookmarks=1)
		displayed_video_bookmark = displayed_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name, user_id)

		# Assert that removing the bookmark vote with a missing user fails.
		with self.assertRaises(ValueError):
			bookmarks_db.remove_bookmark_vote(missing_user_id, bookmark_id)
		# Assert that this had no effect.
		displayed_video = bookmarks_db.get_displayed_video(video_id)
		self._assert_displayed_video(displayed_video,
				video_name, video_length, num_bookmarks=1)
		displayed_video_bookmark = displayed_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name, user_id)
	
	"""Test that fails to vote a bookmark up or down because the user identifier is
	the creator.
	"""
	def test_vote_bookmark_by_creator(self):
		# Create a video with a bookmark by a user.
		video_name = 'video1'
		video_length = 61
		video_id = self._create_video(video_name, video_length)
		user_name = 'user_name1'
		user_id = self._create_user(user_name)
		bookmark_comment = 'comment1'
		bookmark_time = 33
		bookmark_id = self._create_bookmark(user_id, video_id, bookmark_comment, bookmark_time)

		# Assert that the creator voting up the bookmark fails.
		with self.assertRaises(ValueError):
			bookmarks_db.vote_bookmark_thumb_up(user_id, bookmark_id)
		# Assert that this had no effect.
		displayed_video = bookmarks_db.get_displayed_video(video_id)
		self._assert_displayed_video(displayed_video,
				video_name, video_length, num_bookmarks=1)
		displayed_video_bookmark = displayed_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name, user_id)

		# Assert that the creator voting up the bookmark fails.
		with self.assertRaises(ValueError):
			bookmarks_db.vote_bookmark_thumb_down(user_id, bookmark_id)
		# Assert that this had no effect.
		displayed_video = bookmarks_db.get_displayed_video(video_id)
		self._assert_displayed_video(displayed_video,
				video_name, video_length, num_bookmarks=1)
		displayed_video_bookmark = displayed_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name, user_id)

		# Assert that the creator removing the bookmark vote fails.
		with self.assertRaises(ValueError):
			bookmarks_db.remove_bookmark_vote(user_id, bookmark_id)
		# Assert that this had no effect.
		displayed_video = bookmarks_db.get_displayed_video(video_id)
		self._assert_displayed_video(displayed_video,
				video_name, video_length, num_bookmarks=1)
		displayed_video_bookmark = displayed_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name, user_id)

	"""Test that fails to vote a bookmark up or down because the bookmark identifier is
	unknown.
	"""
	def test_vote_bookmark_unknown_bookmark(self):
		# Create a user.
		user_name = 'user_name1'
		user_id = self._create_user(user_name)

		missing_bookmark_id = 'missing_bookmark_id'

		# Assert that voting up a missing bookmark fails.
		with self.assertRaises(ValueError):
			bookmarks_db.vote_bookmark_thumb_up(user_id, missing_bookmark_id)

		# Assert that voting down a missing bookmark fails.
		with self.assertRaises(ValueError):
			bookmarks_db.vote_bookmark_thumb_down(user_id, missing_bookmark_id)

		# Assert that removing the vote for a missing bookmark fails.
		with self.assertRaises(ValueError):
			bookmarks_db.remove_bookmark_vote(user_id, missing_bookmark_id)

	"""Test that successfully votes up a bookmark.
	"""
	def test_up_vote_bookmark(self):
		# Create a video with a bookmark by a user.
		video_name = 'video1'
		video_length = 61
		video_id = self._create_video(video_name, video_length)
		user_name1 = 'user_name1'
		user_id1 = self._create_user(user_name1)
		bookmark_comment = 'comment1'
		bookmark_time = 33
		bookmark_id = self._create_bookmark(user_id1, video_id, bookmark_comment, bookmark_time)
		# Create another user to vote up the bookmark.
		user_name2 = 'user_name2'
		user_id2 = self._create_user(user_name2)

		# Vote up the bookmark.
		bookmarks_db.vote_bookmark_thumb_up(user_id2, bookmark_id, now=self.now)
		# Assert that the bookmark has been voted on.
		displayed_video = bookmarks_db.get_displayed_video(video_id)
		self._assert_displayed_video(displayed_video,
				video_name, video_length, num_bookmarks=1)
		displayed_video_bookmark = displayed_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name1, user_id1, num_thumbs_up=1)

		# Vote up the bookmark again.
		bookmarks_db.vote_bookmark_thumb_up(user_id2, bookmark_id, now=self.now)
		# Assert that this had no effect.
		displayed_video = bookmarks_db.get_displayed_video(video_id)
		self._assert_displayed_video(displayed_video,
				video_name, video_length, num_bookmarks=1)
		displayed_video_bookmark = displayed_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name1, user_id1, num_thumbs_up=1)

		# Remove the vote for the bookmark.
		bookmarks_db.remove_bookmark_vote(user_id2, bookmark_id)
		# Assert that the bookmark is no longer voted on.
		displayed_video = bookmarks_db.get_displayed_video(video_id)
		self._assert_displayed_video(displayed_video,
				video_name, video_length, num_bookmarks=1)
		displayed_video_bookmark = displayed_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name1, user_id1)

		# Remove the vote for the bookmark again.
		bookmarks_db.remove_bookmark_vote(user_id2, bookmark_id)
		# Assert that this had no effect.
		displayed_video = bookmarks_db.get_displayed_video(video_id)
		self._assert_displayed_video(displayed_video,
				video_name, video_length, num_bookmarks=1)
		displayed_video_bookmark = displayed_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name1, user_id1)

	"""Test that successfully votes down a bookmark.
	"""
	def test_down_vote_bookmark(self):
		# Create a video with a bookmark by a user.
		video_name = 'video1'
		video_length = 61
		video_id = self._create_video(video_name, video_length)
		user_name1 = 'user_name1'
		user_id1 = self._create_user(user_name1)
		bookmark_comment = 'comment1'
		bookmark_time = 33
		bookmark_id = self._create_bookmark(user_id1, video_id, bookmark_comment, bookmark_time)
		# Create another user to vote down the bookmark.
		user_name2 = 'user_name2'
		user_id2 = self._create_user(user_name2)

		# Vote down the bookmark.
		bookmarks_db.vote_bookmark_thumb_down(user_id2, bookmark_id, now=self.now)
		# Assert that the bookmark has been voted on.
		displayed_video = bookmarks_db.get_displayed_video(video_id)
		self._assert_displayed_video(displayed_video,
				video_name, video_length, num_bookmarks=1)
		displayed_video_bookmark = displayed_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name1, user_id1, num_thumbs_down=1)

		# Vote down the bookmark again.
		bookmarks_db.vote_bookmark_thumb_down(user_id2, bookmark_id, now=self.now)
		# Assert that this had no effect.
		displayed_video = bookmarks_db.get_displayed_video(video_id)
		self._assert_displayed_video(displayed_video,
				video_name, video_length, num_bookmarks=1)
		displayed_video_bookmark = displayed_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name1, user_id1, num_thumbs_down=1)

		# Remove the vote for the bookmark.
		bookmarks_db.remove_bookmark_vote(user_id2, bookmark_id)
		# Assert that the bookmark is no longer voted on.
		displayed_video = bookmarks_db.get_displayed_video(video_id)
		self._assert_displayed_video(displayed_video,
				video_name, video_length, num_bookmarks=1)
		displayed_video_bookmark = displayed_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name1, user_id1)

		# Remove the vote for the bookmark again.
		bookmarks_db.remove_bookmark_vote(user_id2, bookmark_id)
		# Assert that this had no effect.
		displayed_video = bookmarks_db.get_displayed_video(video_id)
		self._assert_displayed_video(displayed_video,
				video_name, video_length, num_bookmarks=1)
		displayed_video_bookmark = displayed_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name1, user_id1)

	"""Test that successfully changes the vote of a bookmark.
	"""
	def test_change_vote_bookmark(self):
		# Create a video with a bookmark by a user.
		video_name = 'video1'
		video_length = 61
		video_id = self._create_video(video_name, video_length)
		user_name1 = 'user_name1'
		user_id1 = self._create_user(user_name1)
		bookmark_comment = 'comment1'
		bookmark_time = 33
		bookmark_id = self._create_bookmark(user_id1, video_id, bookmark_comment, bookmark_time)
		# Create another user to vote on the bookmark.
		user_name2 = 'user_name2'
		user_id2 = self._create_user(user_name2)

		# Vote up the bookmark.
		bookmarks_db.vote_bookmark_thumb_up(user_id2, bookmark_id, now=self.now)
		# Assert that the bookmark has been voted on.
		displayed_video = bookmarks_db.get_displayed_video(video_id)
		self._assert_displayed_video(displayed_video,
				video_name, video_length, num_bookmarks=1)
		displayed_video_bookmark = displayed_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name1, user_id1, num_thumbs_up=1)

		# Vote down the bookmark.
		bookmarks_db.vote_bookmark_thumb_down(user_id2, bookmark_id, now=self.now)
		# Assert that the bookmark has been voted on.
		displayed_video = bookmarks_db.get_displayed_video(video_id)
		self._assert_displayed_video(displayed_video,
				video_name, video_length, num_bookmarks=1)
		displayed_video_bookmark = displayed_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name1, user_id1, num_thumbs_down=1)

		# Vote up the bookmark again.
		bookmarks_db.vote_bookmark_thumb_up(user_id2, bookmark_id, now=self.now)
		# Assert that the bookmark has been voted on.
		displayed_video = bookmarks_db.get_displayed_video(video_id)
		self._assert_displayed_video(displayed_video,
				video_name, video_length, num_bookmarks=1)
		displayed_video_bookmark = displayed_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name1, user_id1, num_thumbs_up=1)

		# Remove the vote for the bookmark.
		bookmarks_db.remove_bookmark_vote(user_id2, bookmark_id)
		# Assert that the bookmark is no longer voted on.
		displayed_video = bookmarks_db.get_displayed_video(video_id)
		self._assert_displayed_video(displayed_video,
				video_name, video_length, num_bookmarks=1)
		displayed_video_bookmark = displayed_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name1, user_id1)


if __name__ == '__main__':
	unittest.main()

