from datetime import datetime, timedelta
import db
from db_test_case import DbTestCase
import sqlalchemy.orm as sa_orm
import unittest

import common_db

class TestFinderDb(DbTestCase):
	def setUp(self):
		DbTestCase.setUp(self)

		self.game = 'game'
		self.league = 'league'
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
			has_next_match=False, num_matches=0):
		# Begin optional arguments.
		self.assertEqual(has_next_match, displayed_calendar.next_match is not None)
		self.assertEqual(num_matches, len(displayed_calendar.matches))


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
			is_starred=False, num_stars=0, num_streamers=0):
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
		self.assertEqual(num_streamers, len(displayed_match.streamers))


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
			is_starred=False, num_stars=0, num_matches=0):
		# Begin required arguments.
		self.assertEqual(team_id, displayed_team.team_id)
		self.assertEqual(name, displayed_team.name)
		self.assertEqual(game, displayed_team.game)
		self.assertEqual(league, displayed_team.league)
		# Begin optional arguments.
		self.assertEqual(is_starred, displayed_team.is_starred)
		self.assertEqual(num_stars, displayed_team.num_stars)
		self.assertEqual(num_matches, len(displayed_team.matches))


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
			streamer_id, name, is_starred=False, num_stars=0, num_matches=0):
		# Begin required arguments.
		self.assertEqual(streamer_id, displayed_streamer.streamer_id)
		self.assertEqual(name, displayed_streamer.name)
		# Begin optional arguments.
		self.assertEqual(is_starred, displayed_streamer.is_starred)
		self.assertEqual(num_stars, displayed_streamer.num_stars)
		self.assertEqual(num_matches, len(displayed_streamer.matches))


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
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)

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
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)

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
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)

		with self.assertRaises(common_db.DbException):
			db.add_star_streamer(client_id, missing_streamer_id, now=self.now)

	"""Test that adds and removes a star for a match that is not casted.
	"""
	def test_add_remove_match_star_not_casted(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
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
		displayed_calendar = db.get_displayed_calendar(client_id)
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
		displayed_calendar = db.get_displayed_calendar(client_id)
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
		displayed_calendar = db.get_displayed_calendar(client_id)
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
		displayed_calendar = db.get_displayed_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)

	"""Test that adds and removes a star for a match that is casted.
	"""
	def test_add_remove_match_star_casted(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
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
		displayed_calendar = db.get_displayed_calendar(client_id)
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
		displayed_calendar = db.get_displayed_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)
	
	"""Test that adds and removes a star for a team in a match that is not casted.
	"""
	def test_add_remove_team_star_not_casted(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
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
		displayed_calendar = db.get_displayed_calendar(client_id)
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
		displayed_calendar = db.get_displayed_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)
		
		# Remove the star for team2.
		db.remove_star_team(client_id, team2_id, now=self.now)
		# Assert that team2 no longer has a star.
		displayed_team = db.get_displayed_team(client_id, team2_id)
		self._assert_displayed_team(displayed_team,
				team2_id, self.team2_name, self.game, self.league, num_matches=1)
		self._assert_displayed_team_match(displayed_team.matches[0],
				team1_id, self.team1_name, match_id, self.time)
		displayed_calendar = db.get_displayed_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)
	
		# Remove the star for team2 again.
		db.remove_star_team(client_id, team2_id, now=self.now)
		# Assert that this had no effect.
		displayed_team = db.get_displayed_team(client_id, team2_id)
		self._assert_displayed_team(displayed_team,
				team2_id, self.team2_name, self.game, self.league, num_matches=1)
		self._assert_displayed_team_match(displayed_team.matches[0],
				team1_id, self.team1_name, match_id, self.time)
		displayed_calendar = db.get_displayed_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)
	
	"""Test that adds and removes a star for a team in a match that is casted.
	"""
	def test_add_remove_team_star_casted(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
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
		displayed_calendar = db.get_displayed_calendar(client_id)
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
		displayed_calendar = db.get_displayed_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)
	
	"""Test that adds and removes a star for a streamer that is not casting a
	match.
	"""
	def test_add_remove_streamer_star_not_casted(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		# Create the streaming user.
		streamer_steam_id, streamer_id = self._create_steam_user(self.streamer_name)

		# Add a star for the streamer.
		db.add_star_streamer(client_id, streamer_id, now=self.now)
		# Assert that the streamer has a star.
		displayed_streamer = db.get_displayed_streamer(client_id, streamer_id)
		self._assert_displayed_streamer(displayed_streamer,
				streamer_id, self.streamer_name, is_starred=True, num_stars=1)
		# Assert that the user's calendar is empty.
		displayed_calendar = db.get_displayed_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)

		# Add the star for the streamer again.
		with self.assertRaises(common_db.DbException):
			db.add_star_streamer(client_id, streamer_id, now=self.now)
		# Assert that this had no effect.
		displayed_streamer = db.get_displayed_streamer(client_id, streamer_id)
		self._assert_displayed_streamer(displayed_streamer,
				streamer_id, self.streamer_name, is_starred=True, num_stars=1)
		displayed_calendar = db.get_displayed_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)
	
		# Remove the star for the streamer.
		db.remove_star_streamer(client_id, streamer_id, now=self.now)
		# Assert that the streamer no longer has a star.
		displayed_streamer = db.get_displayed_streamer(client_id, streamer_id)
		self._assert_displayed_streamer(displayed_streamer,
				streamer_id, self.streamer_name)
		displayed_calendar = db.get_displayed_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)

		# Remove the star for the streamer.
		db.remove_star_streamer(client_id, streamer_id, now=self.now)
		# Assert that this had no effect.
		displayed_streamer = db.get_displayed_streamer(client_id, streamer_id)
		self._assert_displayed_streamer(displayed_streamer,
				streamer_id, self.streamer_name)
		displayed_calendar = db.get_displayed_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)

	"""Test that adds and removes a star for a streamer that is casting a match.
	"""
	def test_add_remove_streamer_star_casted(self):
		pass
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
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
		displayed_calendar = db.get_displayed_calendar(client_id)
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
		displayed_calendar = db.get_displayed_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)

	def _remove_multi_stars(self, client_id, streamer_id,
			team1_id, team2_id, match_id):
		# Assert that the user's calendar has the match.
		displayed_calendar = db.get_displayed_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		self._assert_displayed_calendar_match(displayed_calendar.next_match,
				match_id, team1_id, self.team1_name, team2_id, self.team2_name,
				self.time, self.game, self.league, num_stars=1, num_streams=1)
		
		# Remove the star for the match.
		db.remove_star_match(client_id, match_id, now=self.now)
		# Assert that the user's calendar still has the match.
		displayed_calendar = db.get_displayed_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		self._assert_displayed_calendar_match(displayed_calendar.next_match,
				match_id, team1_id, self.team1_name, team2_id, self.team2_name,
				self.time, self.game, self.league, num_streams=1)
	
		# Remove the star for both teams.
		db.remove_star_team(client_id, team1_id, now=self.now)
		db.remove_star_team(client_id, team2_id, now=self.now)
		# Assert that the user's calendar still has the match.
		displayed_calendar = db.get_displayed_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		self._assert_displayed_calendar_match(displayed_calendar.next_match,
				match_id, team1_id, self.team1_name, team2_id, self.team2_name,
				self.time, self.game, self.league, num_streams=1)
	
		# Remove the star from the streamer.
		db.remove_star_streamer(client_id, streamer_id, now=self.now)
		# Assert that the user's calendar is empty.
		displayed_calendar = db.get_displayed_calendar(client_id)
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
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)

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
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)

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

