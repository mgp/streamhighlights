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
		self.team1_name = 'team1_name'
		self.team2_name = 'team2_name'
		self.time = datetime(2012, 11, 3, 18, 0, 0)
		self.now = datetime(2012, 11, 5, 12, 0, 0)


	"""Utility method to assert the properties of a DisplayedCalendarMatch.
	"""
	def _assert_displayed_calendar_match(displayed_calendar_match,
			match_id, team1_id, team1_name, team2_id, team2_name, time, game, league,
			num_stars=0, num_streams=0):
		# Begin required arguments.
		self.assertEqual(match_id, displayed_calendar_match.match_id)
		self.assertEqual(team1_id, displayed_calendar_match.team1_id)
		self.assertEqual(team1_name, displayed_calendar_match.team1_name)
		self.assertEqual(team2_id, displayed_calendar_match.team2_id)
		self.assertEqual(team2_name, displayed_calendar_match.team2_name)
		self.assertEqual(time, displayed_calendar.time)
		self.assertEqual(game, displayed_calendar.game)
		self.assertEqual(league, displayed_calendar.league)
		# Begin optional arguments.
		self.assertEqual(num_stars, displayed_calendar.num_stars)
		self.assertEqual(num_streams, displayed_calendar.num_streams)

	"""Utilty method to assert the properties of a DisplayedCalendar.
	"""
	def _assert_displayed_calendar(displayed_calendar,
			has_next_match=False, num_matches=0):
		# Begin optional arguments.
		self.assertEqual(has_next_match, displayed_calendar.next_match is not None)
		self.assertEqual(num_matches, len(displayed_calendar.matches))


	"""Utility method to assert the properties of a DisplayedMatchTeam.
	"""
	def _assert_displayed_match_team(displayed_match_team, team_id, name,
			num_stars=0):
		# Begin required arguments.
		self.assertEqual(team_id, displayed_match_team.team_id)
		self.assertEqual(name, displayed_match_team.name)
		# Begin optional arguments.
		self.assertEqual(num_stars, displayed_match_team.num_stars)

	"""Utility method to assert the properties of a DisplayedMatchStreamer.
	"""
	def _assert_displayed_match_streamer(displayed_match_streamer,
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
	def _assert_displayed_match(displayed_match, match_id, time, game, league,
			is_starred=False, num_stars=0, num_streamers=0):
		# Begin required arguments.
		self.assertEqual(match_id, displayed_match.match_id)
		self.assertEqual(time, displayed_match.time)
		self.assertEqual(game, displayed_match.game)
		self.assertEqual(league, displayed_match.league)
		# Begin optional arguments.
		self.assertEqual(is_starred, displayed_match.is_starred)
		self.assertEqual(num_stars, displayed_match.num_stars)
		self.assertEqual(num_streamers, len(displayed_match.streamers))


	"""Utility method to assert the properties of a DisplayedTeamMatch.
	"""
	def _assert_displayed_team_match(displayed_team_match,
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
	def _assert_displayed_team(displayed_team, team_id, name, game, league,
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
	def _assert_displayed_streamer_match(displayed_streamer_match,
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
	def _assert_displayed_streamer(displayed_streamer,
			streamer_id, name, is_starred=False, num_stars=0, num_matches=0):
		# Begin required arguments.
		self.assertEqual(streamer_id, displayed_streamer.streamer_id)
		self.assertEqual(name, displayed_streamer.name)
		# Begin optional arguments.
		self.assertEqual(is_starred, displayed_streamer.is_starred)
		self.assertEqual(num_stars, displayed_streamer.num_stars)
		self.assertEqual(num_matches, len(displayed_streamer.matches))


	"""Test that fails to create a star because the user identifier is unknown.
	"""
	def test_add_match_star_unknown_user(self):
		missing_user_id = 'missing_user_id'
		# Create the match.
		team1_id = db.add_team(self.team1_name, self.game, self.league)
		team2_id = db.add_team(self.team2_name, self.game, self.league)
		match_id = db.add_match(team1_id, team2_id, self.time, self.game, self.league, now=None)

		with self.assertRaises(common_db.DbException):
			db.add_star_match(missing_user_id, match_id, now=self.now)

	def test_add_match_star_unknown_match(self):
		missing_match_id = 'missing_match_id'
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)

		with self.assertRaises(common_db.DbException):
			db.add_star_match(client_id, missing_match_id, now=self.now)
	
	"""Test that adds and removes a star for a match that is not casted.
	"""
	def test_add_remove_match_star_not_casted(self):
		# Create the client.
		client_name = 'client_name1'
		client_steam_id, client_id = self._create_steam_user(client_name)
		# Create the match.
		team1_id = db.add_team(self.team1_name, self.game, self.league)
		team2_id = db.add_team(self.team2_name, self.game, self.league)
		match_id = db.add_match(team1_id, team2_id, self.time, self.game, self.league, now=None)

		# Add a star for the match.
		db.add_star_match(client_id, match_id, now=self.now)
		# Assert that the match has a star.
		"""
		displayed_match = db.get_displayed_match(client_id, match_id)
		self._assert_displayed_match(displayed_match, num_stars=1)
		"""

		# Add a star for the match again.
		db.add_star_match(client_id, match_id, now=self.now)
		# Assert that this had no effect.
		"""
		displayed_match = db.get_displayed_match(client_id, match_id)
		self._assert_displayed_match(displayed_match, num_stars=1)
		"""

		# Remove the star for the match.
		db.remove_star_match(client_id, match_id, now=self.now)
		# Assert that the match no longer has a star.
		"""
		displayed_match = db.get_displayed_match(client_id, match_id)
		self._assert_displayed_match(displayed_match)
		"""

		# Remove the star for the match again.
		db.remove_star_match(client_id, match_id, now=self.now)
		# Assert that this had no effect.
		"""
		displayed_match = db.get_displayed_match(client_id, match_id)
		self._assert_displayed_match(displayed_match)
		"""

	"""Test that adds and removes a star for a match that is casted.
	"""
	def test_add_remove_match_star_casted(self):
		pass

	"""Test that adds and removes a star for a team in a match that is not casted.
	"""
	def test_add_remove_team_star_not_casted(self):
		pass
	
	"""Test that adds and removes a star for a team in a match that is casted.
	"""
	def test_add_remove_team_star_casted(self):
		pass
	
	"""Test that adds and removes a star for a team in a match that is not casted.
	"""
	def test_add_remove_streamer_star_not_casted(self):
		pass
	
	"""Test that adds and removes a star for a streamer that is not casting a
	match.
	"""
	def test_add_remove_streamer_star_casted(self):
		pass

	"""Test that adds and removes a star for a streamer that is casting a match.
	"""
	def test_add_remove_streamer_star_not_casted(self):
		pass

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
