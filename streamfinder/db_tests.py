from datetime import datetime, timedelta
import db
from db_test_case import DbTestCase
import functools
import sqlalchemy.orm as sa_orm
import time
import unittest

import common_db

"""Prints the seconds taken to run a decorated function.
"""
def timed(f):
	@functools.wraps(f)
	def decorated_function(*pargs, **kwargs):
		start_time = time.time()
		result = f(*pargs, **kwargs)
		end_time = time.time()
		print 'elapsed seconds: %f' % (end_time - start_time)
		return result
	return decorated_function

class TestFinderDb(DbTestCase):
	def setUp(self):
		DbTestCase.setUp(self)

		self.game = 'game'
		self.league = 'league'
		self.client_name = 'client_name'
		self.streamer_name = 'streamer_name'
		self.team1_name = 'team1_name'
		self.team1_url = 'team1_url'
		self.team1_fingerprint = 'team1_fingerprint'
		self.team2_name = 'team2_name'
		self.team2_url = 'team2_url'
		self.team2_fingerprint = 'team2_fingerprint'
		self.match_url = 'match_url'
		self.match_fingerprint = 'match_fingerprint'
		self.time = datetime(2012, 11, 3, 18, 0, 0)
		self.now = datetime(2012, 11, 5, 12, 0, 0)


	"""Utility method to assert the properties of a DisplayedCalendarMatch.
	"""
	def _assert_displayed_calendar_match(self, displayed_calendar_match,
			match_id, team1_id, team1_name, team2_id, team2_name, time, game, league,
			num_stars=0, num_streams=0):
		# Begin required arguments.
		self.assertEqual(match_id, displayed_calendar_match.match_id)
		self.assertEqual(team1_id, displayed_calendar_match.team1_id)
		self.assertEqual(team1_name, displayed_calendar_match.team1_name)
		self.assertEqual(team2_id, displayed_calendar_match.team2_id)
		self.assertEqual(team2_name, displayed_calendar_match.team2_name)
		self.assertEqual(time, displayed_calendar_match.time)
		self.assertEqual(game, displayed_calendar_match.game)
		self.assertEqual(league, displayed_calendar_match.league)
		# Begin optional arguments.
		self.assertEqual(num_stars, displayed_calendar_match.num_stars)
		self.assertEqual(num_streams, displayed_calendar_match.num_streams)

	"""Utilty method to assert the properties of a DisplayedCalendar.
	"""
	def _assert_displayed_calendar(self, displayed_calendar,
			has_next_match=False, num_matches=0,
			prev_time=None, prev_match_id=None, next_time=None, next_match_id=None):
		# Begin optional arguments.
		self.assertEqual(has_next_match, displayed_calendar.next_match is not None)
		self.assertEqual(num_matches, len(displayed_calendar.matches))
		self.assertEqual(prev_time, displayed_calendar.prev_time)
		self.assertEqual(prev_match_id, displayed_calendar.prev_match_id)
		self.assertEqual(next_time, displayed_calendar.next_time)
		self.assertEqual(next_match_id, displayed_calendar.next_match_id)


	"""Utility method to assert the properties of a DisplayedMatchTeam.
	"""
	def _assert_displayed_match_team(self, displayed_match_team, team_id, name,
			num_stars=0):
		# Begin required arguments.
		self.assertEqual(team_id, displayed_match_team.team_id)
		self.assertEqual(name, displayed_match_team.name)
		# Begin optional arguments.
		self.assertEqual(num_stars, displayed_match_team.num_stars)

	"""Utility method to assert the properties of a DisplayedMatchStreamer.
	"""
	def _assert_displayed_match_streamer(self, displayed_match_streamer,
			user_id, name, url_by_id, num_stars=0, image_url=None, url_by_name=None):
		# Begin required arguments.
		self.assertEqual(user_id, displayed_match_streamer.user_id)
		self.assertEqual(name, displayed_match_streamer.name)
		self.assertEqual(url_by_id, displayed_match_streamer.url_by_id)
		# Begin optional arguments.
		self.assertEqual(num_stars, displayed_match_streamer.num_stars)
		self.assertEqual(image_url, displayed_match_streamer.image_url)
		self.assertEqual(url_by_name, displayed_match_streamer.url_by_name)

	"""Utility method to assert the properties of a DisplayedMatch.
	"""
	def _assert_displayed_match(self, displayed_match, match_id, time, game, league,
			is_starred=False, num_stars=0, num_streamers=0,
			prev_time=None, prev_streamer_id=None, next_time=None, next_streamer_id=None):
		# Begin required arguments.
		self.assertEqual(match_id, displayed_match.match_id)
		self.assertIsNotNone(displayed_match.team1)
		self.assertIsNotNone(displayed_match.team2)
		self.assertEqual(time, displayed_match.time)
		self.assertEqual(game, displayed_match.game)
		self.assertEqual(league, displayed_match.league)
		# Begin optional arguments.
		self.assertEqual(is_starred, displayed_match.is_starred)
		self.assertEqual(num_stars, displayed_match.num_stars)
		# XXX: self.assertEqual(num_streamers, len(displayed_match.streamers))
		self.assertEqual(prev_time, displayed_match.prev_time)
		self.assertEqual(prev_streamer_id, displayed_match.prev_streamer_id)
		self.assertEqual(next_time, displayed_match.next_time)
		self.assertEqual(next_streamer_id, displayed_match.next_streamer_id)


	"""Utility method to assert the properties of a DisplayedTeamMatch.
	"""
	def _assert_displayed_team_match(self, displayed_team_match,
			opponent_id, opponent_name, match_id, time, num_stars=0, num_streams=0):
		# Begin required arguments.
		self.assertEqual(opponent_id, displayed_team_match.opponent_id)
		self.assertEqual(opponent_name, displayed_team_match.opponent_name)
		self.assertEqual(match_id, displayed_team_match.match_id)
		self.assertEqual(time, displayed_team_match.time)
		# Begin optional arguments.
		self.assertEqual(num_stars, displayed_team_match.num_stars)
		self.assertEqual(num_streams, displayed_team_match.num_streams)

	"""Utility method to assert the properties of a DisplayedTeam.
	"""
	def _assert_displayed_team(self, displayed_team, team_id, name, game, league,
			is_starred=False, num_stars=0, num_matches=0,
			prev_time=None, prev_match_id=None, next_time=None, next_match_id=None):
		# Begin required arguments.
		self.assertEqual(team_id, displayed_team.team_id)
		self.assertEqual(name, displayed_team.name)
		self.assertEqual(game, displayed_team.game)
		self.assertEqual(league, displayed_team.league)
		# Begin optional arguments.
		self.assertEqual(is_starred, displayed_team.is_starred)
		self.assertEqual(num_stars, displayed_team.num_stars)
		# XXX self.assertEqual(num_matches, len(displayed_team.matches))
		self.assertEqual(prev_time, displayed_team.prev_time)
		self.assertEqual(prev_match_id, displayed_team.prev_match_id)
		self.assertEqual(next_time, displayed_team.next_time)
		self.assertEqual(next_match_id, displayed_team.next_match_id)


	"""Utility method to assert the properties of a DisplayedStreamerMatch.
	"""
	def _assert_displayed_streamer_match(self, displayed_streamer_match,
			match_id, team1_id, team1_name, team2_id, team2_name, time, game, league,
			num_stars=0, num_streams=0):
		# Begin required arguments.
		self.assertEqual(match_id, displayed_streamer_match.match_id)
		self.assertEqual(team1_id, displayed_streamer_match.team1_id)
		self.assertEqual(team1_name, displayed_streamer_match.team1_name)
		self.assertEqual(team2_id, displayed_streamer_match.team2_id)
		self.assertEqual(team2_name, displayed_streamer_match.team2_name)
		self.assertEqual(time, displayed_streamer_match.time)
		self.assertEqual(game, displayed_streamer_match.game)
		self.assertEqual(league, displayed_streamer_match.league)
		# Begin optional arguments.
		self.assertEqual(num_stars, displayed_streamer_match.num_stars)
		self.assertEqual(num_streams, displayed_streamer_match.num_streams)

	"""Utility method to assert the properties of a DisplayedStreamer.
	"""
	def _assert_displayed_streamer(self, displayed_streamer,
			streamer_id, name, is_starred=False, num_stars=0, num_matches=0,
			prev_time=None, prev_match_id=None, next_time=None, next_match_id=None):
		# Begin required arguments.
		self.assertEqual(streamer_id, displayed_streamer.streamer_id)
		self.assertEqual(name, displayed_streamer.name)
		# Begin optional arguments.
		self.assertEqual(is_starred, displayed_streamer.is_starred)
		self.assertEqual(num_stars, displayed_streamer.num_stars)
		# XXX self.assertEqual(num_matches, len(displayed_streamer.matches))
		self.assertEqual(prev_time, displayed_streamer.prev_time)
		self.assertEqual(prev_match_id, displayed_streamer.prev_match_id)
		self.assertEqual(next_time, displayed_streamer.next_time)
		self.assertEqual(next_match_id, displayed_streamer.next_match_id)


	"""Test that fails to create a match because one team identifier is unknown.
	"""
	def test_add_match_unknown_team(self):
		missing_team2_id = 'missing_team2_id'
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_url, self.team1_fingerprint)
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)

		with self.assertRaises(common_db.DbException):
			db.add_match(team1_id, missing_team2_id, self.time, self.game, self.league,
					self.match_url, self.match_fingerprint, now=self.now)

	"""Test that fails to star a match because the client identifier is unknown.
	"""
	def test_add_match_star_unknown_client(self):
		missing_client_id = 'missing_client_id'
		# Create the match.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_url, self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_url, self.team2_fingerprint)
		match_id = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_url, self.match_fingerprint, now=None)

		with self.assertRaises(common_db.DbException):
			db.add_star_match(missing_client_id, match_id, now=self.now)

	"""Test that fails to star a match because the match identifier is unknown.
	"""
	def test_add_match_star_unknown_match(self):
		missing_match_id = 'missing_match_id'
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)

		with self.assertRaises(common_db.DbException):
			db.add_star_match(client_id, missing_match_id, now=self.now)
	
	"""Test that fails to star a team because the client identifier is unknown.
	"""
	def test_add_team_star_unknown_client(self):
		missing_client_id = 'missing_client_id'
		# Create the team.
		team_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_url, self.team1_fingerprint)
	
		with self.assertRaises(common_db.DbException):
			db.add_star_team(missing_client_id, team_id, now=self.now)

	"""Test that fails to star a match because the team identifier is unknown.
	"""
	def test_add_team_star_unknown_team(self):
		missing_team_id = 'missing_team_id'
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)

		with self.assertRaises(common_db.DbException):
			db.add_star_team(client_id, missing_team_id, now=self.now)
	
	"""Test that fails to star a streamer because the client identifier is unknown.
	"""
	def test_add_streamer_star_unknown_client(self):
		missing_client_id = 'missing_client_id'
		# Create the streaming user.
		streamer_steam_id, streamer_id = self._create_steam_user(self.streamer_name)

		with self.assertRaises(common_db.DbException):
			db.add_star_team(missing_client_id, streamer_id, now=self.now)
	
	"""Test that fails to star a streamer because the streamer identifier is unknown.
	"""
	def test_add_streamer_star_unknown_team(self):
		missing_streamer_id = 'missing_streamer_id'
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)

		with self.assertRaises(common_db.DbException):
			db.add_star_streamer(client_id, missing_streamer_id, now=self.now)

	"""Test that adds and removes a star for a match that is not casted.
	"""
	def test_add_remove_match_star_not_casted(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)
		# Create the match.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_url, self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_url, self.team2_fingerprint)
		match_id = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_url, self.match_fingerprint, now=None)

		# Add a star for the match.
		db.add_star_match(client_id, match_id, now=self.now)
		# Assert that the match has a star.
		displayed_match = db.get_displayed_match(client_id, match_id)
		self._assert_displayed_match(displayed_match,
				match_id, self.time, self.game, self.league,
				is_starred=True, num_stars=1)
		self._assert_displayed_match_team(displayed_match.team1,
				team1_id, self.team1_name)
		self._assert_displayed_match_team(displayed_match.team2,
				team2_id, self.team2_name)
		# Assert that the user's calendar is empty.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)

		# Add a star for the match again.
		with self.assertRaises(common_db.DbException):
			db.add_star_match(client_id, match_id, now=self.now)
		# Assert that this had no effect.
		displayed_match = db.get_displayed_match(client_id, match_id)
		self._assert_displayed_match(displayed_match,
				match_id, self.time, self.game, self.league,
				is_starred=True, num_stars=1)
		self._assert_displayed_match_team(displayed_match.team1,
				team1_id, self.team1_name)
		self._assert_displayed_match_team(displayed_match.team2,
				team2_id, self.team2_name)
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)

		# Remove the star for the match.
		db.remove_star_match(client_id, match_id, now=self.now)
		# Assert that the match no longer has a star.
		displayed_match = db.get_displayed_match(client_id, match_id)
		self._assert_displayed_match(displayed_match,
				match_id, self.time, self.game, self.league)
		self._assert_displayed_match_team(displayed_match.team1,
				team1_id, self.team1_name)
		self._assert_displayed_match_team(displayed_match.team2,
				team2_id, self.team2_name)
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)

		# Remove the star for the match again.
		db.remove_star_match(client_id, match_id, now=self.now)
		# Assert that this had no effect.
		displayed_match = db.get_displayed_match(client_id, match_id)
		self._assert_displayed_match(displayed_match,
				match_id, self.time, self.game, self.league)
		self._assert_displayed_match_team(displayed_match.team1,
				team1_id, self.team1_name)
		self._assert_displayed_match_team(displayed_match.team2,
				team2_id, self.team2_name)
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)

	"""Test that adds and removes a star for a match that is casted.
	"""
	def test_add_remove_match_star_casted(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)
		# Create the match.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_url, self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_url, self.team2_fingerprint)
		match_id = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_url, self.match_fingerprint, now=None)

		# Create the streaming user.
		streamer_steam_id, streamer_id = self._create_steam_user(self.streamer_name)
		# Stream the match.
		db.add_stream_match(streamer_id, match_id)

		# Add a star for the match.
		db.add_star_match(client_id, match_id, now=self.now)
		# Assert that the match has a star.
		displayed_match = db.get_displayed_match(client_id, match_id)
		self._assert_displayed_match(displayed_match,
				match_id, self.time, self.game, self.league,
				is_starred=True, num_stars=1, num_streamers=1)
		self._assert_displayed_match_team(displayed_match.team1,
				team1_id, self.team1_name)
		self._assert_displayed_match_team(displayed_match.team2,
				team2_id, self.team2_name)
		self._assert_displayed_match_streamer(displayed_match.streamers[0],
				streamer_id, self.streamer_name,
				common_db._get_steam_url_by_id(streamer_steam_id))
		# Assert that the user's calendar has the match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		self._assert_displayed_calendar_match(displayed_calendar.next_match,
				match_id, team1_id, self.team1_name, team2_id, self.team2_name,
				self.time, self.game, self.league, num_stars=1, num_streams=1)

		# Remove the star for the match.
		db.remove_star_match(client_id, match_id, now=self.now)
		# Assert that the match no longer has a star.
		displayed_match = db.get_displayed_match(client_id, match_id)
		self._assert_displayed_match(displayed_match,
				match_id, self.time, self.game, self.league, num_streamers=1)
		self._assert_displayed_match_team(displayed_match.team1,
				team1_id, self.team1_name)
		self._assert_displayed_match_team(displayed_match.team2,
				team2_id, self.team2_name)
		self._assert_displayed_match_streamer(displayed_match.streamers[0],
				streamer_id, self.streamer_name,
				common_db._get_steam_url_by_id(streamer_steam_id))
		# Assert that the user's calendar is empty.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)
	
	"""Test that adds and removes a star for a team in a match that is not casted.
	"""
	def test_add_remove_team_star_not_casted(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)
		# Create the match.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_url, self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_url, self.team2_fingerprint)
		match_id = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_url, self.match_fingerprint, now=None)

		# Add a star for team2.
		db.add_star_team(client_id, team2_id, now=self.now)
		# Assert that the team has a star.
		displayed_team = db.get_displayed_team(client_id, team2_id)
		self._assert_displayed_team(displayed_team,
				team2_id, self.team2_name, self.game, self.league,
				is_starred=True, num_stars=1, num_matches=1)
		self._assert_displayed_team_match(displayed_team.matches[0],
				team1_id, self.team1_name, match_id, self.time)
		# Assert that the user's calendar is empty.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)
		
		# Add a star for team2 again.
		with self.assertRaises(common_db.DbException):
			db.add_star_team(client_id, team2_id, now=self.now)
		# Assert that this had no effect.
		displayed_team = db.get_displayed_team(client_id, team2_id)
		self._assert_displayed_team(displayed_team,
				team2_id, self.team2_name, self.game, self.league,
				is_starred=True, num_stars=1, num_matches=1)
		self._assert_displayed_team_match(displayed_team.matches[0],
				team1_id, self.team1_name, match_id, self.time)
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)
		
		# Remove the star for team2.
		db.remove_star_team(client_id, team2_id, now=self.now)
		# Assert that team2 no longer has a star.
		displayed_team = db.get_displayed_team(client_id, team2_id)
		self._assert_displayed_team(displayed_team,
				team2_id, self.team2_name, self.game, self.league, num_matches=1)
		self._assert_displayed_team_match(displayed_team.matches[0],
				team1_id, self.team1_name, match_id, self.time)
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)
	
		# Remove the star for team2 again.
		db.remove_star_team(client_id, team2_id, now=self.now)
		# Assert that this had no effect.
		displayed_team = db.get_displayed_team(client_id, team2_id)
		self._assert_displayed_team(displayed_team,
				team2_id, self.team2_name, self.game, self.league, num_matches=1)
		self._assert_displayed_team_match(displayed_team.matches[0],
				team1_id, self.team1_name, match_id, self.time)
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)
	
	"""Test that adds and removes a star for a team in a match that is casted.
	"""
	def test_add_remove_team_star_casted(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)
		# Create the match.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_url, self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_url, self.team2_fingerprint)
		match_id = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_url, self.match_fingerprint, now=None)

		# Create the streaming user.
		streamer_steam_id, streamer_id = self._create_steam_user(self.streamer_name)
		# Stream the match.
		db.add_stream_match(streamer_id, match_id)

		# Add a star for team2.
		db.add_star_team(client_id, team2_id, now=self.now)
		# Assert that the team has a star.
		displayed_team = db.get_displayed_team(client_id, team2_id)
		self._assert_displayed_team(displayed_team,
				team2_id, self.team2_name, self.game, self.league,
				is_starred=True, num_stars=1, num_matches=1)
		self._assert_displayed_team_match(displayed_team.matches[0],
				team1_id, self.team1_name, match_id, self.time, num_streams=1)
		# Assert that the user's calendar has the match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		self._assert_displayed_calendar_match(displayed_calendar.next_match,
				match_id, team1_id, self.team1_name, team2_id, self.team2_name,
				self.time, self.game, self.league, num_streams=1)

		# Remove the star for team2.
		db.remove_star_team(client_id, team2_id, now=self.now)
		# Assert that team2 no longer has a star.
		displayed_team = db.get_displayed_team(client_id, team2_id)
		self._assert_displayed_team(displayed_team,
				team2_id, self.team2_name, self.game, self.league, num_matches=1)
		self._assert_displayed_team_match(displayed_team.matches[0],
				team1_id, self.team1_name, match_id, self.time, num_streams=1)
		# Assert that the user's calendar is empty.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)
	
	"""Test that adds and removes a star for a streamer that is not casting a
	match.
	"""
	def test_add_remove_streamer_star_not_casted(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)
		# Create the streaming user.
		streamer_steam_id, streamer_id = self._create_steam_user(self.streamer_name)

		# Add a star for the streamer.
		db.add_star_streamer(client_id, streamer_id, now=self.now)
		# Assert that the streamer has a star.
		displayed_streamer = db.get_displayed_streamer(client_id, streamer_id)
		self._assert_displayed_streamer(displayed_streamer,
				streamer_id, self.streamer_name, is_starred=True, num_stars=1)
		# Assert that the user's calendar is empty.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)

		# Add the star for the streamer again.
		with self.assertRaises(common_db.DbException):
			db.add_star_streamer(client_id, streamer_id, now=self.now)
		# Assert that this had no effect.
		displayed_streamer = db.get_displayed_streamer(client_id, streamer_id)
		self._assert_displayed_streamer(displayed_streamer,
				streamer_id, self.streamer_name, is_starred=True, num_stars=1)
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)
	
		# Remove the star for the streamer.
		db.remove_star_streamer(client_id, streamer_id, now=self.now)
		# Assert that the streamer no longer has a star.
		displayed_streamer = db.get_displayed_streamer(client_id, streamer_id)
		self._assert_displayed_streamer(displayed_streamer,
				streamer_id, self.streamer_name)
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)

		# Remove the star for the streamer.
		db.remove_star_streamer(client_id, streamer_id, now=self.now)
		# Assert that this had no effect.
		displayed_streamer = db.get_displayed_streamer(client_id, streamer_id)
		self._assert_displayed_streamer(displayed_streamer,
				streamer_id, self.streamer_name)
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)

	"""Test that adds and removes a star for a streamer that is casting a match.
	"""
	def test_add_remove_streamer_star_casted(self):
		pass
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)
		# Create the streaming user.
		streamer_steam_id, streamer_id = self._create_steam_user(self.streamer_name)
		# Create the match.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_url, self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_url, self.team2_fingerprint)
		match_id = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_url, self.match_fingerprint, now=None)

		# Create the streaming user.
		streamer_steam_id, streamer_id = self._create_steam_user(self.streamer_name)
		# Stream the match.
		db.add_stream_match(streamer_id, match_id)

		# Add a star for the streamer.
		db.add_star_streamer(client_id, streamer_id, now=self.now)
		# Assert that the streamer has a star.
		displayed_streamer = db.get_displayed_streamer(client_id, streamer_id)
		self._assert_displayed_streamer(displayed_streamer,
				streamer_id, self.streamer_name,
				is_starred=True, num_stars=1, num_matches=1)
		self._assert_displayed_streamer_match(displayed_streamer.matches[0],
				match_id, team1_id, self.team1_name, team2_id, self.team2_name,
				self.time, self.game, self.league, num_streams=1)
		# Assert that the user's calendar has the match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		self._assert_displayed_calendar_match(displayed_calendar.next_match,
				match_id, team1_id, self.team1_name, team2_id, self.team2_name,
				self.time, self.game, self.league, num_stars=0, num_streams=1)

		# Remove the star for the streamer.
		db.remove_star_streamer(client_id, streamer_id, now=self.now)
		# Assert that the streamer no longer has a star.
		displayed_streamer = db.get_displayed_streamer(client_id, streamer_id)
		self._assert_displayed_streamer(displayed_streamer,
				streamer_id, self.streamer_name, num_matches=1)
		# Assert that the user's calendar is empty.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)

	def _remove_multi_stars(self, client_id, streamer_id,
			team1_id, team2_id, match_id):
		# Assert that the user's calendar has the match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		self._assert_displayed_calendar_match(displayed_calendar.next_match,
				match_id, team1_id, self.team1_name, team2_id, self.team2_name,
				self.time, self.game, self.league, num_stars=1, num_streams=1)
		
		# Remove the star for the match.
		db.remove_star_match(client_id, match_id, now=self.now)
		# Assert that the user's calendar still has the match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		self._assert_displayed_calendar_match(displayed_calendar.next_match,
				match_id, team1_id, self.team1_name, team2_id, self.team2_name,
				self.time, self.game, self.league, num_streams=1)
	
		# Remove the star for both teams.
		db.remove_star_team(client_id, team1_id, now=self.now)
		db.remove_star_team(client_id, team2_id, now=self.now)
		# Assert that the user's calendar still has the match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		self._assert_displayed_calendar_match(displayed_calendar.next_match,
				match_id, team1_id, self.team1_name, team2_id, self.team2_name,
				self.time, self.game, self.league, num_streams=1)
	
		# Remove the star from the streamer.
		db.remove_star_streamer(client_id, streamer_id, now=self.now)
		# Assert that the user's calendar is empty.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)

		# Assert that the match should no longer have a star.
		displayed_match = db.get_displayed_match(client_id, match_id)
		self._assert_displayed_match(displayed_match,
				match_id, self.time, self.game, self.league, num_streamers=1)
		self._assert_displayed_match_team(displayed_match.team1,
				team1_id, self.team1_name)
		self._assert_displayed_match_team(displayed_match.team2,
				team2_id, self.team2_name)
		# Assert that team1 no longer has a star.
		displayed_team = db.get_displayed_team(client_id, team1_id)
		self._assert_displayed_team(displayed_team,
				team1_id, self.team1_name, self.game, self.league, num_matches=1)
		self._assert_displayed_team_match(displayed_team.matches[0],
				team2_id, self.team2_name, match_id, self.time, num_streams=1)
		# Assert that team2 no longer has a star.
		displayed_team = db.get_displayed_team(client_id, team2_id)
		self._assert_displayed_team(displayed_team,
				team2_id, self.team2_name, self.game, self.league, num_matches=1)
		self._assert_displayed_team_match(displayed_team.matches[0],
				team1_id, self.team1_name, match_id, self.time, num_streams=1)
		# The streamer should no longer have a star.
		displayed_streamer = db.get_displayed_streamer(client_id, streamer_id)
		self._assert_displayed_streamer(displayed_streamer,
				streamer_id, self.streamer_name, num_matches=1)
		self._assert_displayed_streamer_match(displayed_streamer.matches[0],
				match_id, team1_id, self.team1_name, team2_id, self.team2_name,
				self.time, self.game, self.league, num_streams=1)

	"""Test that adds stars to all match components, and then adds a user
	streaming the match before removing all stars.
	"""
	def test_add_multi_stars_then_stream(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)

		# Create the match.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_url, self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_url, self.team2_fingerprint)
		match_id = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_url, self.match_fingerprint, now=None)
		# Create the streaming user.
		streamer_steam_id, streamer_id = self._create_steam_user(self.streamer_name)

		# Add a star for the match.
		db.add_star_match(client_id, match_id, now=self.now)
		# Add a star for both teams.
		db.add_star_team(client_id, team1_id, now=self.now)
		db.add_star_team(client_id, team2_id, now=self.now)
		# Add a star for the streamer.
		db.add_star_streamer(client_id, streamer_id, now=self.now)

		# Stream the match.
		db.add_stream_match(streamer_id, match_id)

		# Remove all the stars.
		self._remove_multi_stars(client_id, streamer_id, team1_id, team2_id, match_id)

	"""Test that adds a user streaming a match, and then adds stars to all match
	components before removing all stars.
	"""
	def test_stream_then_add_multi_stars(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)

		# Create the match.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_url, self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_url, self.team2_fingerprint)
		match_id = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_url, self.match_fingerprint, now=None)
		# Create the streaming user.
		streamer_steam_id, streamer_id = self._create_steam_user(self.streamer_name)

		# Stream the match.
		db.add_stream_match(streamer_id, match_id)

		# Add a star for the match.
		db.add_star_match(client_id, match_id, now=self.now)
		# Add a star for both teams.
		db.add_star_team(client_id, team1_id, now=self.now)
		db.add_star_team(client_id, team2_id, now=self.now)
		# Add a star for the streamer.
		db.add_star_streamer(client_id, streamer_id, now=self.now)

		# Remove all the stars.
		self._remove_multi_stars(client_id, streamer_id, team1_id, team2_id, match_id)

	"""Test that adds and removes multiple streamers for a casted match.
	"""
	def test_add_remove_multi_streamers(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)

		# Create the match.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_url, self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_url, self.team2_fingerprint)
		match_id = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_url, self.match_fingerprint, now=None)
		# Add a star for the match.
		db.add_star_match(client_id, match_id, now=self.now)

		# Create the first streaming user.
		streamer_steam_id1, streamer_id1 = self._create_steam_user(self.streamer_name)
		# Create the second streaming user.
		streamer_name2 = 'streamer_name2'
		streamer_steam_id2, streamer_id2 = self._create_steam_user(streamer_name2)

		# The first streamer streams the match.
		db.add_stream_match(streamer_id1, match_id)
		# Assert that the user's calendar has the match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		self._assert_displayed_calendar_match(displayed_calendar.next_match,
				match_id, team1_id, self.team1_name, team2_id, self.team2_name,
				self.time, self.game, self.league, num_stars=1, num_streams=1)
	
		# The second streamer streams the match.
		db.add_stream_match(streamer_id2, match_id)
		# Assert that the user's calendar still has the match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		self._assert_displayed_calendar_match(displayed_calendar.next_match,
				match_id, team1_id, self.team1_name, team2_id, self.team2_name,
				self.time, self.game, self.league, num_stars=1, num_streams=2)
	
		# The first streamer is no longer streaming the match.
		db.remove_stream_match(streamer_id1, match_id)
		# Assert that the user's calendar still has the match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		self._assert_displayed_calendar_match(displayed_calendar.next_match,
				match_id, team1_id, self.team1_name, team2_id, self.team2_name,
				self.time, self.game, self.league, num_stars=1, num_streams=1)

		# The second streamer is no longer streaming the match.
		db.remove_stream_match(streamer_id2, match_id)
		# Assert that the user's calendar is empty.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)

	# TODO: Test remove_stream_match.

	"""Tests pagination of matches when displaying the client's viewing calendar.
	"""
	def test_get_displayed_calendar_pagination(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)
		# Create the teams.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_url, self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_url, self.team2_fingerprint)
		# Add stars for both teams.
		db.add_star_team(client_id, team1_id)
		db.add_star_team(client_id, team2_id)

		# The second and third matches happen at the same time.
		time2 = self.time + timedelta(days=1)
		time3 = time2
		time4 = time3 + timedelta(days=1)
		time5 = time4 + timedelta(days=1)
		# Create the matches.
		match_url2 = 'match_url2'
		match_url3 = 'match_url3'
		match_url4 = 'match_url4'
		match_url5 = 'match_url5'
		match_fingerprint2 = 'match_fingerprint2'
		match_fingerprint3 = 'match_fingerprint3'
		match_fingerprint4 = 'match_fingerprint4'
		match_fingerprint5 = 'match_fingerprint5'
		match_id1 = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_url, self.match_fingerprint, now=None)
		match_id2 = db.add_match(team1_id, team2_id, time2, self.game, self.league,
				match_url2, match_fingerprint2, now=None)
		match_id3 = db.add_match(team1_id, team2_id, time3, self.game, self.league,
				match_url3, match_fingerprint3, now=None)
		match_id4 = db.add_match(team1_id, team2_id, time4, self.game, self.league,
				match_url4, match_fingerprint4, now=None)
		match_id5 = db.add_match(team1_id, team2_id, time5, self.game, self.league,
				match_url5, match_fingerprint5, now=None)

		# Create the streaming user.
		streamer_steam_id, streamer_id = self._create_steam_user(self.streamer_name)
		# Stream all matches.
		for match_id in (match_id1, match_id2, match_id3, match_id4, match_id5):
			db.add_stream_match(streamer_id, match_id)

		def _get_next_page():
			return db.get_displayed_viewer_calendar(client_id, page_limit=2,
					next_time=displayed_calendar.next_time,
					next_match_id=displayed_calendar.next_match_id)

		def _get_prev_page():
			return db.get_displayed_viewer_calendar(client_id, page_limit=2,
					prev_time=displayed_calendar.prev_time,
					prev_match_id=displayed_calendar.prev_match_id)

		def _assert_next_match():
			self._assert_displayed_calendar_match(displayed_calendar.next_match,
					match_id1, team1_id, self.team1_name, team2_id, self.team2_name,
					self.time, self.game, self.league, num_streams=1)

		def _assert_first_page():
			self.assertEqual(2, len(displayed_calendar.matches))
			self._assert_displayed_calendar(displayed_calendar,
					has_next_match=True, num_matches=2,
					next_time=time2, next_match_id=match_id2)
			_assert_next_match()
			# Assert the partial list of paginated matches.
			self._assert_displayed_calendar_match(displayed_calendar.matches[0],
					match_id1, team1_id, self.team1_name, team2_id, self.team2_name,
					self.time, self.game, self.league, num_streams=1)
			self._assert_displayed_calendar_match(displayed_calendar.matches[1],
					match_id2, team1_id, self.team1_name, team2_id, self.team2_name,
					time2, self.game, self.league, num_streams=1)

		def _assert_second_page():
			self.assertEqual(2, len(displayed_calendar.matches))
			self._assert_displayed_calendar(displayed_calendar,
					has_next_match=True, num_matches=2,
					prev_time=time3, prev_match_id=match_id3,
					next_time=time4, next_match_id=match_id4)
			_assert_next_match()
			# Assert the partial list of paginated matches.
			self._assert_displayed_calendar_match(displayed_calendar.matches[0],
					match_id3, team1_id, self.team1_name, team2_id, self.team2_name,
					time3, self.game, self.league, num_streams=1)
			self._assert_displayed_calendar_match(displayed_calendar.matches[1],
					match_id4, team1_id, self.team1_name, team2_id, self.team2_name,
					time4, self.game, self.league, num_streams=1)

		def _assert_third_page():
			self.assertEqual(1, len(displayed_calendar.matches))
			self._assert_displayed_calendar(displayed_calendar,
					has_next_match=True, num_matches=1,
					prev_time=time5, prev_match_id=match_id5)
			_assert_next_match()
			# Assert the partial list of paginated matches.
			self._assert_displayed_calendar_match(displayed_calendar.matches[0],
					match_id5, team1_id, self.team1_name, team2_id, self.team2_name,
					time5, self.game, self.league, num_streams=1)

		# Assert that, clicking Next, the pages are correct.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id, page_limit=2)
		_assert_first_page()
		displayed_calendar = _get_next_page()
		_assert_second_page()
		displayed_calendar = _get_next_page()
		_assert_third_page()

		# Assert that, clicking Previous, the pages are correct.
		displayed_calendar = _get_prev_page()
		_assert_second_page()
		displayed_calendar = _get_prev_page()
		_assert_first_page()

	"""Tests pagination of matches when displaying the client's streaming calendar.
	"""
	def test_get_displayed_streamer_calendar_pagination(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)
		# Create the teams.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_url, self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_url, self.team2_fingerprint)

		# The second and third matches happen at the same time.
		time2 = self.time + timedelta(days=1)
		time3 = time2
		time4 = time3 + timedelta(days=1)
		time5 = time4 + timedelta(days=1)
		# Create the matches.
		match_url2 = 'match_url2'
		match_url3 = 'match_url3'
		match_url4 = 'match_url4'
		match_url5 = 'match_url5'
		match_fingerprint2 = 'match_fingerprint2'
		match_fingerprint3 = 'match_fingerprint3'
		match_fingerprint4 = 'match_fingerprint4'
		match_fingerprint5 = 'match_fingerprint5'
		match_id1 = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_url, self.match_fingerprint, now=None)
		match_id2 = db.add_match(team1_id, team2_id, time2, self.game, self.league,
				match_url2, match_fingerprint2, now=None)
		match_id3 = db.add_match(team1_id, team2_id, time3, self.game, self.league,
				match_url3, match_fingerprint3, now=None)
		match_id4 = db.add_match(team1_id, team2_id, time4, self.game, self.league,
				match_url4, match_fingerprint4, now=None)
		match_id5 = db.add_match(team1_id, team2_id, time5, self.game, self.league,
				match_url5, match_fingerprint5, now=None)

		# The client streams all matches.
		for match_id in (match_id1, match_id2, match_id3, match_id4, match_id5):
			db.add_stream_match(client_id, match_id)

		def _get_next_page():
			return db.get_displayed_streamer_calendar(client_id, page_limit=2,
					next_time=displayed_calendar.next_time,
					next_match_id=displayed_calendar.next_match_id)
			
		def _get_prev_page():
			return db.get_displayed_streamer_calendar(client_id, page_limit=2,
					prev_time=displayed_calendar.prev_time,
					prev_match_id=displayed_calendar.prev_match_id)

		def _assert_next_match():
			self._assert_displayed_calendar_match(displayed_calendar.next_match,
					match_id1, team1_id, self.team1_name, team2_id, self.team2_name,
					self.time, self.game, self.league, num_streams=1)

		def _assert_first_page():
			self._assert_displayed_calendar(displayed_calendar,
					has_next_match=True, num_matches=2,
					next_time=time2, next_match_id=match_id2)
			_assert_next_match()
			# Assert the partial list of paginated matches.
			self._assert_displayed_calendar_match(displayed_calendar.matches[0],
					match_id1, team1_id, self.team1_name, team2_id, self.team2_name,
					self.time, self.game, self.league, num_streams=1)
			self._assert_displayed_calendar_match(displayed_calendar.matches[1],
					match_id2, team1_id, self.team1_name, team2_id, self.team2_name,
					time2, self.game, self.league, num_streams=1)

		def _assert_second_page():
			self._assert_displayed_calendar(displayed_calendar,
					has_next_match=True, num_matches=2,
					prev_time=time3, prev_match_id=match_id3,
					next_time=time4, next_match_id=match_id4)
			_assert_next_match()
			# Assert the partial list of paginated matches.
			self._assert_displayed_calendar_match(displayed_calendar.matches[0],
					match_id3, team1_id, self.team1_name, team2_id, self.team2_name,
					time3, self.game, self.league, num_streams=1)
			self._assert_displayed_calendar_match(displayed_calendar.matches[1],
					match_id4, team1_id, self.team1_name, team2_id, self.team2_name,
					time4, self.game, self.league, num_streams=1)

		def _assert_third_page():
			self._assert_displayed_calendar(displayed_calendar,
					has_next_match=True, num_matches=1,
					prev_time=time5, prev_match_id=match_id5)
			_assert_next_match()
			# Assert the partial list of paginated matches.
			self._assert_displayed_calendar_match(displayed_calendar.matches[0],
					match_id5, team1_id, self.team1_name, team2_id, self.team2_name,
					time5, self.game, self.league, num_streams=1)

		# Assert that, clicking Next, the pages are correct.
		displayed_calendar = db.get_displayed_streamer_calendar(client_id, page_limit=2)
		_assert_first_page()
		displayed_calendar = _get_next_page()
		_assert_second_page()
		displayed_calendar = _get_next_page()
		_assert_third_page()

		# Assert that, clicking Previous, the pages are correct.
		displayed_calendar = _get_prev_page()
		_assert_second_page()
		displayed_calendar = _get_prev_page()
		_assert_first_page()

	"""Tests pagination of streamers when displaying a match.
	"""
	def test_get_displayed_match_pagination(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)
		# Create the match.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_url, self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_url, self.team2_fingerprint)
		match_id = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_url, self.match_fingerprint, now=None)

		# Create the streamers.
		streamer_steam_id1, streamer_id1 = self._create_steam_user(self.streamer_name)
		streamer_name2 = 'streamer_name2'
		streamer_steam_id2, streamer_id2 = self._create_steam_user(streamer_name2)
		streamer_name3 = 'streamer_name3'
		streamer_steam_id3, streamer_id3 = self._create_steam_user(streamer_name3)
		streamer_name4 = 'streamer_name4'
		streamer_steam_id4, streamer_id4 = self._create_steam_user(streamer_name4)
		streamer_name5 = 'streamer_name5'
		streamer_steam_id5, streamer_id5 = self._create_steam_user(streamer_name5)
		# Stream the match.
		streamer_added_time1 = self.now + timedelta(minutes=1)
		db.add_stream_match(streamer_id1, match_id, now=streamer_added_time1)
		streamer_added_time2 = self.now + timedelta(minutes=2)
		db.add_stream_match(streamer_id2, match_id, now=streamer_added_time2)
		streamer_added_time3 = self.now + timedelta(minutes=3)
		db.add_stream_match(streamer_id3, match_id, now=streamer_added_time3)
		streamer_added_time4 = self.now + timedelta(minutes=4)
		db.add_stream_match(streamer_id4, match_id, now=streamer_added_time4)
		streamer_added_time5 = self.now + timedelta(minutes=5)
		db.add_stream_match(streamer_id5, match_id, now=streamer_added_time5)

		def _get_next_page():
			return db.get_displayed_match(client_id, match_id, page_limit=2,
					next_time=displayed_match.next_time,
					next_streamer_id=displayed_match.next_streamer_id)

		def _get_prev_page():
			return db.get_displayed_match(client_id, match_id, page_limit=2,
					prev_time=displayed_match.prev_time,
					prev_streamer_id=displayed_match.prev_streamer_id)

		def _assert_first_page():
			self.assertEqual(2, len(displayed_match.streamers))
			self._assert_displayed_match(displayed_match,
					match_id, self.time, self.game, self.league, num_streamers=2,
					next_time=streamer_added_time2, next_streamer_id=streamer_id2)
			# Assert the partial list of paginated streamers.
			self._assert_displayed_match_streamer(displayed_match.streamers[0],
					streamer_id1, self.streamer_name,
					common_db._get_steam_url_by_id(streamer_steam_id1))
			self._assert_displayed_match_streamer(displayed_match.streamers[1],
					streamer_id2, streamer_name2,
					common_db._get_steam_url_by_id(streamer_steam_id2))

		def _assert_second_page():
			self.assertEqual(2, len(displayed_match.streamers))
			self._assert_displayed_match(displayed_match,
					match_id, self.time, self.game, self.league, num_streamers=2,
					prev_time=streamer_added_time3, prev_streamer_id=streamer_id3,
					next_time=streamer_added_time4, next_streamer_id=streamer_id4)
			# Assert the partial list of paginated streamers.
			self._assert_displayed_match_streamer(displayed_match.streamers[0],
					streamer_id3, streamer_name3,
					common_db._get_steam_url_by_id(streamer_steam_id3))
			self._assert_displayed_match_streamer(displayed_match.streamers[1],
					streamer_id4, streamer_name4,
					common_db._get_steam_url_by_id(streamer_steam_id4))

		def _assert_third_page():
			self.assertEqual(1, len(displayed_match.streamers))
			self._assert_displayed_match(displayed_match,
					match_id, self.time, self.game, self.league, num_streamers=1,
					prev_time=streamer_added_time5, prev_streamer_id=streamer_id5)
			# Assert the partial list of paginated streamers.
			self._assert_displayed_match_streamer(displayed_match.streamers[0],
					streamer_id5, streamer_name5,
					common_db._get_steam_url_by_id(streamer_steam_id5))

		# Assert that, clicking Next, the pages are correct.
		displayed_match = db.get_displayed_match(client_id, match_id, page_limit=2)
		_assert_first_page()
		displayed_match = _get_next_page()
		_assert_second_page()
		displayed_match = _get_next_page()
		_assert_third_page()

		# Assert that, clicking Previous, the pages are correct.
		displayed_match = _get_prev_page()
		_assert_second_page()
		displayed_match = _get_prev_page()
		_assert_first_page()

	"""Tests pagination of matches when displaying a team.
	"""
	def test_get_displayed_team_pagination(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)
		# Create the teams.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_url, self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_url, self.team2_fingerprint)
		team3_name = 'team3_name'
		team3_url = 'team3_url'
		team3_fingerprint = 'team3_fingerprint'
		team3_id = db.add_team(team3_name, self.game, self.league,
				team3_url, team3_fingerprint)

		# The second and third matches happen at the same time.
		time2 = self.time + timedelta(days=1)
		time3 = time2
		time4 = time3 + timedelta(days=1)
		time5 = time4 + timedelta(days=1)
		# Create the matches.
		match_url2 = 'match_url2'
		match_url3 = 'match_url3'
		match_url4 = 'match_url4'
		match_url5 = 'match_url5'
		match_fingerprint2 = 'match_fingerprint2'
		match_fingerprint3 = 'match_fingerprint3'
		match_fingerprint4 = 'match_fingerprint4'
		match_fingerprint5 = 'match_fingerprint5'
		match_id1 = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_url, self.match_fingerprint, now=None)
		match_id2 = db.add_match(team1_id, team3_id, time2, self.game, self.league,
				match_url2, match_fingerprint2, now=None)
		match_id3 = db.add_match(team1_id, team3_id, time3, self.game, self.league,
				match_url3, match_fingerprint3, now=None)
		match_id4 = db.add_match(team1_id, team2_id, time4, self.game, self.league,
				match_url4, match_fingerprint4, now=None)
		match_id5 = db.add_match(team1_id, team3_id, time5, self.game, self.league,
				match_url5, match_fingerprint5, now=None)
	
		def _get_next_page():
			return db.get_displayed_team(client_id, team1_id, page_limit=2,
					next_time=displayed_team.next_time,
					next_match_id=displayed_team.next_match_id)
		
		def _get_prev_page():
			return db.get_displayed_team(client_id, team1_id, page_limit=2,
					prev_time=displayed_team.prev_time,
					prev_match_id=displayed_team.prev_match_id)
	
		def _assert_first_page():
			self.assertEqual(2, len(displayed_team.matches))
			self._assert_displayed_team(displayed_team,
					team1_id, self.team1_name, self.game, self.league, num_matches=5,
					next_time=time2, next_match_id=match_id2)
			# Assert the partial list of paginated matches.
			self._assert_displayed_team_match(displayed_team.matches[0],
					team2_id, self.team2_name, match_id1, self.time)
			self._assert_displayed_team_match(displayed_team.matches[1],
					team3_id, team3_name, match_id2, time2)

		def _assert_second_page():		
			self.assertEqual(2, len(displayed_team.matches))
			self._assert_displayed_team(displayed_team,
					team1_id, self.team1_name, self.game, self.league, num_matches=5,
					prev_time=time3, prev_match_id=match_id3,
					next_time=time4, next_match_id=match_id4)
			# Assert the partial list of paginated matches.
			self._assert_displayed_team_match(displayed_team.matches[0],
					team3_id, team3_name, match_id3, time3)
			self._assert_displayed_team_match(displayed_team.matches[1],
					team2_id, self.team2_name, match_id4, time4)

		def _assert_third_page():
			self.assertEqual(1, len(displayed_team.matches))
			self._assert_displayed_team(displayed_team,
					team1_id, self.team1_name, self.game, self.league, num_matches=5,
					prev_time=time5, prev_match_id=match_id5)
			# Assert the partial list of paginated matches.
			self._assert_displayed_team_match(displayed_team.matches[0],
					team3_id, team3_name, match_id5, time5)

		# Assert that, clicking Next, the pages are correct.
		displayed_team = db.get_displayed_team(client_id, team1_id, page_limit=2)
		_assert_first_page()
		displayed_team = _get_next_page()
		_assert_second_page()
		displayed_team = _get_next_page()
		_assert_third_page()

		# Assert that, clicking Previous, the pages are correct.
		displayed_team = _get_prev_page()
		_assert_second_page()
		displayed_team = _get_prev_page()
		_assert_first_page()

	"""Tests pagination of matches when displaying a streaming user.
	"""
	def test_get_displayed_streamer_pagination(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)
		# Create the teams.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_url, self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_url, self.team2_fingerprint)

		# The second and third matches happen at the same time.
		time2 = self.time + timedelta(days=1)
		time3 = time2
		time4 = time3 + timedelta(days=1)
		time5 = time4 + timedelta(days=1)
		# Create the matches.
		match_url2 = 'match_url2'
		match_url3 = 'match_url3'
		match_url4 = 'match_url4'
		match_url5 = 'match_url5'
		match_fingerprint2 = 'match_fingerprint2'
		match_fingerprint3 = 'match_fingerprint3'
		match_fingerprint4 = 'match_fingerprint4'
		match_fingerprint5 = 'match_fingerprint5'
		match_id1 = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_url, self.match_fingerprint, now=None)
		match_id2 = db.add_match(team1_id, team2_id, time2, self.game, self.league,
				match_url2, match_fingerprint2, now=None)
		match_id3 = db.add_match(team1_id, team2_id, time3, self.game, self.league,
				match_url3, match_fingerprint3, now=None)
		match_id4 = db.add_match(team1_id, team2_id, time4, self.game, self.league,
				match_url4, match_fingerprint4, now=None)
		match_id5 = db.add_match(team1_id, team2_id, time5, self.game, self.league,
				match_url5, match_fingerprint5, now=None)

		# Create the streaming user.
		streamer_steam_id, streamer_id = self._create_steam_user(self.streamer_name)
		# Stream all matches.
		for match_id in (match_id1, match_id2, match_id3, match_id4, match_id5):
			db.add_stream_match(streamer_id, match_id)

		def _get_next_page():
			return db.get_displayed_streamer(client_id, streamer_id, page_limit=2,
					next_time=displayed_streamer.next_time,
					next_match_id=displayed_streamer.next_match_id)

		def _get_prev_page():
			return db.get_displayed_streamer(client_id, streamer_id, page_limit=2,
					prev_time=displayed_streamer.prev_time,
					prev_match_id=displayed_streamer.prev_match_id)

		def _assert_first_page():
			self.assertEqual(2, len(displayed_streamer.matches))
			self._assert_displayed_streamer(displayed_streamer,
					streamer_id, self.streamer_name, num_matches=5,
					next_time=time2, next_match_id=match_id2)
			# Assert the partial list of paginated matches.
			self._assert_displayed_streamer_match(displayed_streamer.matches[0],
					match_id1, team1_id, self.team1_name, team2_id, self.team2_name,
					self.time, self.game, self.league, num_streams=1)
			self._assert_displayed_streamer_match(displayed_streamer.matches[1],
					match_id2, team1_id, self.team1_name, team2_id, self.team2_name,
					time2, self.game, self.league, num_streams=1)

		def _assert_second_page():
			self.assertEqual(2, len(displayed_streamer.matches))
			self._assert_displayed_streamer(displayed_streamer,
					streamer_id, self.streamer_name, num_matches=5,
					prev_time=time3, prev_match_id=match_id3,
					next_time=time4, next_match_id=match_id4)
			# Assert the partial list of paginated matches.
			self._assert_displayed_streamer_match(displayed_streamer.matches[0],
					match_id3, team1_id, self.team1_name, team2_id, self.team2_name,
					time3, self.game, self.league, num_streams=1)
			self._assert_displayed_streamer_match(displayed_streamer.matches[1],
					match_id4, team1_id, self.team1_name, team2_id, self.team2_name,
					time4, self.game, self.league, num_streams=1)

		def _assert_third_page():
			self.assertEqual(1, len(displayed_streamer.matches))
			self._assert_displayed_streamer(displayed_streamer,
					streamer_id, self.streamer_name, num_matches=5,
					prev_time=time5, prev_match_id=match_id5)
			# Assert the partial list of paginated matches.
			self._assert_displayed_streamer_match(displayed_streamer.matches[0],
					match_id5, team1_id, self.team1_name, team2_id, self.team2_name,
					time5, self.game, self.league, num_streams=1)

		# Assert that, clicking Next, the pages are correct.
		displayed_streamer = db.get_displayed_streamer(client_id, streamer_id, page_limit=2)
		_assert_first_page()
		displayed_streamer = _get_next_page()
		_assert_second_page()
		displayed_streamer = _get_next_page()
		_assert_third_page()

		# Assert that, clicking Previous, the pages are correct.
		displayed_streamer = _get_prev_page()
		_assert_second_page()
		displayed_streamer = _get_prev_page()
		_assert_first_page()

	"""Tests pagination when displaying all matches.
	"""
	def test_get_all_matches_pagination(self):
		# TODO
		pass
	
	def _assert_displayed_team_list_entry(self, displayed_team_list_entry,
			team_id, name, game, league):
		# Begin required arguments.
		self.assertEqual(team_id, displayed_team_list_entry.team_id)
		self.assertEqual(name, displayed_team_list_entry.name)
		self.assertEqual(game, displayed_team_list_entry.game)
		self.assertEqual(league, displayed_team_list_entry.league)

	def _assert_displayed_team_list(self, displayed_team_list, num_teams=0,
			prev_name=None, prev_team_id=None, next_name=None, next_team_id=None):
		# Begin optional arguments.
		self.assertEqual(num_teams, len(displayed_team_list.teams))
		self.assertEqual(prev_name, displayed_team_list.prev_name)
		self.assertEqual(prev_team_id, displayed_team_list.prev_team_id)
		self.assertEqual(next_name, displayed_team_list.next_name)
		self.assertEqual(next_team_id, displayed_team_list.next_team_id)

	"""Tests pagination when displaying all teams.
	"""
	def test_get_all_teams_pagination(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)
		# Create the teams.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_url, self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_url, self.team2_fingerprint)
		team3_name = 'team3_name'
		team3_url = 'team3_url'
		team3_fingerprint = 'team3_fingerprint'
		team3_id = db.add_team(team3_name, self.game, self.league,
				team3_url, team3_fingerprint)
		team4_name = 'team4_name'
		team4_url = 'team4_url'
		team4_fingerprint = 'team4_fingerprint'
		team4_id = db.add_team(team4_name, self.game, self.league,
				team4_url, team4_fingerprint)
		team5_name = 'team5_name'
		team5_url = 'team5_url'
		team5_fingerprint = 'team5_fingerprint'
		team5_id = db.add_team(team5_name, self.game, self.league,
				team5_url, team5_fingerprint)

		def _get_next_page():
			return db.get_all_teams(client_id, page_limit=2,
					next_name=displayed_teams.next_name,
					next_team_id=displayed_teams.next_team_id)
		
		def _get_prev_page():
			return db.get_all_teams(client_id, page_limit=2,
					prev_name=displayed_teams.prev_name,
					prev_team_id=displayed_teams.prev_team_id)

		def _assert_first_page():
			self._assert_displayed_team_list(displayed_teams, num_teams=2,
					next_name=self.team2_name, next_team_id=team2_id)
			# Assert the partial list of paginated teams.
			self._assert_displayed_team_list_entry(displayed_teams.teams[0],
					team1_id, self.team1_name, self.game, self.league)
			self._assert_displayed_team_list_entry(displayed_teams.teams[1],
					team2_id, self.team2_name, self.game, self.league)

		def _assert_second_page():
			self._assert_displayed_team_list(displayed_teams, num_teams=2,
					prev_name=team3_name, prev_team_id=team3_id,
					next_name=team4_name, next_team_id=team4_id)
			# Assert the partial list of paginated teams.
			self._assert_displayed_team_list_entry(displayed_teams.teams[0],
					team3_id, team3_name, self.game, self.league)
			self._assert_displayed_team_list_entry(displayed_teams.teams[1],
					team4_id, team4_name, self.game, self.league)

		def _assert_third_page():
			self._assert_displayed_team_list(displayed_teams, num_teams=1,
					prev_name=team5_name, prev_team_id=team5_id)
			# Assert the partial list of paginated teams.
			self._assert_displayed_team_list_entry(displayed_teams.teams[0],
					team5_id, team5_name, self.game, self.league)

		# Assert that, clicking Next, the pages are correct.
		displayed_teams = db.get_all_teams(client_id, page_limit=2)
		_assert_first_page()
		displayed_teams = _get_next_page()
		_assert_second_page()
		displayed_teams = _get_next_page()
		_assert_third_page()

		# Assert that, clicking Previous, the pages are correct.
		displayed_teams = _get_prev_page()
		_assert_second_page()
		displayed_teams = _get_prev_page()
		_assert_first_page()
	
	def _assert_displayed_streamer_list_entry(self, displayed_streamer_list_entry,
			streamer_id, name):
		# Begin required arguments.
		self.assertEqual(streamer_id, displayed_streamer_list_entry.streamer_id)
		self.assertEqual(name, displayed_streamer_list_entry.name)

	def _assert_displayed_streamer_list(self, displayed_streamer_list, num_streamers=0,
			prev_name=None, prev_streamer_id=None, next_name=None, next_streamer_id=None):
		# Begin optional arguments.
		self.assertEqual(num_streamers, len(displayed_streamer_list.streamers))
		self.assertEqual(prev_name, displayed_streamer_list.prev_name)
		self.assertEqual(prev_streamer_id, displayed_streamer_list.prev_streamer_id)
		self.assertEqual(next_name, displayed_streamer_list.next_name)
		self.assertEqual(next_streamer_id, displayed_streamer_list.next_streamer_id)

	"""Tests pagination when displaying all streaming users.
	"""
	def test_get_all_streamers_pagination(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)

		# Create the streamers.
		streamer_twitch_id1, streamer_id1 = self._create_twitch_user(self.streamer_name)
		streamer_name2 = 'streamer_name2'
		streamer_twitch_id2, streamer_id2 = self._create_twitch_user(streamer_name2)
		streamer_name3 = 'streamer_name3'
		streamer_twitch_id3, streamer_id3 = self._create_twitch_user(streamer_name3)
		streamer_name4 = 'streamer_name4'
		streamer_twitch_id4, streamer_id4 = self._create_twitch_user(streamer_name4)
		streamer_name5 = 'streamer_name5'
		streamer_twitch_id5, streamer_id5 = self._create_twitch_user(streamer_name5)
	
		def _get_next_page():
			return db.get_all_streamers(client_id, page_limit=2,
					next_name=displayed_streamers.next_name,
					next_streamer_id=displayed_streamers.next_streamer_id)
		
		def _get_prev_page():
			return db.get_all_streamers(client_id, page_limit=2,
					prev_name=displayed_streamers.prev_name,
					prev_streamer_id=displayed_streamers.prev_streamer_id)

		def _assert_first_page():
			self._assert_displayed_streamer_list(displayed_streamers, num_streamers=2,
					next_name=streamer_name2, next_streamer_id=streamer_id2)
			# Assert the partial list of paginated streamers.
			self._assert_displayed_streamer_list_entry(displayed_streamers.streamers[0],
					streamer_id1, self.streamer_name)
			self._assert_displayed_streamer_list_entry(displayed_streamers.streamers[1],
					streamer_id2, streamer_name2)

		def _assert_second_page():
			self._assert_displayed_streamer_list(displayed_streamers, num_streamers=2,
					prev_name=streamer_name3, prev_streamer_id=streamer_id3,
					next_name=streamer_name4, next_streamer_id=streamer_id4)
			# Assert the partial list of paginated streamers.
			self._assert_displayed_streamer_list_entry(displayed_streamers.streamers[0],
					streamer_id3, streamer_name3)
			self._assert_displayed_streamer_list_entry(displayed_streamers.streamers[1],
					streamer_id4, streamer_name4)

		def _assert_third_page():
			self._assert_displayed_streamer_list(displayed_streamers, num_streamers=1,
					prev_name=streamer_name5, prev_streamer_id=streamer_id5)
			# Assert the partial list of paginated streamers.
			self._assert_displayed_streamer_list_entry(displayed_streamers.streamers[0],
					streamer_id5, streamer_name5)

		# Assert that, clicking Next, the pages are correct.
		displayed_streamers = db.get_all_streamers(client_id, page_limit=2)
		_assert_first_page()
		displayed_streamers = _get_next_page()
		_assert_second_page()
		displayed_streamers = _get_next_page()
		_assert_third_page()

		# Assert that, clicking Previous, the pages are correct.
		displayed_streamers = _get_prev_page()
		_assert_second_page()
		displayed_streamers = _get_prev_page()
		_assert_first_page()

	"""Tests pagination when dispaying matches starred by the client.
	"""
	def test_get_starred_matches_pagination(self):
		# TODO
		pass
	
	"""Tests pagination when displaying teams starred by the client.
	"""
	def test_get_starred_teams_pagination(self):
		# TODO
		pass

	"""Tests pagination when displaying streaming users starred by the client.
	"""
	def test_get_starred_streamers_pagination(self):
		# TODO
		pass

	"""Test that updates the name of an existing team.
	"""
	def test_update_existing_team(self):
		updated_team_name = 'updated_name'
		updated_game = 'updated_game'
		updated_league = 'updated_league'
		updated_team_url = 'updated_team_url'

		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)
		# Create the team.
		team_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_url, self.team1_fingerprint)

		# Update the team name.
		updated_team_id = db.add_team(
				updated_team_name, updated_game, updated_league, updated_team_url,
				self.team1_fingerprint)
		# Assert that only the name was updated.
		self.assertEqual(team_id, updated_team_id)
		displayed_team = db.get_displayed_team(client_id, team_id)
		self._assert_displayed_team(displayed_team,
				team_id, updated_team_name, self.game, self.league)

	"""Test that fails to add a duplicate of an existing match.
	"""
	def test_add_existing_match(self):
		updated_time = self.time + timedelta(hours=1)
		updated_game = 'updated_game'
		updated_league = 'updated_league'
		updated_match_url = 'updated_match_url'

		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)
		# Create the teams.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_url, self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_url, self.team2_fingerprint)
		# Create the match.
		match_id = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_url, self.match_fingerprint, now=None)

		# Attempt to add the match again.
		updated_match_id = db.add_match(team1_id, team2_id,
				updated_time, updated_game, updated_league, updated_match_url,
				self.match_fingerprint, now=None)
		# Assert that this had no effect.
		self.assertEqual(match_id, updated_match_id)
		displayed_match = db.get_displayed_match(client_id, match_id)
		self._assert_displayed_match(displayed_match,
				match_id, self.time, self.game, self.league)

	"""Test that clients see their own stars for matches.
	"""
	def test_client_stars_matches(self):
		# Create the first client.
		client_steam_id1, client_id1 = self._create_steam_user(self.client_name)
		# Create the second client.
		client_name2 = 'client_name2'
		client_steam_id2, client_id2 = self._create_steam_user(client_name2)

		# Create the teams.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_url, self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_url, self.team2_fingerprint)
		# Create the first match.
		match_id1 = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_url, self.match_fingerprint, now=None)
		# Create the second match.
		time2 = self.time + timedelta(days=1)
		match_url2 = 'match_url2'
		match_fingerprint2 = 'match_fingerprint2'
		match_id2 = db.add_match(team1_id, team2_id, time2, self.game, self.league,
				match_url2, match_fingerprint2, now=None)

		# Create the streaming user.
		streamer_steam_id, streamer_id = self._create_steam_user(self.streamer_name)
		# Stream both matches.
		db.add_stream_match(streamer_id, match_id1)
		db.add_stream_match(streamer_id, match_id2)

		# The first user adds a star for the first match.
		db.add_star_match(client_id1, match_id1)
		# The second user adds a star for the second match.
		db.add_star_match(client_id2, match_id2)

		# Assert that the first match has a star by the first user.
		displayed_match = db.get_displayed_match(client_id1, match_id1)
		self._assert_displayed_match(displayed_match,
				match_id1, self.time, self.game, self.league,
				is_starred=True, num_stars=1, num_streamers=1)
		# Assert that the second match has no star by the first user.
		displayed_match = db.get_displayed_match(client_id1, match_id2)
		self._assert_displayed_match(displayed_match,
				match_id2, time2, self.game, self.league,
				num_stars=1, num_streamers=1)
	
		# Assert that the first match has no star by the second user.
		displayed_match = db.get_displayed_match(client_id2, match_id1)
		self._assert_displayed_match(displayed_match,
				match_id1, self.time, self.game, self.league,
				num_stars=1, num_streamers=1)
		# Assert that the second match has a star by the second user.
		displayed_match = db.get_displayed_match(client_id2, match_id2)
		self._assert_displayed_match(displayed_match,
				match_id2, time2, self.game, self.league,
				is_starred=True, num_stars=1, num_streamers=1)

		# Assert that the first user's calendar has the first match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id1)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		self._assert_displayed_calendar_match(displayed_calendar.next_match,
				match_id1, team1_id, self.team1_name, team2_id, self.team2_name,
				self.time, self.game, self.league, num_stars=1, num_streams=1)

		# Assert that the second user's calendar has the second match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id2)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		self._assert_displayed_calendar_match(displayed_calendar.next_match,
				match_id2, team1_id, self.team1_name, team2_id, self.team2_name,
				time2, self.game, self.league, num_stars=1, num_streams=1)

	"""Test that clients see their own stars for teams.
	"""
	def test_client_stars_teams(self):
		# Create the first client.
		client_steam_id1, client_id1 = self._create_steam_user(self.client_name)
		# Create the second client.
		client_name2 = 'client_name2'
		client_steam_id2, client_id2 = self._create_steam_user(client_name2)

		# Create the teams.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_url, self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_url, self.team2_fingerprint)
		team3_name = 'team3_name'
		team3_url = 'team3_url'
		team3_fingerprint = 'team3_fingerprint'
		team3_id = db.add_team(team3_name, self.game, self.league,
				team3_url, team3_fingerprint)

		# Create the first match.
		match_id1 = db.add_match(team1_id, team3_id, self.time, self.game, self.league,
				self.match_url, self.match_fingerprint, now=None)
		# Create the second match.
		time2 = self.time + timedelta(days=1)
		match_url2 = 'match_url2'
		match_fingerprint2 = 'match_fingerprint2'
		match_id2 = db.add_match(team2_id, team3_id, time2, self.game, self.league,
				match_url2, match_fingerprint2, now=None)

		# Create the streaming user.
		streamer_steam_id, streamer_id = self._create_steam_user(self.streamer_name)
		# Stream both matches.
		db.add_stream_match(streamer_id, match_id1)
		db.add_stream_match(streamer_id, match_id2)

		# The first user adds a star for the first team.
		db.add_star_team(client_id1, team1_id)
		# The second user adds a star for the second team.
		db.add_star_team(client_id2, team2_id)

		# Assert that the first team has a star by the first user.
		displayed_team = db.get_displayed_team(client_id1, team1_id)
		self._assert_displayed_team(displayed_team,
				team1_id, self.team1_name, self.game, self.league,
				is_starred=True, num_stars=1, num_matches=1)
		# Assert that the second team has no star by the first user.
		displayed_team = db.get_displayed_team(client_id1, team2_id)
		self._assert_displayed_team(displayed_team,
				team2_id, self.team2_name, self.game, self.league,
				num_stars=1, num_matches=1)

		# Assert that the first team has no star by the second user.
		displayed_team = db.get_displayed_team(client_id2, team1_id)
		self._assert_displayed_team(displayed_team,
				team1_id, self.team1_name, self.game, self.league,
				num_stars=1, num_matches=1)
		# Assert that the second team has a star by the second user.
		displayed_team = db.get_displayed_team(client_id2, team2_id)
		self._assert_displayed_team(displayed_team,
				team2_id, self.team2_name, self.game, self.league,
				is_starred=True, num_stars=1, num_matches=1)

		# Assert that the first user's calendar has the first match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id1)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		self._assert_displayed_calendar_match(displayed_calendar.next_match,
				match_id1, team1_id, self.team1_name, team3_id, team3_name,
				self.time, self.game, self.league, num_streams=1)

		# Assert that the second user's calendar has the second match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id2)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		self._assert_displayed_calendar_match(displayed_calendar.next_match,
				match_id2, team2_id, self.team2_name, team3_id, team3_name,
				time2, self.game, self.league, num_streams=1)

	"""Test that clients see their own stars for streamers.
	"""
	def test_client_stars_streamers(self):
		# Create the first client.
		client_steam_id1, client_id1 = self._create_steam_user(self.client_name)
		# Create the second client.
		client_name2 = 'client_name2'
		client_steam_id2, client_id2 = self._create_steam_user(client_name2)

		# Create the teams.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_url, self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_url, self.team2_fingerprint)
		# Create the first match.
		match_id1 = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_url, self.match_fingerprint, now=None)
		# Create the second match.
		time2 = self.time + timedelta(days=1)
		match_url2 = 'match_url2'
		match_fingerprint2 = 'match_fingerprint2'
		match_id2 = db.add_match(team1_id, team2_id, time2, self.game, self.league,
				match_url2, match_fingerprint2, now=None)

		# Create the first streaming user and stream the first match.
		streamer_steam_id1, streamer_id1 = self._create_steam_user(self.streamer_name)
		db.add_stream_match(streamer_id1, match_id1)
		# Create the second streaming user and stream the second match.
		streamer_name2 = 'streamer_name2'
		streamer_steam_id2, streamer_id2 = self._create_steam_user(streamer_name2)
		db.add_stream_match(streamer_id2, match_id2)

		# The first user adds a star for the first streaming user.
		db.add_star_streamer(client_id1, streamer_id1)
		# The second user adds a star for the second streaming user.
		db.add_star_streamer(client_id2, streamer_id2)

		# Assert that the first streamer has a star by the first user.
		displayed_streamer = db.get_displayed_streamer(client_id1, streamer_id1)
		self._assert_displayed_streamer(displayed_streamer,
				streamer_id1, self.streamer_name, is_starred=True, num_stars=1)
		# Assert that the second streamer has no star by the first user.
		displayed_streamer = db.get_displayed_streamer(client_id1, streamer_id2)
		self._assert_displayed_streamer(displayed_streamer,
				streamer_id2, streamer_name2, num_stars=1)

		# Assert that the first team has no star by the second user.
		displayed_streamer = db.get_displayed_streamer(client_id2, streamer_id1)
		self._assert_displayed_streamer(displayed_streamer,
				streamer_id1, self.streamer_name, num_stars=1)
		# Assert that the second team has a star by the second user.
		displayed_streamer = db.get_displayed_streamer(client_id2, streamer_id2)
		self._assert_displayed_streamer(displayed_streamer,
				streamer_id2, streamer_name2, is_starred=True, num_stars=1)

		# Assert that the first user's calendar has the first match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id1)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		self._assert_displayed_calendar_match(displayed_calendar.next_match,
				match_id1, team1_id, self.team1_name, team2_id, self.team2_name,
				self.time, self.game, self.league, num_streams=1)

		# Assert that the second user's calendar has the second match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id2)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		self._assert_displayed_calendar_match(displayed_calendar.next_match,
				match_id2, team1_id, self.team1_name, team2_id, self.team2_name,
				time2, self.game, self.league, num_streams=1)

	"""Test that clients see their own streams for matches.
	"""
	def test_client_streams_matches(self):
		# Create the first client.
		client_steam_id1, client_id1 = self._create_steam_user(self.client_name)
		# Create the second client.
		client_name2 = 'client_name2'
		client_steam_id2, client_id2 = self._create_steam_user(client_name2)

		# Create the teams.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_url, self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_url, self.team2_fingerprint)
		# Create the first match.
		match_id1 = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_url, self.match_fingerprint, now=None)
		# Create the second match.
		time2 = self.time + timedelta(days=1)
		match_url2 = 'match_url2'
		match_fingerprint2 = 'match_fingerprint2'
		match_id2 = db.add_match(team1_id, team2_id, time2, self.game, self.league,
				match_url2, match_fingerprint2, now=None)

		# Create the first streaming user.
		streamer_steam_id1, streamer_id1 = self._create_steam_user(self.streamer_name)
		# Create the second streaming user.
		streamer_name2 = 'streamer_name2'
		streamer_steam_id2, streamer_id2 = self._create_steam_user(streamer_name2)
		# The first streamer streams the first match.
		db.add_stream_match(streamer_id1, match_id1)
		# The second streamer streams the second match.
		db.add_stream_match(streamer_id2, match_id2)

		# The first user adds a star for the first streamer.
		db.add_star_streamer(client_id1, streamer_id1)
		# The second user adds a star for the second streamer.
		db.add_star_streamer(client_id2, streamer_id2)

		# Assert that the first streamer has a star by the first user.
		displayed_streamer = db.get_displayed_streamer(client_id1, streamer_id1)
		self._assert_displayed_streamer(displayed_streamer,
				streamer_id1, self.streamer_name,
				is_starred=True, num_stars=1, num_matches=1)
		# Assert that the second streamer has no star by the first user.
		displayed_streamer = db.get_displayed_streamer(client_id1, streamer_id2)
		self._assert_displayed_streamer(displayed_streamer,
				streamer_id2, streamer_name2, num_stars=1, num_matches=1)

		# Assert that the second streamer has no star by the first user.
		displayed_streamer = db.get_displayed_streamer(client_id2, streamer_id1)
		self._assert_displayed_streamer(displayed_streamer,
				streamer_id1, self.streamer_name, num_stars=1, num_matches=1)
		# Assert that the second streamer has a star by the second user.
		displayed_streamer = db.get_displayed_streamer(client_id2, streamer_id2)
		self._assert_displayed_streamer(displayed_streamer,
				streamer_id2, streamer_name2,
				is_starred=True, num_stars=1, num_matches=1)

		# Assert that the first user's calendar has the first match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id1)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		self._assert_displayed_calendar_match(displayed_calendar.next_match,
				match_id1, team1_id, self.team1_name, team2_id, self.team2_name,
				self.time, self.game, self.league, num_streams=1)

		# Assert that the second user's calendar has the second match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id2)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		self._assert_displayed_calendar_match(displayed_calendar.next_match,
				match_id2, team1_id, self.team1_name, team2_id, self.team2_name,
				time2, self.game, self.league, num_streams=1)

