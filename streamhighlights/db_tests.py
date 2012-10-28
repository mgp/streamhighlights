from datetime import timedelta
import db
from db_test_case import DbTestCase
import unittest


class TestBookmarksDb(DbTestCase):
	def test_add_twitch_video(self):
		title = 'title_value'
		length = 33
		archive_id = 'archive_id_value'
		video_file_url = 'video_file_value'
		link_url = 'link_url_value'

		db.add_twitch_video(title, length, archive_id, video_file_url, link_url)
		# TODO: Assert the video can be retrieved.

	#
	# Begin tests for users.
	# 

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

		# Get the Twitch user.
		displayed_twitch_user = db.get_displayed_twitch_user(None, twitch_id)
		# Assert that the created Twitch user was returned.
		expected_link_url = 'http://www.twitch.tv/%s' % name
		self._assert_displayed_twitch_user(displayed_twitch_user,
				user_id, display_name, twitch_id, expected_link_url, image_url_large=logo)

		# TODO: Read from DB, assert created, last_seen

		# Update the Twitch user.
		updated_name = 'updated_name'
		updated_display_name = 'updated_display_name'
		updated_logo = 'updated_logo_url'
		updated_access_token = 'updated_access_token'
		updated_time = self.now + timedelta(minutes=10)
		updated_user_id = db.twitch_user_logged_in(
				twitch_id, updated_name, updated_display_name,
				updated_logo, updated_access_token, updated_time)
		self.assertEqual(updated_user_id, user_id)

		# Get the Twitch user.
		displayed_twitch_user = db.get_displayed_twitch_user(None, twitch_id)
		# Assert that the updated Twitch user was returned.
		updated_expected_link_url = 'http://www.twitch.tv/%s' % updated_name
		self._assert_displayed_twitch_user(displayed_twitch_user,
				user_id, updated_display_name, twitch_id,
				updated_expected_link_url, image_url_large=updated_logo)

		# TODO: Read from DB, assert created, last_seen

	def test_steam_user_logged_in(self):
		# Create a new Steam user.
		steam_id = 456
		personaname = 'personaname'
		profile_url = 'profile_url'
		avatar = 'avatar'
		avatar_full = 'avatar_full'
		user_id = db.steam_user_logged_in(
				steam_id, personaname, profile_url, avatar, avatar_full, self.now)
		self.assertIsNotNone(user_id)

		# Get the Steam user.
		displayed_steam_user = db.get_displayed_steam_user(None, steam_id)
		# Assert that the created Steam user was returned.
		self._assert_displayed_steam_user(displayed_steam_user,
				user_id, personaname, steam_id, profile_url,
				image_url_small=avatar, image_url_large=avatar_full)

		# TODO: Read from DB, assert created, last_seen

		# Update the Steam user.
		updated_personaname = 'updated_personaname'
		updated_profile_url = 'updated_profile_url'
		updated_avatar = 'updated_avatar'
		updated_avatar_full = 'updated_avatar_full'
		updated_time = self.now + timedelta(minutes=10)
		updated_user_id = db.steam_user_logged_in(
				steam_id, updated_personaname,
				updated_profile_url, updated_avatar, updated_avatar_full, updated_time)
		self.assertEqual(updated_user_id, user_id)

		# Get the Steam user.
		displayed_steam_user = db.get_displayed_steam_user(None, steam_id)
		# Assert that the updated Steam user was returned.
		self._assert_displayed_steam_user(displayed_steam_user,
				user_id, updated_personaname, steam_id, updated_profile_url,
				image_url_small=updated_avatar, image_url_large=updated_avatar_full)

		# TODO: Read from DB, assert created, last_seen

	"""Test that fails to return a displayed Twitch user because the Twitch user
	identifier is unknown.
	"""
	def test_get_displayed_twitch_user_unknown_user(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		missing_twitch_id = 'missing_twitch_id'
		with self.assertRaises(db.DbException):
			db.get_displayed_twitch_user(client_id, missing_twitch_id)

	"""Test that fails to return a displayed Steam user because the Steam user
	identifier is unknown.
	"""
	def test_get_displayed_steam_user_unknown_user(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		missing_steam_id = 'missing_steam_id'
		with self.assertRaises(db.DbException):
			db.get_displayed_steam_user(client_id, missing_steam_id)

	"""Test that fails to create a playlist because the user identifier is unknown.
	"""
	def test_create_playlist_unknown_user(self):
		missing_user_id = 'missing_user_id'
		playlist_title = 'playlist1'
		with self.assertRaises(db.DbException):
			db.create_playlist(missing_user_id, playlist_title, now=self.now)

	"""Test that successfully creates and deletes a bookmark.
	"""
	def test_create_remove_playlist(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		# Create a playlist for a user.
		user_name = 'user_name1'
		user_steam_id, user_id = self._create_steam_user(user_name)
		playlist_title = 'playlist1'
		playlist_id = db.create_playlist(user_id, playlist_title, now=self.now)

		# Get the displayed user.
		displayed_user = db.get_displayed_user(client_id, user_id)
		self._assert_displayed_user(displayed_user, user_id, user_name, num_playlists=1)
		# Assert that the created playlist was returned.
		displayed_user_playlist = displayed_user.playlists[0]
		self._assert_displayed_user_playlist(displayed_user_playlist,
				playlist_id, playlist_title, self.now)

		# Delete the playlist.
		db.remove_playlist(user_id, playlist_id)

		# Assert that the playlist is no longer returned.
		displayed_user = db.get_displayed_user(client_id, user_id)
		self._assert_displayed_user(displayed_user, user_id, user_name)

	"""Test that fails to delete a playlist that does not exist.
	"""
	def test_delete_missing_playlist(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		# Create a user.
		user_name = 'user_name1'
		user_steam_id, user_id = self._create_steam_user(user_name)
		# Delete a missing playlist.
		missing_playlist_id = 'missing_playlist_id'
		with self.assertRaises(db.DbException):
			db.remove_playlist(user_id, missing_playlist_id)

		# Assert that this had no effect.
		displayed_user = db.get_displayed_user(client_id, user_id)
		self._assert_displayed_user(displayed_user, user_id, user_name)

	"""Test that fails to delete a playlist because the user identifier is not the
	creator.
	"""
	def test_remove_playlist_wrong_user(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		# Create a playlist for a user.
		user_name1 = 'user_name1'
		user_steam_id1, user_id1 = self._create_steam_user(user_name1)
		playlist_title = 'playlist1'
		playlist_id = db.create_playlist(user_id1, playlist_title, now=self.now)
		# Create another user.
		user_name2 = 'user_name2'
		user_steam_id2, user_id2 = self._create_steam_user(user_name2)

		# Attempt to delete the playlist with another user.
		with self.assertRaises(db.DbException):
			db.remove_playlist(user_id2, playlist_id)

		# Assert that this had no effect.
		displayed_user = db.get_displayed_user(client_id, user_id1)
		self._assert_displayed_user(displayed_user, user_id1, user_name1, num_playlists=1)
		displayed_user_playlist = displayed_user.playlists[0]
		self._assert_displayed_user_playlist(displayed_user_playlist,
				playlist_id, playlist_title, self.now)


	# 
	# Begin tests for playlists.
	# 

	"""Test that fails to return a displayed playlist because the playlist identifier
	is unknown.
	"""
	def test_get_displayed_playlist_unknown_playlist(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		missing_playlist_id = 'missing_playlist_id'
		with self.assertRaises(db.DbException):
			db.get_displayed_playlist(client_id, missing_playlist_id)

	"""Test that fails to add a bookmark to a playlist because the user identifier
	is unknown.
	"""
	def test_add_playlist_bookmark_unknown_user(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		# Create a user with a playlist.
		user_name1 = 'user_name1'
		user_steam_id1, user_id1 = self._create_steam_user(user_name1)
		playlist_title = 'playlist1'
		playlist_id = db.create_playlist(user_id1, playlist_title, now=self.now)
		# Create a video.
		video_title = 'video1'
		video_length = 61
		archive_id = 'archive_id1'
		video_file_url = 'video_file_url1'
		link_url = 'link_url1'
		video_id = db.add_twitch_video(
				video_title, video_length, archive_id, video_file_url, link_url)
		# Create a bookmark for that video by another user.
		user_name2 = 'user_name2'
		user_steam_id2, user_id2 = self._create_steam_user(user_name2)
		bookmark_comment = 'comment1'
		bookmark_time = 33
		bookmark_id = db.add_video_bookmark(
				user_id2, video_id, bookmark_comment, bookmark_time, self.now)

		# Assert that adding the bookmark by a missing user fails.
		missing_user_id = 'missing_user_id'
		add_bookmark_time = self.now + timedelta(minutes=10)
		with self.assertRaises(db.DbException):
			db.add_playlist_bookmark(
					missing_user_id, playlist_id, bookmark_id, now=add_bookmark_time)
		# Assert that this had no effect.
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_title)

	"""Test that fails to add a bookmark to a playlist because the playlist identifier
	is unknown.
	"""
	def test_add_playlist_bookmark_unknown_playlist(self):
		# Create a user without playlists.
		user_name1 = 'user_name1'
		user_steam_id1, user_id1 = self._create_steam_user(user_name1)
		# Create a video with a bookmark.
		video_title = 'video1'
		video_length = 61
		archive_id = 'archive_id1'
		video_file_url = 'video_file_url1'
		link_url = 'link_url1'
		video_id = db.add_twitch_video(
				video_title, video_length, archive_id, video_file_url, link_url)
		# Create a bookmark for that video by another user.
		user_name2 = 'user_name2'
		user_steam_id2, user_id2 = self._create_steam_user(user_name2)
		bookmark_comment = 'comment1'
		bookmark_time = 33
		bookmark_id = db.add_video_bookmark(
				user_id2, video_id, bookmark_comment, bookmark_time, self.now)

		# Assert that adding the bookmark to a missing playlist fails.
		missing_playlist_id = 'missing_playlist_id'
		with self.assertRaises(db.DbException):
			db.add_playlist_bookmark(
					user_id1, missing_playlist_id, bookmark_id, now=self.now)
	
	"""Test that fails to add a bookmark to a playlist becuase the bookmark identifier
	is unknown.
	"""
	def test_add_playlist_bookmark_unknown_bookmark(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		# Create a user with a playlist.
		user_name1 = 'user_name1'
		user_steam_id1, user_id1 = self._create_steam_user(user_name1)
		playlist_title = 'playlist1'
		playlist_id = db.create_playlist(user_id1, playlist_title, now=self.now)

		# Assert that adding a missing bookmark to a playlist fails.
		missing_bookmark_id = 'missing_bookmark_id'
		add_bookmark_time = self.now + timedelta(minutes=10)
		with self.assertRaises(db.DbException):
			db.add_playlist_bookmark(
					user_id1, playlist_id, missing_bookmark_id, now=add_bookmark_time)
		# Assert that this had no effect.
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_title)
	
	"""Test that successfully adds a bookmark to and removes a bookmark from a
	playlist.
	"""
	def test_add_remove_playlist_bookmark(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		# Create a user with a playlist.
		user_name1 = 'user_name1'
		user_steam_id1, user_id1 = self._create_steam_user(user_name1)
		playlist_title = 'playlist1'
		playlist_id = db.create_playlist(user_id1, playlist_title, now=self.now)
		# Create a video.
		video_title = 'video1'
		video_length = 61
		archive_id = 'archive_id1'
		video_file_url = 'video_file_url1'
		link_url = 'link_url1'
		video_id = db.add_twitch_video(
				video_title, video_length, archive_id, video_file_url, link_url)
		# Create a bookmark for that video by another user.
		user_name2 = 'user_name2'
		user_steam_id2, user_id2 = self._create_steam_user(user_name2)
		bookmark_comment = 'comment1'
		bookmark_time = 33
		bookmark_id = db.add_video_bookmark(
				user_id2, video_id, bookmark_comment, bookmark_time, self.now)

		# Add the bookmark to the playlist.
		add_bookmark_time = self.now + timedelta(minutes=10)
		db.add_playlist_bookmark(user_id1, playlist_id, bookmark_id,
				now=add_bookmark_time)
		# Assert that the playlist has a bookmark.
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_title,
				time_updated=add_bookmark_time, num_bookmarks=1)
		# Assert that the bookmark is correct.
		displayed_playlist_bookmark = displayed_playlist.bookmarks[0]
		self._assert_displayed_playlist_bookmark(displayed_playlist_bookmark,
				bookmark_id, video_title, bookmark_comment, add_bookmark_time,
				user_name2, user_id2)

		# Add the bookmark to the playlist again.
		add_bookmark_again_time = self.now + timedelta(minutes=20)
		db.add_playlist_bookmark(user_id1, playlist_id, bookmark_id,
				now=add_bookmark_again_time)
		# Assert that this had no effect.
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_title,
				time_updated=add_bookmark_time, num_bookmarks=1)
		displayed_playlist_bookmark = displayed_playlist.bookmarks[0]
		self._assert_displayed_playlist_bookmark(displayed_playlist_bookmark,
				bookmark_id, video_title, bookmark_comment, add_bookmark_time,
				user_name2, user_id2)

		# Remove the bookmark from the playlist.
		remove_bookmark_time = self.now + timedelta(minutes=30)
		db.remove_playlist_bookmark(user_id1, playlist_id, bookmark_id,
				now=remove_bookmark_time)
		# Assert that the playlist has no bookmarks.
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_title,
				time_updated=remove_bookmark_time, num_bookmarks=0)

		# Remove the bookmark from the playlist again.
		remove_bookmark_again_time = self.now + timedelta(minutes=40)
		db.remove_playlist_bookmark(user_id1, playlist_id, bookmark_id,
				now=remove_bookmark_again_time)
		# Assert that this had no effect.
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_title,
				time_updated=remove_bookmark_time, num_bookmarks=0)

	"""Test that fails to add a bookmark to a playlist because the user identifier is
	not the playlist creator.
	"""
	def test_add_playlist_bookmark_wrong_user(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		# Create a user with a playlist.
		user_name1 = 'user_name1'
		user_steam_id1, user_id1 = self._create_steam_user(user_name1)
		playlist_title = 'playlist1'
		playlist_id = db.create_playlist(user_id1, playlist_title, now=self.now)
		# Create a video with a bookmark.
		video_title = 'video1'
		video_length = 61
		archive_id = 'archive_id1'
		video_file_url = 'video_file_url1'
		link_url = 'link_url1'
		video_id = db.add_twitch_video(
				video_title, video_length, archive_id, video_file_url, link_url)
		# Create a bookmark for that video by another user.
		user_name2 = 'user_name2'
		user_steam_id2, user_id2 = self._create_steam_user(user_name2)
		bookmark_comment = 'comment1'
		bookmark_time = 33
		bookmark_id = db.add_video_bookmark(
				user_id2, video_id, bookmark_comment, bookmark_time, self.now)

		# Assert that adding the bookmark by a user not the playlist creator fails.
		user_name3 = 'user_name3'
		user_steam_id3, user_id3 = self._create_steam_user(user_name3)
		add_bookmark_time = self.now + timedelta(minutes=10)
		with self.assertRaises(db.DbException):
			db.add_playlist_bookmark(user_id3, playlist_id, bookmark_id,
					now=add_bookmark_time)
		# Assert that this had no effect.
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_title)

	"""Test that fails to remove a bookmark from a playlist because the user identifier
	is not the playlist creator.
	"""
	def test_remove_playlist_bookmark_wrong_user(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		# Create a user with a playlist.
		user_name1 = 'user_name1'
		user_steam_id1, user_id1 = self._create_steam_user(user_name1)
		playlist_title = 'playlist1'
		playlist_id = db.create_playlist(user_id1, playlist_title, now=self.now)
		# Create a video with a bookmark.
		video_title = 'video1'
		video_length = 61
		archive_id = 'archive_id1'
		video_file_url = 'video_file_url1'
		link_url = 'link_url1'
		video_id = db.add_twitch_video(
				video_title, video_length, archive_id, video_file_url, link_url)
		# Create a bookmark for that video by another user.
		user_name2 = 'user_name2'
		user_steam_id2, user_id2 = self._create_steam_user(user_name2)
		bookmark_comment = 'comment1'
		bookmark_time = 33
		bookmark_id = db.add_video_bookmark(
				user_id2, video_id, bookmark_comment, bookmark_time, self.now)

		# Add the bookmark to the playlist.
		add_bookmark_time = self.now + timedelta(minutes=10)
		db.add_playlist_bookmark(user_id1, playlist_id, bookmark_id,
				now=add_bookmark_time)

		# Assert that removing the bookmark by a user not the playlist creator fails.
		user_name3 = 'user_name3'
		user_steam_id3, user_id3 = self._create_steam_user(user_name3)
		remove_bookmark_time = self.now + timedelta(minutes=20)
		with self.assertRaises(db.DbException):
			db.remove_playlist_bookmark(user_id3, playlist_id, bookmark_id,
					now=remove_bookmark_time)
		# Assert that this had no effect.
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_title,
				time_updated=add_bookmark_time, num_bookmarks=1)
		displayed_playlist_bookmark = displayed_playlist.bookmarks[0]
		self._assert_displayed_playlist_bookmark(displayed_playlist_bookmark,
				bookmark_id, video_title, bookmark_comment, add_bookmark_time,
				user_name2, user_id2)

	"""Test that fails to vote a bookmark up or down because the user identifier is
	unknown.
	"""
	def test_vote_playlist_unknown_user(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		# Create a user with a playlist.
		user_name = 'user_name1'
		user_steam_id, user_id = self._create_steam_user(user_name)
		playlist_title = 'playlist1'
		playlist_id = db.create_playlist(user_id, playlist_title, now=self.now)
		
		missing_user_id = 'missing_user_id'

		# Assert that voting up the playlist with a missing user fails.
		with self.assertRaises(db.DbException):
			db.vote_playlist_thumb_up(missing_user_id, playlist_id)
		# Assert that this had no effect.
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id, user_name, self.now, playlist_title)

		# Assert that voting down the playlist with a missing user fails.
		with self.assertRaises(db.DbException):
			db.vote_playlist_thumb_down(missing_user_id, playlist_id)
		# Assert that this had no effect.
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id, user_name, self.now, playlist_title)

		# Assert that removing the playlist vote with a missing user fails.
		with self.assertRaises(db.DbException):
			db.remove_playlist_vote(missing_user_id, playlist_id)
		# Assert that this had no effect.
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id, user_name, self.now, playlist_title)

	"""Test that fails to vote a bookmark up or down because the user identifier is
	the creator.
	"""
	def test_vote_playlist_by_creator(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		# Create a user with a playlist.
		user_name = 'user_name1'
		user_steam_id, user_id = self._create_steam_user(user_name)
		playlist_title = 'playlist1'
		playlist_id = db.create_playlist(user_id, playlist_title, now=self.now)
			
		# Assert that the creator voting up the playlist fails.
		with self.assertRaises(db.DbException):
			db.vote_playlist_thumb_up(user_id, playlist_id)
		# Assert that this had no effect.
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id, user_name, self.now, playlist_title)

		# Assert that the creator voting down the playlist fails.
		with self.assertRaises(db.DbException):
			db.vote_playlist_thumb_down(user_id, playlist_id)
		# Assert that this had no effect.
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id, user_name, self.now, playlist_title)

		# Assert that the creator removing the playlist vote fails.
		with self.assertRaises(db.DbException):
			db.remove_playlist_vote(user_id, playlist_id)
		# Assert that this had no effect.
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id, user_name, self.now, playlist_title)

	"""Test that fails to vote a playlist up or down because the playlist identifier
	is unknown.
	"""
	def test_vote_playlist_unknown_playlist(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		# Create a user.
		user_name = 'user_name1'
		user_steam_id, user_id = self._create_steam_user(user_name)

		missing_playlist_id = 'missing_playlist_id'

		# Assert that voting up a missing playlist fails.
		with self.assertRaises(db.DbException):
			db.vote_playlist_thumb_up(user_id, missing_playlist_id)
		# Assert that this had no effect.
		with self.assertRaises(db.DbException):
			db.get_displayed_playlist(client_id, missing_playlist_id)

		# Assert that voting down a missing playlist fails.
		with self.assertRaises(db.DbException):
			db.vote_playlist_thumb_down(user_id, missing_playlist_id)
		# Assert that this had no effect.
		with self.assertRaises(db.DbException):
			db.get_displayed_playlist(client_id, missing_playlist_id)

		# Assert that removing the vote for a missing playlist fails.
		with self.assertRaises(db.DbException):
			db.remove_playlist_vote(user_id, missing_playlist_id)
		# Assert that this had no effect.
		with self.assertRaises(db.DbException):
			db.get_displayed_playlist(client_id, missing_playlist_id)

	"""Test that successfully votes up a playlist.
	"""
	def test_up_vote_playlist(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		# Create a user with a playlist.
		user_name1 = 'user_name1'
		user_steam_id1, user_id1 = self._create_steam_user(user_name1)
		playlist_title = 'playlist1'
		playlist_id = db.create_playlist(user_id1, playlist_title, now=self.now)
		# Create another user to vote up the playlist.
		user_name2 = 'user_name2'
		user_steam_id2, user_id2 = self._create_steam_user(user_name2)

		# Vote up the playlist.
		db.vote_playlist_thumb_up(user_id2, playlist_id, now=self.now)
		# Assert that the playlist has been voted on.
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_title, num_thumbs_up=1)

		# Vote up the playlist again.
		db.vote_playlist_thumb_up(user_id2, playlist_id)
		# Assert that this had no effect.
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_title, num_thumbs_up=1)

		# Remove the vote for the playlist.
		db.remove_playlist_vote(user_id2, playlist_id)
		# Assert that the playlist is no longer voted on.
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_title)

		# Remove the vote for the playlist again.
		with self.assertRaises(db.DbException):
			db.remove_playlist_vote(user_id2, playlist_id)
		# Assert that this had no effect.
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_title)

	"""Test that successfully votes down a playlist.
	"""
	def test_down_vote_playlist(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		# Create a user with a playlist.
		user_name1 = 'user_name1'
		user_steam_id1, user_id1 = self._create_steam_user(user_name1)
		playlist_title = 'playlist1'
		playlist_id = db.create_playlist(user_id1, playlist_title, now=self.now)
		# Create another user to vote down the playlist.
		user_name2 = 'user_name2'
		user_steam_id2, user_id2 = self._create_steam_user(user_name2)

		# Vote down the playlist.
		db.vote_playlist_thumb_down(user_id2, playlist_id, now=self.now)
		# Assert that the playlist has been voted on.
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_title, num_thumbs_down=1)

		# Vote down the playlist again.
		db.vote_playlist_thumb_down(user_id2, playlist_id)
		# Assert that this had no effect.
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_title, num_thumbs_down=1)

		# Remove the vote for the playlist.
		db.remove_playlist_vote(user_id2, playlist_id)
		# Assert that the playlist is no longer voted on.
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_title)

		# Remove the vote for the playlist again.
		with self.assertRaises(db.DbException):
			db.remove_playlist_vote(user_id2, playlist_id)
		# Assert that this had no effect.
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_title)

	"""Test that successfully changes the vote of a playlist.
	"""
	def test_change_vote_playlist(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		# Create a user with a playlist.
		user_name1 = 'user_name1'
		user_steam_id1, user_id1 = self._create_steam_user(user_name1)
		playlist_title = 'playlist1'
		playlist_id = db.create_playlist(user_id1, playlist_title, now=self.now)
		# Create another user to vote on the playlist.
		user_name2 = 'user_name2'
		user_steam_id2, user_id2 = self._create_steam_user(user_name2)

		# Vote up the playlist.
		db.vote_playlist_thumb_up(user_id2, playlist_id, now=self.now)
		# Assert that the playlist has been voted on.
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_title, num_thumbs_up=1)

		# Vote down the playlist.
		db.vote_playlist_thumb_down(user_id2, playlist_id, now=self.now)
		# Assert that the playlist has been voted on.
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_title, num_thumbs_down=1)

		# Vote up the playlist again.
		db.vote_playlist_thumb_up(user_id2, playlist_id, now=self.now)
		# Assert that the playlist has been voted on.
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_title, num_thumbs_up=1)

		# Remove the vote for the playlist.
		db.remove_playlist_vote(user_id2, playlist_id)
		# Assert that the playlist is no longer voted on.
		displayed_playlist = db.get_displayed_playlist(client_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id1, user_name1, self.now, playlist_title)

	"""Test that clients see their own votes for playlists.
	"""
	def test_client_votes_playlist(self):
		# Create a user with a playlist.
		user_name = 'user_name1'
		user_steam_id, user_id = self._create_steam_user(user_name)
		playlist_title = 'playlist1'
		playlist_id = db.create_playlist(user_id, playlist_title, now=self.now)
		# Create a user to vote up the playlist.
		client_name1 = 'client_name1'
		client_steam_id1, client_id1 = self._create_steam_user(client_name1)
		db.vote_playlist_thumb_up(client_id1, playlist_id, now=self.now)
		# Create a user to vote down the playlist.
		client_name2 = 'client_name2'
		client_steam_id2, client_id2 = self._create_steam_user(client_name2)
		db.vote_playlist_thumb_down(client_id2, playlist_id, now=self.now)

		# Assert that the playlist creator sees no vote.
		displayed_playlist = db.get_displayed_playlist(user_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id, user_name, self.now, playlist_title,
				num_thumbs_up=1, num_thumbs_down=1)
		# Assert that the first client sees his vote up.
		displayed_playlist = db.get_displayed_playlist(client_id1, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id, user_name, self.now, playlist_title,
				num_thumbs_up=1, num_thumbs_down=1, user_vote=db._THUMB_UP_VOTE)
		# Assert that the second client sees his vote down.
		displayed_playlist = db.get_displayed_playlist(client_id2, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id, user_name, self.now, playlist_title,
				num_thumbs_up=1, num_thumbs_down=1, user_vote=db._THUMB_DOWN_VOTE)
		# Assert that a logged out client sees no vote.
		displayed_playlist = db.get_displayed_playlist(None, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id, user_name, self.now, playlist_title,
				num_thumbs_up=1, num_thumbs_down=1)

	"""Test that clients see their own votes for playlists of users.
	"""
	def test_client_votes_user_playlist(self):
		# Create a user with a playlist.
		user_name = 'user_name1'
		user_steam_id, user_id = self._create_steam_user(user_name)
		playlist_title = 'playlist1'
		playlist_id = db.create_playlist(user_id, playlist_title, now=self.now)
		# Create a user to vote up the playlist.
		client_name1 = 'client_name1'
		client_steam_id1, client_id1 = self._create_steam_user(client_name1)
		db.vote_playlist_thumb_up(client_id1, playlist_id, now=self.now)
		# Create a user to vote down the playlist.
		client_name2 = 'client_name2'
		client_steam_id2, client_id2 = self._create_steam_user(client_name2)
		db.vote_playlist_thumb_down(client_id2, playlist_id, now=self.now)

		# Assert that the user sees no vote.
		displayed_user = db.get_displayed_user(user_id, user_id)
		self._assert_displayed_user(displayed_user, user_id, user_name, num_playlists=1)
		displayed_user_playlist = displayed_user.playlists[0]
		self._assert_displayed_user_playlist(displayed_user_playlist,
				playlist_id, playlist_title, self.now,
				num_thumbs_up=1, num_thumbs_down=1)
		# Assert that the first client sees his vote up.
		displayed_user = db.get_displayed_user(client_id1, user_id)
		self._assert_displayed_user(displayed_user, user_id, user_name, num_playlists=1)
		displayed_user_playlist = displayed_user.playlists[0]
		self._assert_displayed_user_playlist(displayed_user_playlist,
				playlist_id, playlist_title, self.now,
				num_thumbs_up=1, num_thumbs_down=1, user_vote=db._THUMB_UP_VOTE)
		# Assert that the second client sees his vote down.
		displayed_user = db.get_displayed_user(client_id2, user_id)
		self._assert_displayed_user(displayed_user, user_id, user_name, num_playlists=1)
		displayed_user_playlist = displayed_user.playlists[0]
		self._assert_displayed_user_playlist(displayed_user_playlist,
				playlist_id, playlist_title, self.now,
				num_thumbs_up=1, num_thumbs_down=1, user_vote=db._THUMB_DOWN_VOTE)
		# Assert that a logged out client sees no vote.
		displayed_user = db.get_displayed_user(None, user_id)
		self._assert_displayed_user(displayed_user, user_id, user_name, num_playlists=1)
		displayed_user_playlist = displayed_user.playlists[0]
		self._assert_displayed_user_playlist(displayed_user_playlist,
				playlist_id, playlist_title, self.now,
				num_thumbs_up=1, num_thumbs_down=1)

	"""Test that clients see their own votes for bookmarks of playlists.
	"""
	def test_client_votes_playlist_bookmark(self):
		# Create a user with a playlist.
		user_name = 'user_name1'
		user_steam_id, user_id = self._create_steam_user(user_name)
		playlist_title = 'playlist1'
		playlist_id = db.create_playlist(user_id, playlist_title, now=self.now)
		# Create a video.
		video_title = 'video1'
		video_length = 61
		archive_id = 'archive_id1'
		video_file_url = 'video_file_url1'
		link_url = 'link_url1'
		video_id = db.add_twitch_video(
				video_title, video_length, archive_id, video_file_url, link_url)
		# Create a bookmark for that video.
		bookmark_comment = 'comment1'
		bookmark_time = 33
		bookmark_id = db.add_video_bookmark(
				user_id, video_id, bookmark_comment, bookmark_time, self.now)
		# Add the bookmark to the playlist.
		add_bookmark_time = self.now + timedelta(minutes=10)
		db.add_playlist_bookmark(user_id, playlist_id, bookmark_id,
				now=add_bookmark_time)
		# Create a user to vote up the bookmark.
		client_name1 = 'client_name1'
		client_steam_id1, client_id1 = self._create_steam_user(client_name1)
		db.vote_bookmark_thumb_up(client_id1, bookmark_id, now=self.now)
		# Create a user to vote down the bookmark.
		client_name2 = 'client_name2'
		client_steam_id2, client_id2 = self._create_steam_user(client_name2)
		db.vote_bookmark_thumb_down(client_id2, bookmark_id, now=self.now)

		# Assert that the playlist creator sees no vote.
		displayed_playlist = db.get_displayed_playlist(user_id, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id, user_name, self.now, playlist_title,
				time_updated=add_bookmark_time, num_bookmarks=1)
		displayed_playlist_bookmark = displayed_playlist.bookmarks[0]
		self._assert_displayed_playlist_bookmark(displayed_playlist_bookmark,
				bookmark_id, video_title, bookmark_comment, add_bookmark_time,
				user_name, user_id,
				num_thumbs_up=1, num_thumbs_down=1)
		# Assert that the first client sees his vote up.
		displayed_playlist = db.get_displayed_playlist(client_id1, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id, user_name, self.now, playlist_title,
				time_updated=add_bookmark_time, num_bookmarks=1)
		displayed_playlist_bookmark = displayed_playlist.bookmarks[0]
		self._assert_displayed_playlist_bookmark(displayed_playlist_bookmark,
				bookmark_id, video_title, bookmark_comment, add_bookmark_time,
				user_name, user_id,
				num_thumbs_up=1, num_thumbs_down=1, user_vote=db._THUMB_UP_VOTE)
		# Assert that the second client sees his vote down.
		displayed_playlist = db.get_displayed_playlist(client_id2, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id, user_name, self.now, playlist_title,
				time_updated=add_bookmark_time, num_bookmarks=1)
		displayed_playlist_bookmark = displayed_playlist.bookmarks[0]
		self._assert_displayed_playlist_bookmark(displayed_playlist_bookmark,
				bookmark_id, video_title, bookmark_comment, add_bookmark_time,
				user_name, user_id,
				num_thumbs_up=1, num_thumbs_down=1, user_vote=db._THUMB_DOWN_VOTE)
		# Assert that a logged out client sees no vote.
		displayed_playlist = db.get_displayed_playlist(None, playlist_id)
		self._assert_displayed_playlist(displayed_playlist,
				user_id, user_name, self.now, playlist_title,
				time_updated=add_bookmark_time, num_bookmarks=1)
		displayed_playlist_bookmark = displayed_playlist.bookmarks[0]
		self._assert_displayed_playlist_bookmark(displayed_playlist_bookmark,
				bookmark_id, video_title, bookmark_comment, add_bookmark_time,
				user_name, user_id,
				num_thumbs_up=1, num_thumbs_down=1)

	# 
	# Begin tests for videos.
	# 

	"""Test that fails to return a displayed video because the video identifier is
	unknown.
	"""
	def test_get_displayed_twitch_video_unknown_video(self):
		# TODO: actually, this should implicitly create the video
		pass

	"""Test that fails to create a bookmark because the user identifier is unknown.
	"""
	def test_create_bookmark_unknown_user(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		# Create a video.
		video_title = 'video1'
		video_length = 61
		archive_id = 'archive_id1'
		video_file_url = 'video_file_url1'
		link_url = 'link_url1'
		video_id = db.add_twitch_video(
				video_title, video_length, archive_id, video_file_url, link_url)

		# Assert that creating a bookmark by a missing user fails.
		bookmark_comment = 'comment1'
		bookmark_time = 33
		missing_user_id = 'missing_user_id'
		with self.assertRaises(db.DbException):
			db.add_video_bookmark(missing_user_id, video_id,
					bookmark_comment, bookmark_time, now=self.now)
		# Assert that this had no effect.
		displayed_twitch_video = db.get_displayed_twitch_video(client_id, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url)
	
	"""Test that fails to create a bookmark because the video identifier is unknown.
	"""
	def test_create_bookmark_unknown_video(self):
		# Create a user.
		user_name = 'user_name1'
		user_steam_id, user_id = self._create_steam_user(user_name)

		# Assert that creating a bookmark for a missing video fails.
		bookmark_comment = 'comment1'
		bookmark_time = 33
		missing_video_id = 'missing_video_id'
		with self.assertRaises(db.DbException):
			db.add_video_bookmark(user_id, missing_video_id,
					bookmark_comment, bookmark_time, now=self.now)

	"""Test that successfully creates and deletes a bookmark.
	"""
	def test_create_delete_bookmark(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		# Create a user.
		user_name = 'user_name1'
		user_steam_id, user_id = self._create_steam_user(user_name)
		# Create a video.
		video_title = 'video1'
		video_length = 61
		archive_id = 'archive_id1'
		video_file_url = 'video_file_url1'
		link_url = 'link_url1'
		video_id = db.add_twitch_video(
				video_title, video_length, archive_id, video_file_url, link_url)

		# Add the bookmark to the video.
		add_bookmark_time = self.now + timedelta(minutes=10)
		bookmark_comment = 'comment1'
		bookmark_time = 33
		bookmark_id = db.add_video_bookmark(
				user_id, video_id, bookmark_comment, bookmark_time, now=add_bookmark_time)
		# Assert that the video has a bookmark.
		displayed_twitch_video = db.get_displayed_twitch_video(client_id, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url,
				num_bookmarks=1)
		# Assert that the bookmark is correct.
		displayed_video_bookmark = displayed_twitch_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, add_bookmark_time,
				user_name, user_id)

		# Remove the bookmark from the video.
		remove_bookmark_time = self.now + timedelta(minutes=20)
		db.remove_video_bookmark(user_id, bookmark_id, now=remove_bookmark_time)
		# Assert that the video has no bookmarks.
		displayed_twitch_video = db.get_displayed_twitch_video(client_id, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url)

		# Remove the bookmark from the video again.
		remove_bookmark_again_time = self.now + timedelta(minutes=30)
		with self.assertRaises(db.DbException):
			db.remove_video_bookmark(
					user_id, bookmark_id, now=remove_bookmark_again_time)
		# Assert that this had no effect.
		displayed_twitch_video = db.get_displayed_twitch_video(client_id, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url)
	
	"""Test that fails to delete a bookmark that does not exist.
	"""
	def test_delete_missing_bookmark(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		# Create a user.
		user_name = 'user_name1'
		user_steam_id, user_id = self._create_steam_user(user_name)
		# Create a video.
		video_title = 'video1'
		video_length = 61
		archive_id = 'archive_id1'
		video_file_url = 'video_file_url1'
		link_url = 'link_url1'
		video_id = db.add_twitch_video(
				video_title, video_length, archive_id, video_file_url, link_url)
		# Delete a missing bookmark.
		remove_bookmark_time = self.now + timedelta(minutes=10)
		missing_bookmark_id = 'missing_bookmark_id'
		with self.assertRaises(db.DbException):
			db.remove_video_bookmark(
					user_id, missing_bookmark_id, now=remove_bookmark_time)

		# Assert that this had no effect.
		displayed_twitch_video = db.get_displayed_twitch_video(client_id, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url)

	"""Test that fails to delete a bookmark because the user identifier is not
	the creator.
	"""
	def test_delete_bookmark_wrong_user(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		# Create a video.
		video_title = 'video1'
		video_length = 61
		archive_id = 'archive_id1'
		video_file_url = 'video_file_url1'
		link_url = 'link_url1'
		video_id = db.add_twitch_video(
				video_title, video_length, archive_id, video_file_url, link_url)
		# Create a bookmark for that video by a user.
		user_name1 = 'user_name1'
		user_steam_id1, user_id1 = self._create_steam_user(user_name1)
		bookmark_comment = 'comment1'
		bookmark_time = 33
		bookmark_id = db.add_video_bookmark(
				user_id1, video_id, bookmark_comment, bookmark_time, self.now)

		# Assert that a user removing the bookmark who is not the creator fails.
		user_name2 = 'user_name2'
		user_steam_id2, user_id2 = self._create_steam_user(user_name2)
		remove_bookmark_time = self.now + timedelta(minutes=10)
		with self.assertRaises(db.DbException):
			db.remove_video_bookmark(
					user_id2, bookmark_id, now=remove_bookmark_time)

		# Assert that this had no effect.
		displayed_twitch_video = db.get_displayed_twitch_video(client_id, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url,
				num_bookmarks=1)
		displayed_video_bookmark = displayed_twitch_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name1, user_id1)

	"""Test that fails to vote a bookmark up or down because the user identifier is
	unknown.
	"""
	def test_vote_bookmark_unknown_user(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		# Create a video with a bookmark by a user.
		video_title = 'video1'
		video_length = 61
		archive_id = 'archive_id1'
		video_file_url = 'video_file_url1'
		link_url = 'link_url1'
		video_id = db.add_twitch_video(
				video_title, video_length, archive_id, video_file_url, link_url)
		# Create a bookmark for that video by a user.
		user_name = 'user_name1'
		user_steam_id, user_id = self._create_steam_user(user_name)
		bookmark_comment = 'comment1'
		bookmark_time = 33
		bookmark_id = db.add_video_bookmark(
				user_id, video_id, bookmark_comment, bookmark_time, self.now)

		missing_user_id = 'missing_user_id'

		# Assert that voting up the bookmark with a missing user fails.
		with self.assertRaises(db.DbException):
			db.vote_bookmark_thumb_up(missing_user_id, bookmark_id)
		# Assert that this had no effect.
		displayed_twitch_video = db.get_displayed_twitch_video(client_id, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url,
				num_bookmarks=1)
		displayed_video_bookmark = displayed_twitch_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name, user_id)

		# Assert that voting up the bookmark with a missing user fails.
		with self.assertRaises(db.DbException):
			db.vote_bookmark_thumb_down(missing_user_id, bookmark_id)
		# Assert that this had no effect.
		displayed_twitch_video = db.get_displayed_twitch_video(client_id, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url,
				num_bookmarks=1)
		displayed_video_bookmark = displayed_twitch_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name, user_id)

		# Assert that removing the bookmark vote with a missing user fails.
		with self.assertRaises(db.DbException):
			db.remove_bookmark_vote(missing_user_id, bookmark_id)
		# Assert that this had no effect.
		displayed_twitch_video = db.get_displayed_twitch_video(client_id, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url,
				num_bookmarks=1)
		displayed_video_bookmark = displayed_twitch_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name, user_id)
	
	"""Test that fails to vote a bookmark up or down because the user identifier is
	the creator.
	"""
	def test_vote_bookmark_by_creator(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		# Create a video.
		video_title = 'video1'
		video_length = 61
		archive_id = 'archive_id1'
		video_file_url = 'video_file_url1'
		link_url = 'link_url1'
		video_id = db.add_twitch_video(
				video_title, video_length, archive_id, video_file_url, link_url)
		# Create a bookmark for that video by a user.
		user_name = 'user_name1'
		user_steam_id, user_id = self._create_steam_user(user_name)
		bookmark_comment = 'comment1'
		bookmark_time = 33
		bookmark_id = db.add_video_bookmark(
				user_id, video_id, bookmark_comment, bookmark_time, self.now)

		# Assert that the creator voting up the bookmark fails.
		with self.assertRaises(db.DbException):
			db.vote_bookmark_thumb_up(user_id, bookmark_id)
		# Assert that this had no effect.
		displayed_twitch_video = db.get_displayed_twitch_video(client_id, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url,
				num_bookmarks=1)
		displayed_video_bookmark = displayed_twitch_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name, user_id)

		# Assert that the creator voting up the bookmark fails.
		with self.assertRaises(db.DbException):
			db.vote_bookmark_thumb_down(user_id, bookmark_id)
		# Assert that this had no effect.
		displayed_twitch_video = db.get_displayed_twitch_video(client_id, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url,
				num_bookmarks=1)
		displayed_video_bookmark = displayed_twitch_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name, user_id)

		# Assert that the creator removing the bookmark vote fails.
		with self.assertRaises(db.DbException):
			db.remove_bookmark_vote(user_id, bookmark_id)
		# Assert that this had no effect.
		displayed_twitch_video = db.get_displayed_twitch_video(client_id, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url,
				num_bookmarks=1)
		displayed_video_bookmark = displayed_twitch_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name, user_id)

	"""Test that fails to vote a bookmark up or down because the bookmark identifier is
	unknown.
	"""
	def test_vote_bookmark_unknown_bookmark(self):
		# Create a user.
		user_name = 'user_name1'
		user_steam_id, user_id = self._create_steam_user(user_name)

		missing_bookmark_id = 'missing_bookmark_id'

		# Assert that voting up a missing bookmark fails.
		with self.assertRaises(db.DbException):
			db.vote_bookmark_thumb_up(user_id, missing_bookmark_id)

		# Assert that voting down a missing bookmark fails.
		with self.assertRaises(db.DbException):
			db.vote_bookmark_thumb_down(user_id, missing_bookmark_id)

		# Assert that removing the vote for a missing bookmark fails.
		with self.assertRaises(db.DbException):
			db.remove_bookmark_vote(user_id, missing_bookmark_id)

	"""Test that successfully votes up a bookmark.
	"""
	def test_up_vote_bookmark(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		# Create a video.
		video_title = 'video1'
		video_length = 61
		archive_id = 'archive_id1'
		video_file_url = 'video_file_url1'
		link_url = 'link_url1'
		video_id = db.add_twitch_video(
				video_title, video_length, archive_id, video_file_url, link_url)
		# Create a bookmark for that video by a user.
		user_name1 = 'user_name1'
		user_steam_id1, user_id1 = self._create_steam_user(user_name1)
		bookmark_comment = 'comment1'
		bookmark_time = 33
		bookmark_id = db.add_video_bookmark(
				user_id1, video_id, bookmark_comment, bookmark_time, self.now)
		# Create another user to vote up the bookmark.
		user_name2 = 'user_name2'
		user_steam_id2, user_id2 = self._create_steam_user(user_name2)

		# Vote up the bookmark.
		db.vote_bookmark_thumb_up(user_id2, bookmark_id, now=self.now)
		# Assert that the bookmark has been voted on.
		displayed_twitch_video = db.get_displayed_twitch_video(client_id, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url,
				num_bookmarks=1)
		displayed_video_bookmark = displayed_twitch_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name1, user_id1, num_thumbs_up=1)

		# Vote up the bookmark again.
		db.vote_bookmark_thumb_up(user_id2, bookmark_id, now=self.now)
		# Assert that this had no effect.
		displayed_twitch_video = db.get_displayed_twitch_video(client_id, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url,
				num_bookmarks=1)
		displayed_video_bookmark = displayed_twitch_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name1, user_id1, num_thumbs_up=1)

		# Remove the vote for the bookmark.
		db.remove_bookmark_vote(user_id2, bookmark_id)
		# Assert that the bookmark is no longer voted on.
		displayed_twitch_video = db.get_displayed_twitch_video(client_id, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url,
				num_bookmarks=1)
		displayed_video_bookmark = displayed_twitch_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name1, user_id1)

		# Remove the vote for the bookmark again.
		with self.assertRaises(db.DbException):
			db.remove_bookmark_vote(user_id2, bookmark_id)
		# Assert that this had no effect.
		displayed_twitch_video = db.get_displayed_twitch_video(client_id, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url,
				num_bookmarks=1)
		displayed_video_bookmark = displayed_twitch_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name1, user_id1)

	"""Test that successfully votes down a bookmark.
	"""
	def test_down_vote_bookmark(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		# Create a video.
		video_title = 'video1'
		video_length = 61
		archive_id = 'archive_id1'
		video_file_url = 'video_file_url1'
		link_url = 'link_url1'
		video_id = db.add_twitch_video(
				video_title, video_length, archive_id, video_file_url, link_url)
		# Create a bookmark for that video by a user.
		user_name1 = 'user_name1'
		user_steam_id1, user_id1 = self._create_steam_user(user_name1)
		bookmark_comment = 'comment1'
		bookmark_time = 33
		bookmark_id = db.add_video_bookmark(
				user_id1, video_id, bookmark_comment, bookmark_time, self.now)
		# Create another user to vote down the bookmark.
		user_name2 = 'user_name2'
		user_steam_id2, user_id2 = self._create_steam_user(user_name2)

		# Vote down the bookmark.
		db.vote_bookmark_thumb_down(user_id2, bookmark_id, now=self.now)
		# Assert that the bookmark has been voted on.
		displayed_twitch_video = db.get_displayed_twitch_video(client_id, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url,
				num_bookmarks=1)
		displayed_video_bookmark = displayed_twitch_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name1, user_id1, num_thumbs_down=1)

		# Vote down the bookmark again.
		db.vote_bookmark_thumb_down(user_id2, bookmark_id, now=self.now)
		# Assert that this had no effect.
		displayed_twitch_video = db.get_displayed_twitch_video(client_id, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url,
				num_bookmarks=1)
		displayed_video_bookmark = displayed_twitch_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name1, user_id1, num_thumbs_down=1)

		# Remove the vote for the bookmark.
		db.remove_bookmark_vote(user_id2, bookmark_id)
		# Assert that the bookmark is no longer voted on.
		displayed_twitch_video = db.get_displayed_twitch_video(client_id, archive_id)
		self._assert_displayed_video(displayed_twitch_video,
				video_title, video_length, num_bookmarks=1)
		displayed_video_bookmark = displayed_twitch_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name1, user_id1)

		# Remove the vote for the bookmark again.
		with self.assertRaises(db.DbException):
			db.remove_bookmark_vote(user_id2, bookmark_id)
		# Assert that this had no effect.
		displayed_twitch_video = db.get_displayed_twitch_video(client_id, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url,
				num_bookmarks=1)
		displayed_video_bookmark = displayed_twitch_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name1, user_id1)

	"""Test that successfully changes the vote of a bookmark.
	"""
	def test_change_vote_bookmark(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		# Create a video.
		video_title = 'video1'
		video_length = 61
		archive_id = 'archive_id1'
		video_file_url = 'video_file_url1'
		link_url = 'link_url1'
		video_id = db.add_twitch_video(
				video_title, video_length, archive_id, video_file_url, link_url)
		# Create a bookmark for that video by a user.
		user_name1 = 'user_name1'
		user_steam_id1, user_id1 = self._create_steam_user(user_name1)
		bookmark_comment = 'comment1'
		bookmark_time = 33
		bookmark_id = db.add_video_bookmark(
				user_id1, video_id, bookmark_comment, bookmark_time, self.now)
		# Create another user to vote on the bookmark.
		user_name2 = 'user_name2'
		user_steam_id2, user_id2 = self._create_steam_user(user_name2)

		# Vote up the bookmark.
		db.vote_bookmark_thumb_up(user_id2, bookmark_id, now=self.now)
		# Assert that the bookmark has been voted on.
		displayed_twitch_video = db.get_displayed_twitch_video(client_id, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url,
				num_bookmarks=1)
		displayed_video_bookmark = displayed_twitch_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name1, user_id1, num_thumbs_up=1)

		# Vote down the bookmark.
		db.vote_bookmark_thumb_down(user_id2, bookmark_id, now=self.now)
		# Assert that the bookmark has been voted on.
		displayed_twitch_video = db.get_displayed_twitch_video(client_id, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url,
				num_bookmarks=1)
		displayed_video_bookmark = displayed_twitch_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name1, user_id1, num_thumbs_down=1)

		# Vote up the bookmark again.
		db.vote_bookmark_thumb_up(user_id2, bookmark_id, now=self.now)
		# Assert that the bookmark has been voted on.
		displayed_twitch_video = db.get_displayed_twitch_video(client_id, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url,
				num_bookmarks=1)
		displayed_video_bookmark = displayed_twitch_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name1, user_id1, num_thumbs_up=1)

		# Remove the vote for the bookmark.
		db.remove_bookmark_vote(user_id2, bookmark_id)
		# Assert that the bookmark is no longer voted on.
		displayed_twitch_video = db.get_displayed_twitch_video(client_id, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url,
				num_bookmarks=1)
		displayed_video_bookmark = displayed_twitch_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name1, user_id1)

	"""Test that clients see their own votes for bookmarks of videos.
	"""
	def test_client_votes_video_bookmark(self):
		# Create a video.
		video_title = 'video1'
		video_length = 61
		archive_id = 'archive_id1'
		video_file_url = 'video_file_url1'
		link_url = 'link_url1'
		video_id = db.add_twitch_video(
				video_title, video_length, archive_id, video_file_url, link_url)
		# Create a bookmark for that video by a user.
		user_name = 'user_name'
		user_steam_id, user_id = self._create_steam_user(user_name)
		bookmark_comment = 'comment1'
		bookmark_time = 33
		bookmark_id = db.add_video_bookmark(
				user_id, video_id, bookmark_comment, bookmark_time, self.now)
		# Create a user to vote up the bookmark.
		client_name1 = 'client_name1'
		client_steam_id1, client_id1 = self._create_steam_user(client_name1)
		db.vote_bookmark_thumb_up(client_id1, bookmark_id, now=self.now)
		# Create a user to vote down the bookmark.
		client_name2 = 'client_name2'
		client_steam_id2, client_id2 = self._create_steam_user(client_name2)
		db.vote_bookmark_thumb_down(client_id2, bookmark_id, now=self.now)

		# Assert that the bookmark creator sees no vote.
		displayed_twitch_video = db.get_displayed_twitch_video(user_id, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url,
				num_bookmarks=1)
		displayed_video_bookmark = displayed_twitch_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name, user_id, num_thumbs_up=1, num_thumbs_down=1)
		# Assert that the first client sees his vote up.
		displayed_twitch_video = db.get_displayed_twitch_video(client_id1, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url,
				num_bookmarks=1)
		displayed_video_bookmark = displayed_twitch_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name, user_id, num_thumbs_up=1, num_thumbs_down=1,
				user_vote=db._THUMB_UP_VOTE)
		# Assert that the second client sees his vote down.
		displayed_twitch_video = db.get_displayed_twitch_video(client_id2, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url,
				num_bookmarks=1)
		displayed_video_bookmark = displayed_twitch_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name, user_id, num_thumbs_up=1, num_thumbs_down=1,
				user_vote=db._THUMB_DOWN_VOTE)
		# Assert that a logged out client sees no vote.
		displayed_twitch_video = db.get_displayed_twitch_video(None, archive_id)
		self._assert_displayed_twitch_video(displayed_twitch_video,
				video_title, video_length, archive_id, video_file_url, link_url,
				num_bookmarks=1)
		displayed_video_bookmark = displayed_twitch_video.bookmarks[0]
		self._assert_displayed_video_bookmark(displayed_video_bookmark,
				bookmark_id, bookmark_comment, bookmark_time, self.now,
				user_name, user_id, num_thumbs_up=1, num_thumbs_down=1)


if __name__ == '__main__':
	unittest.main()

