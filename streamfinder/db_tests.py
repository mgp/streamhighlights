from datetime import timedelta
import db
from db_test_case import DbTestCase
import sqlalchemy.orm as sa_orm
import unittest


class TestFinderDb(DbTestCase):
	"""Test that fails to create a star because the user identifier is unknown.
	"""
	def test_add_match_star_unknown_user(self):
		missing_user_id = 'missing_user_id'

		with self.assertRaises(db.DbException):
			db.create_playlist(missing_user_id, playlist_title, now=self.now)

	def test_add_match_star_unknown_match(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)

	
	"""Test that successfully creates and deletes a star for a match.
	"""
	def test_add_remove_match_star(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		# Create the match.
		match_id = None	# TODO

		# Add a star for the match.
		db.add_star_match(client_id, match_id, now=self.now)
		# Assert that the match has a star.
		displayed_match = db.get_displayed_match(client_id, match_id)
		self._assert_displayed_match(displayed_match, num_stars=1)

		# Add a star for the match again.
		db.add_star_match(client_id, match_id, now=self.now)
		# Assert that this had no effect.
		displayed_match = db.get_displayed_match(client_id, match_id)
		self._assert_displayed_match(displayed_match, num_stars=1)

		# Remove the star for the match.
		db.remove_star_match(client_id, match_id, now=self.now)
		# Assert that the match no longer has a star.
		displayed_match = db.get_displayed_match(client_id, match_id)
		self._assert_displayed_match(displayed_match)

		# Remove the star for the match again.
		db.remove_star_match(client_id, match_id, now=self.now)
		# Assert that this had no effect.
		displayed_match = db.get_displayed_match(client_id, match_id)
		self._assert_displayed_match(displayed_match)

	# TODO: same three tests with stars for teams and streams for matches

	"""Test that clients see their own stars for matches.
	"""
	def test_client_stars_matches(self):
		pass
	
	"""Test that clients see their own stars for teams.
	"""
	def test_client_stars_teams(self):
		pass
	
	"""Test that clients see their own streams for matches.
	"""
	def test_client_streams_matches(self):
		pass

