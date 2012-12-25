from datetime import datetime, timedelta
import db
from db_test_case import DbTestCase
import functools
import sqlalchemy.orm as sa_orm
import time
import unittest

import common_db

def timed(f):
	"""Prints the seconds taken to run a decorated function."""
	@functools.wraps(f)
	def decorated_function(*pargs, **kwargs):
		start_time = time.time()
		result = f(*pargs, **kwargs)
		end_time = time.time()
		print 'elapsed seconds: %f' % (end_time - start_time)
		return result
	return decorated_function


class AbstractFinderDbTestCase(DbTestCase):
	def setUp(self):
		DbTestCase.setUp(self)

		self.game = 'game'
		self.league = 'league'
		self.client_name = 'client_name'
		self.streamer_name = 'streamer_name'
		self.team1_name = 'team1_name'
		self.team1_fingerprint = 'team1_fingerprint'
		self.team2_name = 'team2_name'
		self.team2_fingerprint = 'team2_fingerprint'
		self.match_fingerprint = 'match_fingerprint'
		self.time = datetime(2012, 11, 3, 18, 0, 0)
		self.now = datetime(2012, 11, 5, 12, 0, 0)

	def _get_steam_urls(self, steam_id, name):
		url_by_id = common_db._get_steam_url_by_id(steam_id)
		url_by_name = common_db._get_steam_url_by_name_from_community_id(name)
		return (url_by_id, url_by_name)

	def _get_twitch_urls(self, twitch_id, name):
		url_by_id = common_db._get_twitch_url_by_id(twitch_id)
		url_by_name = common_db._get_twitch_url_by_name(name)
		return url_by_id, url_by_name

	def _assert_displayed_team(self, displayed_team,
			team_id, name, num_stars=0, game=None, league=None):
		"""Utility method to assert the attributes of a DisplayedTeam."""

		self.assertIsNotNone(displayed_team)
		self.assertEqual(team_id, displayed_team.team_id)
		self.assertEqual(name, displayed_team.name)
		# Begin optional arguments.
		self.assertEqual(num_stars, displayed_team.num_stars)
		self.assertEqual(game, displayed_team.game)
		self.assertEqual(league, displayed_team.league)

	def _assert_displayed_team_details(self, displayed_team,
			team_id, name, game, league, fingerprint,
			num_stars=0, is_starred=False, num_matches=0,
			prev_time=None, prev_match_id=None, next_time=None, next_match_id=None):
		"""Utility method to assert the attributes of a DisplayedTeamDetails.

		This does not assert the matches attribute, but only its length.
		"""

		self._assert_displayed_team(displayed_team,
				team_id, name, num_stars, game, league)
		self.assertEqual(fingerprint, displayed_team.fingerprint)
		# Begin optional arguments.
		self.assertEqual(is_starred, displayed_team.is_starred)
		self.assertEqual(num_matches, len(displayed_team.matches))
		self.assertEqual(prev_time, displayed_team.prev_time)
		self.assertEqual(prev_match_id, displayed_team.prev_match_id)
		self.assertEqual(next_time, displayed_team.next_time)
		self.assertEqual(next_match_id, displayed_team.next_match_id)

	def _assert_displayed_match(self, displayed_match,
			match_id, time, num_stars=0, num_streams=0, game=None, league=None):
		"""Utility method to assert the attributes of a DisplayedMatch.
		
		This does not assert the team1 and team2 attributes, however.
		"""

		self.assertEqual(match_id, displayed_match.match_id)
		self.assertEqual(time, displayed_match.time)
		# Begin optional arguments.
		self.assertEqual(num_stars, displayed_match.num_stars)
		self.assertEqual(num_streams, displayed_match.num_streams)
		self.assertEqual(game, displayed_match.game)
		self.assertEqual(league, displayed_match.league)

	def _assert_displayed_match_details(self, displayed_match,
			match_id, time, game, league, fingerprint,
			num_stars=0, num_streams=0, is_starred=False,
			prev_time=None, prev_streamer_id=None, next_time=None, next_streamer_id=None):
		"""Utility method to assert the properties of a DisplayedMatchDetails.

		This does not assert the streamers attribute, but only its length.
		"""

		self._assert_displayed_match(displayed_match,
				match_id, time, num_stars, num_streams, game, league)
		self.assertEqual(fingerprint, displayed_match.fingerprint)
		# Begin optional arguments.
		self.assertEqual(is_starred, displayed_match.is_starred)
		self.assertEqual(prev_time, displayed_match.prev_time)
		self.assertEqual(prev_streamer_id, displayed_match.prev_streamer_id)
		self.assertEqual(next_time, displayed_match.next_time)
		self.assertEqual(next_streamer_id, displayed_match.next_streamer_id)

	def _assert_displayed_calendar(self, displayed_calendar,
			has_next_match=False, num_matches=0,
			prev_time=None, prev_match_id=None, next_time=None, next_match_id=None):
		"""Utilty method to assert the attributes of a DisplayedCalendar.
		
		This does not assert the next_match or matches attributes, but only its
		existence and its length, respectively.
		"""

		# Begin optional arguments.
		self.assertEqual(has_next_match, displayed_calendar.next_match is not None)
		self.assertEqual(num_matches, len(displayed_calendar.matches))
		self.assertEqual(prev_time, displayed_calendar.prev_time)
		self.assertEqual(prev_match_id, displayed_calendar.prev_match_id)
		self.assertEqual(next_time, displayed_calendar.next_time)
		self.assertEqual(next_match_id, displayed_calendar.next_match_id)

	def _assert_displayed_streamer(self, displayed_streamer,
			streamer_id, name, url_by_id,
			num_stars=0, image_url_small=None, image_url_large=None, url_by_name=None):
		"""Utility method to assert the properties of a DisplayedStreamer."""

		self.assertEqual(streamer_id, displayed_streamer.streamer_id)
		self.assertEqual(name, displayed_streamer.name)
		self.assertEqual(url_by_id, displayed_streamer.url_by_id)
		# Begin optional arguments.
		self.assertEqual(num_stars, displayed_streamer.num_stars)
		self.assertEqual(image_url_small, displayed_streamer.image_url_small)
		self.assertEqual(image_url_large, displayed_streamer.image_url_large)
		self.assertEqual(url_by_name, displayed_streamer.url_by_name)

	def _assert_displayed_streamer_details(self, displayed_streamer,
			streamer_id, name, url_by_id,
			num_stars=0, image_url_small=None, image_url_large=None,
			url_by_name=None, is_starred=False, num_matches=0,
			prev_time=None, prev_match_id=None, next_time=None, next_match_id=None):
		"""Utility method to assert the properties of a DisplayedMatchDetails.

		This does not assert the streamers attribute, but only its length.
		"""

		self._assert_displayed_streamer(displayed_streamer,
				streamer_id, name, url_by_id, num_stars,
				image_url_small, image_url_large, url_by_name)
		# Begin optional arguments.
		self.assertEqual(is_starred, displayed_streamer.is_starred)
		self.assertEqual(num_matches, len(displayed_streamer.matches))
		self.assertEqual(prev_time, displayed_streamer.prev_time)
		self.assertEqual(prev_match_id, displayed_streamer.prev_match_id)
		self.assertEqual(next_time, displayed_streamer.next_time)
		self.assertEqual(next_match_id, displayed_streamer.next_match_id)


"""Tests for pagination of streaming users.
"""
class StreamerPaginationTestCase(AbstractFinderDbTestCase):
	def setUp(self):
		AbstractFinderDbTestCase.setUp(self)

		# Create the streamers.
		self.streamer_twitch_id1, self.streamer_id1 = self._create_twitch_user(
				self.streamer_name)
		self.url_by_id1, self.url_by_name1 = self._get_twitch_urls(
				self.streamer_twitch_id1, self.streamer_name)
		self.streamer_name2 = 'streamer_name2'
		self.streamer_twitch_id2, self.streamer_id2 = self._create_twitch_user(
				self.streamer_name2)
		self.url_by_id2, self.url_by_name2 = self._get_twitch_urls(
				self.streamer_twitch_id2, self.streamer_name2)
		self.streamer_name3 = 'streamer_name3'
		self.streamer_twitch_id3, self.streamer_id3 = self._create_twitch_user(
				self.streamer_name3)
		self.url_by_id3, self.url_by_name3 = self._get_twitch_urls(
				self.streamer_twitch_id3, self.streamer_name3)
		self.streamer_name4 = 'streamer_name4'
		self.streamer_twitch_id4, self.streamer_id4 = self._create_twitch_user(
				self.streamer_name4)
		self.url_by_id4, self.url_by_name4 = self._get_twitch_urls(
				self.streamer_twitch_id4, self.streamer_name4)
		self.streamer_name5 = 'streamer_name5'
		self.streamer_twitch_id5, self.streamer_id5 = self._create_twitch_user(
				self.streamer_name5)
		self.url_by_id5, self.url_by_name5 = self._get_twitch_urls(
				self.streamer_twitch_id5, self.streamer_name5)
	
	def _assert_displayed_streamer_list(self, displayed_streamer_list, num_streams=0,
			prev_name=None, prev_streamer_id=None, next_name=None, next_streamer_id=None):
		# Begin optional arguments.
		self.assertEqual(num_streams, len(displayed_streamer_list.streamers))
		self.assertEqual(prev_name, displayed_streamer_list.prev_name)
		self.assertEqual(prev_streamer_id, displayed_streamer_list.prev_streamer_id)
		self.assertEqual(next_name, displayed_streamer_list.next_name)
		self.assertEqual(next_streamer_id, displayed_streamer_list.next_streamer_id)

	def _test_get_streamers_pagination(self,
			displayed_streamers, get_next_page, get_prev_page, streamer_num_stars=0):
		def _assert_first_page():
			self._assert_displayed_streamer_list(displayed_streamers, num_streams=2,
					next_name=self.streamer_name2, next_streamer_id=self.streamer_id2)
			# Assert the partial list of paginated streamers.
			self._assert_displayed_streamer(displayed_streamers.streamers[0],
					self.streamer_id1, self.streamer_name, self.url_by_id1,
					num_stars=streamer_num_stars, url_by_name=self.url_by_name1)
			self._assert_displayed_streamer(displayed_streamers.streamers[1],
					self.streamer_id2, self.streamer_name2, self.url_by_id2,
					num_stars=streamer_num_stars, url_by_name=self.url_by_name2)

		def _assert_second_page():
			self._assert_displayed_streamer_list(displayed_streamers, num_streams=2,
					prev_name=self.streamer_name3, prev_streamer_id=self.streamer_id3,
					next_name=self.streamer_name4, next_streamer_id=self.streamer_id4)
			# Assert the partial list of paginated streamers.
			self._assert_displayed_streamer(displayed_streamers.streamers[0],
					self.streamer_id3, self.streamer_name3, self.url_by_id3,
					num_stars=streamer_num_stars, url_by_name=self.url_by_name3)
			self._assert_displayed_streamer(displayed_streamers.streamers[1],
					self.streamer_id4, self.streamer_name4, self.url_by_id4,
					num_stars=streamer_num_stars, url_by_name=self.url_by_name4)

		def _assert_third_page():
			self._assert_displayed_streamer_list(displayed_streamers, num_streams=1,
					prev_name=self.streamer_name5, prev_streamer_id=self.streamer_id5)
			# Assert the partial list of paginated streamers.
			self._assert_displayed_streamer(displayed_streamers.streamers[0],
					self.streamer_id5, self.streamer_name5, self.url_by_id5,
					num_stars=streamer_num_stars, url_by_name=self.url_by_name5)

		# Assert that, clicking Next, the pages are correct.
		_assert_first_page()
		displayed_streamers = get_next_page(displayed_streamers)
		_assert_second_page()
		displayed_streamers = get_next_page(displayed_streamers)
		_assert_third_page()

		# Assert that, clicking Previous, the pages are correct.
		displayed_streamers = get_prev_page(displayed_streamers)
		_assert_second_page()
		displayed_streamers = get_prev_page(displayed_streamers)
		_assert_first_page()

	"""Tests pagination when displaying all streaming users.
	"""
	def test_get_all_streamers_pagination(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)

		def _get_next_page(displayed_streamers):
			return db.get_all_streamers(client_id, page_limit=2,
					next_name=displayed_streamers.next_name,
					next_streamer_id=displayed_streamers.next_streamer_id)
		
		def _get_prev_page(displayed_streamers):
			return db.get_all_streamers(client_id, page_limit=2,
					prev_name=displayed_streamers.prev_name,
					prev_streamer_id=displayed_streamers.prev_streamer_id)

		displayed_streamers = db.get_all_streamers(client_id, page_limit=2)
		self._test_get_streamers_pagination(
				displayed_streamers, _get_next_page, _get_prev_page)

	"""Tests pagination when displaying streaming users starred by the client.
	"""
	def test_get_starred_streamers_pagination(self):
		# Add a streaming user that will not be starred.
		streamer_name6 = 'streamer_name6'
		streamer_twitch_id6, streamer_id6 = self._create_twitch_user(streamer_name6)

		# Create the client, who stars the other five streaming users.
		client_steam_id, client_id = self._create_steam_user(self.client_name)
		for streamer_id in (
				self.streamer_id1,
				self.streamer_id2,
				self.streamer_id3,
				self.streamer_id4,
				self.streamer_id5):
			db.add_star_streamer(client_id, streamer_id)

		def _get_next_page(displayed_streamers):
			return db.get_starred_streamers(client_id, page_limit=2,
					next_name=displayed_streamers.next_name,
					next_streamer_id=displayed_streamers.next_streamer_id)
		
		def _get_prev_page(displayed_streamers):
			return db.get_starred_streamers(client_id, page_limit=2,
					prev_name=displayed_streamers.prev_name,
					prev_streamer_id=displayed_streamers.prev_streamer_id)

		displayed_streamers = db.get_all_streamers(client_id, page_limit=2)
		self._test_get_streamers_pagination(
				displayed_streamers, _get_next_page, _get_prev_page, streamer_num_stars=1)

	"""Tests pagination of streamers when displaying a match.
	"""
	def test_get_displayed_match_pagination(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)
		# Create the match.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_fingerprint)
		match_id = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_fingerprint, now=None)

		# Each streamer is streaming the match.
		streamer_added_time1 = self.now + timedelta(minutes=1)
		db.add_stream_match(self.streamer_id1, match_id, now=streamer_added_time1)
		streamer_added_time2 = self.now + timedelta(minutes=2)
		db.add_stream_match(self.streamer_id2, match_id, now=streamer_added_time2)
		streamer_added_time3 = self.now + timedelta(minutes=3)
		db.add_stream_match(self.streamer_id3, match_id, now=streamer_added_time3)
		streamer_added_time4 = self.now + timedelta(minutes=4)
		db.add_stream_match(self.streamer_id4, match_id, now=streamer_added_time4)
		streamer_added_time5 = self.now + timedelta(minutes=5)
		db.add_stream_match(self.streamer_id5, match_id, now=streamer_added_time5)

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
			self._assert_displayed_match_details(displayed_match,
					match_id, self.time, self.game, self.league, self.match_fingerprint,
					num_streams=5,
					next_time=streamer_added_time2, next_streamer_id=self.streamer_id2)
			# Assert the partial list of paginated streamers.
			self._assert_displayed_streamer(displayed_match.streamers[0],
					self.streamer_id1, self.streamer_name, self.url_by_id1,
					url_by_name=self.url_by_name1)
			self._assert_displayed_streamer(displayed_match.streamers[1],
					self.streamer_id2, self.streamer_name2, self.url_by_id2,
					url_by_name=self.url_by_name2)

		def _assert_second_page():
			self.assertEqual(2, len(displayed_match.streamers))
			self._assert_displayed_match_details(displayed_match,
					match_id, self.time, self.game, self.league, self.match_fingerprint,
					num_streams=5,
					prev_time=streamer_added_time3, prev_streamer_id=self.streamer_id3,
					next_time=streamer_added_time4, next_streamer_id=self.streamer_id4)
			# Assert the partial list of paginated streamers.
			self._assert_displayed_streamer(displayed_match.streamers[0],
					self.streamer_id3, self.streamer_name3, self.url_by_id3,
					url_by_name=self.url_by_name3)
			self._assert_displayed_streamer(displayed_match.streamers[1],
					self.streamer_id4, self.streamer_name4, self.url_by_id4,
					url_by_name=self.url_by_name4)

		def _assert_third_page():
			self.assertEqual(1, len(displayed_match.streamers))
			self._assert_displayed_match_details(displayed_match,
					match_id, self.time, self.game, self.league, self.match_fingerprint,
					num_streams=5,
					prev_time=streamer_added_time5, prev_streamer_id=self.streamer_id5)
			# Assert the partial list of paginated streamers.
			self._assert_displayed_streamer(displayed_match.streamers[0],
					self.streamer_id5, self.streamer_name5, self.url_by_id5,
					url_by_name=self.url_by_name5)

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


"""Tests for pagination of teams.
"""
class TeamPaginationTestCase(AbstractFinderDbTestCase):
	def setUp(self):
		AbstractFinderDbTestCase.setUp(self)

		# Create the teams.
		self.team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_fingerprint)
		self.team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_fingerprint)
		self.team3_name = 'team3_name'
		self.team3_url = 'team3_url'
		self.team3_fingerprint = 'team3_fingerprint'
		self.team3_id = db.add_team(self.team3_name, self.game, self.league,
				self.team3_url, self.team3_fingerprint)
		self.team4_name = 'team4_name'
		self.team4_url = 'team4_url'
		self.team4_fingerprint = 'team4_fingerprint'
		self.team4_id = db.add_team(self.team4_name, self.game, self.league,
				self.team4_url, self.team4_fingerprint)
		self.team5_name = 'team5_name'
		self.team5_url = 'team5_url'
		self.team5_fingerprint = 'team5_fingerprint'
		self.team5_id = db.add_team(self.team5_name, self.game, self.league,
				self.team5_url, self.team5_fingerprint)

	def _assert_displayed_team_list(self, displayed_team_list, num_teams=0,
			prev_name=None, prev_team_id=None, next_name=None, next_team_id=None):
		# Begin optional arguments.
		self.assertEqual(num_teams, len(displayed_team_list.teams))
		self.assertEqual(prev_name, displayed_team_list.prev_name)
		self.assertEqual(prev_team_id, displayed_team_list.prev_team_id)
		self.assertEqual(next_name, displayed_team_list.next_name)
		self.assertEqual(next_team_id, displayed_team_list.next_team_id)

	def _test_get_teams_pagination(self,
			displayed_teams, get_next_page, get_prev_page, team_num_stars=0):
		def _assert_first_page():
			self._assert_displayed_team_list(displayed_teams, num_teams=2,
					next_name=self.team2_name, next_team_id=self.team2_id)
			# Assert the partial list of paginated teams.
			self._assert_displayed_team(displayed_teams.teams[0],
					self.team1_id, self.team1_name, num_stars=team_num_stars,
					game=self.game, league=self.league)
			self._assert_displayed_team(displayed_teams.teams[1],
					self.team2_id, self.team2_name, num_stars=team_num_stars,
					game=self.game, league=self.league)

		def _assert_second_page():
			self._assert_displayed_team_list(displayed_teams, num_teams=2,
					prev_name=self.team3_name, prev_team_id=self.team3_id,
					next_name=self.team4_name, next_team_id=self.team4_id)
			# Assert the partial list of paginated teams.
			self._assert_displayed_team(displayed_teams.teams[0],
					self.team3_id, self.team3_name, num_stars=team_num_stars,
					game=self.game, league=self.league)
			self._assert_displayed_team(displayed_teams.teams[1],
					self.team4_id, self.team4_name, num_stars=team_num_stars,
					game=self.game, league=self.league)

		def _assert_third_page():
			self._assert_displayed_team_list(displayed_teams, num_teams=1,
					prev_name=self.team5_name, prev_team_id=self.team5_id)
			# Assert the partial list of paginated teams.
			self._assert_displayed_team(displayed_teams.teams[0],
					self.team5_id, self.team5_name, num_stars=team_num_stars,
					game=self.game, league=self.league)

		# Assert that, clicking Next, the pages are correct.
		_assert_first_page()
		displayed_teams = get_next_page(displayed_teams)
		_assert_second_page()
		displayed_teams = get_next_page(displayed_teams)
		_assert_third_page()

		# Assert that, clicking Previous, the pages are correct.
		displayed_teams = get_prev_page(displayed_teams)
		_assert_second_page()
		displayed_teams = get_prev_page(displayed_teams)
		_assert_first_page()

	"""Tests pagination when displaying all teams.
	"""
	def test_get_all_teams_pagination(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)

		def _get_next_page(displayed_teams):
			return db.get_all_teams(client_id, page_limit=2,
					next_name=displayed_teams.next_name,
					next_team_id=displayed_teams.next_team_id)
		
		def _get_prev_page(displayed_teams):
			return db.get_all_teams(client_id, page_limit=2,
					prev_name=displayed_teams.prev_name,
					prev_team_id=displayed_teams.prev_team_id)

		displayed_teams = db.get_all_teams(client_id, page_limit=2)
		self._test_get_teams_pagination(displayed_teams, _get_next_page, _get_prev_page)

	"""Tests pagination when displaying teams starred by the client.
	"""
	def test_get_starred_teams_pagination(self):
		# Add a team that will not be starred.
		team6_name = 'team6_name'
		team6_url = 'team6_url'
		team6_fingerprint = 'team6_fingerprint'
		team6_id = db.add_team(
				team6_name, self.game, self.league, team6_url, team6_fingerprint)

		# Create the client, who stars the other five teams.
		client_steam_id, client_id = self._create_steam_user(self.client_name)
		for team_id in (
				self.team1_id, self.team2_id, self.team3_id, self.team4_id, self.team5_id):
			db.add_star_team(client_id, team_id)

		def _get_next_page(displayed_teams):
			return db.get_starred_teams(client_id, page_limit=2,
					next_name=displayed_teams.next_name,
					next_team_id=displayed_teams.next_team_id)
		
		def _get_prev_page(displayed_teams):
			return db.get_starred_teams(client_id, page_limit=2,
					prev_name=displayed_teams.prev_name,
					prev_team_id=displayed_teams.prev_team_id)

		displayed_teams = db.get_starred_teams(client_id, page_limit=2)
		self._test_get_teams_pagination(
				displayed_teams, _get_next_page, _get_prev_page, team_num_stars=1)


"""Tests for pagination of matches.
"""
class MatchPaginationTestCase(AbstractFinderDbTestCase):
	def setUp(self):
		AbstractFinderDbTestCase.setUp(self)

		# Create the teams.
		self.team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_fingerprint)
		self.team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_fingerprint)
		self.team3_name = 'team3_name'
		self.team3_url = 'team3_url'
		self.team3_fingerprint = 'team3_fingerprint'
		self.team3_id = db.add_team(self.team3_name, self.game, self.league,
				self.team3_url, self.team3_fingerprint)

		# The second and third matches happen at the same time.
		self.time2 = self.time + timedelta(days=1)
		self.time3 = self.time2
		self.time4 = self.time3 + timedelta(days=1)
		self.time5 = self.time4 + timedelta(days=1)

		# Create the matches.
		self.match_fingerprint2 = 'match_fingerprint2'
		self.match_fingerprint3 = 'match_fingerprint3'
		self.match_fingerprint4 = 'match_fingerprint4'
		self.match_fingerprint5 = 'match_fingerprint5'
		self.match_id1 = db.add_match(self.team1_id, self.team2_id, self.time,
				self.game, self.league, self.match_fingerprint, now=None)
		self.match_id2 = db.add_match(self.team1_id, self.team3_id, self.time2,
				self.game, self.league, self.match_fingerprint2, now=None)
		self.match_id3 = db.add_match(self.team1_id, self.team3_id, self.time3,
				self.game, self.league, self.match_fingerprint3, now=None)
		self.match_id4 = db.add_match(self.team1_id, self.team2_id, self.time4,
				self.game, self.league, self.match_fingerprint4, now=None)
		self.match_id5 = db.add_match(self.team1_id, self.team3_id, self.time5,
				self.game, self.league, self.match_fingerprint5, now=None)

	def _test_get_displayed_calendar_pagination(self,
			displayed_calendar, get_next_page, get_prev_page):
		def _assert_next_match():
			next_match = displayed_calendar.next_match
			self._assert_displayed_match(next_match, self.match_id1,
					self.time, num_streams=1, game=self.game, league=self.league)
			self._assert_displayed_team(next_match.team1, self.team1_id, self.team1_name)
			self._assert_displayed_team(next_match.team2, self.team2_id, self.team2_name)

		def _assert_first_page():
			self.assertEqual(2, len(displayed_calendar.matches))
			self._assert_displayed_calendar(displayed_calendar,
					has_next_match=True, num_matches=2,
					next_time=self.time2, next_match_id=self.match_id2)
			_assert_next_match()
			# Assert the partial list of paginated matches.
			match = displayed_calendar.matches[0]
			self._assert_displayed_match(match,
					self.match_id1, self.time, num_streams=1, game=self.game, league=self.league)
			self._assert_displayed_team(match.team1, self.team1_id, self.team1_name)
			self._assert_displayed_team(match.team2, self.team2_id, self.team2_name)
			match = displayed_calendar.matches[1]
			self._assert_displayed_match(match,
					self.match_id2, self.time2, num_streams=1, game=self.game, league=self.league)
			self._assert_displayed_team(match.team1, self.team1_id, self.team1_name)
			self._assert_displayed_team(match.team2, self.team3_id, self.team3_name)

		def _assert_second_page():
			self.assertEqual(2, len(displayed_calendar.matches))
			self._assert_displayed_calendar(displayed_calendar,
					has_next_match=True, num_matches=2,
					prev_time=self.time3, prev_match_id=self.match_id3,
					next_time=self.time4, next_match_id=self.match_id4)
			_assert_next_match()
			# Assert the partial list of paginated matches.
			match = displayed_calendar.matches[0]
			self._assert_displayed_match(match,
					self.match_id3, self.time3, num_streams=1, game=self.game, league=self.league)
			self._assert_displayed_team(match.team1, self.team1_id, self.team1_name)
			self._assert_displayed_team(match.team2, self.team3_id, self.team3_name)
			match = displayed_calendar.matches[1]
			self._assert_displayed_match(match,
					self.match_id4, self.time4, num_streams=1, game=self.game, league=self.league)
			self._assert_displayed_team(match.team1, self.team1_id, self.team1_name)
			self._assert_displayed_team(match.team2, self.team2_id, self.team2_name)

		def _assert_third_page():
			self.assertEqual(1, len(displayed_calendar.matches))
			self._assert_displayed_calendar(displayed_calendar,
					has_next_match=True, num_matches=1,
					prev_time=self.time5, prev_match_id=self.match_id5)
			_assert_next_match()
			# Assert the partial list of paginated matches.
			match = displayed_calendar.matches[0]
			self._assert_displayed_match(match,
					self.match_id5, self.time5, num_streams=1, game=self.game, league=self.league)
			self._assert_displayed_team(match.team1, self.team1_id, self.team1_name)
			self._assert_displayed_team(match.team2, self.team3_id, self.team3_name)

		# Assert that, clicking Next, the pages are correct.
		_assert_first_page()
		displayed_calendar = get_next_page(displayed_calendar)
		_assert_second_page()
		displayed_calendar = get_next_page(displayed_calendar)
		_assert_third_page()

		# Assert that, clicking Previous, the pages are correct.
		displayed_calendar = get_prev_page(displayed_calendar)
		_assert_second_page()
		displayed_calendar = get_prev_page(displayed_calendar)
		_assert_first_page()

	"""Tests pagination of matches when displaying the client's viewing calendar.
	"""
	def test_get_displayed_viewer_calendar_pagination(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)

		# Create the streaming user, who streams all matches.
		streamer_steam_id, streamer_id = self._create_steam_user(self.streamer_name)
		for match_id in (
				self.match_id1, self.match_id2, self.match_id3, self.match_id4, self.match_id5):
			db.add_stream_match(streamer_id, match_id)
		# Star the streamer.
		db.add_star_streamer(client_id, streamer_id)

		def _get_next_page(displayed_calendar):
			return db.get_displayed_viewer_calendar(client_id, page_limit=2,
					next_time=displayed_calendar.next_time,
					next_match_id=displayed_calendar.next_match_id)

		def _get_prev_page(displayed_calendar):
			return db.get_displayed_viewer_calendar(client_id, page_limit=2,
					prev_time=displayed_calendar.prev_time,
					prev_match_id=displayed_calendar.prev_match_id)

		displayed_calendar = db.get_displayed_viewer_calendar(client_id, page_limit=2)
		self._test_get_displayed_calendar_pagination(
				displayed_calendar, _get_next_page, _get_prev_page)

	"""Tests pagination of matches when displaying the client's streaming calendar.
	"""
	def test_get_displayed_streamer_calendar_pagination(self):
		# Add a match that will not be streamed.
		match_fingerprint6 = 'match_fingerprint6'
		match_id6 = db.add_match(self.team1_id, self.team2_id, self.time,
				self.game, self.league, match_fingerprint6, now=None)

		# Create the client, who streams the other five matches.
		client_steam_id, client_id = self._create_steam_user(self.client_name)
		for match_id in (
				self.match_id1, self.match_id2, self.match_id3, self.match_id4, self.match_id5):
			db.add_stream_match(client_id, match_id)

		def _get_next_page(displayed_calendar):
			return db.get_displayed_streamer_calendar(client_id, page_limit=2,
					next_time=displayed_calendar.next_time,
					next_match_id=displayed_calendar.next_match_id)
			
		def _get_prev_page(displayed_calendar):
			return db.get_displayed_streamer_calendar(client_id, page_limit=2,
					prev_time=displayed_calendar.prev_time,
					prev_match_id=displayed_calendar.prev_match_id)

		displayed_calendar = db.get_displayed_streamer_calendar(client_id, page_limit=2)
		self._test_get_displayed_calendar_pagination(
				displayed_calendar, _get_next_page, _get_prev_page)

	"""Tests pagination of matches when displaying a streaming user.
	"""
	def test_get_displayed_streamer_pagination(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)

		# Create the streaming user, who streams all matches.
		streamer_steam_id, streamer_id = self._create_steam_user(self.streamer_name)
		url_by_id, url_by_name = self._get_steam_urls(streamer_steam_id, self.streamer_name)
		for match_id in (
				self.match_id1, self.match_id2, self.match_id3, self.match_id4, self.match_id5):
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
			self._assert_displayed_streamer_details(displayed_streamer,
					streamer_id, self.streamer_name, url_by_id,
					url_by_name=url_by_name, num_matches=2,
					next_time=self.time2, next_match_id=self.match_id2)
			# Assert the partial list of paginated matches.
			match = displayed_streamer.matches[0]
			self._assert_displayed_match(match,
					self.match_id1, self.time, num_streams=1, game=self.game, league=self.league)
			self._assert_displayed_team(match.team1, self.team1_id, self.team1_name)
			self._assert_displayed_team(match.team2, self.team2_id, self.team2_name)
			match = displayed_streamer.matches[1]
			self._assert_displayed_match(match,
					self.match_id2, self.time2, num_streams=1, game=self.game, league=self.league)
			self._assert_displayed_team(match.team1, self.team1_id, self.team1_name)
			self._assert_displayed_team(match.team2, self.team3_id, self.team3_name)

		def _assert_second_page():
			self._assert_displayed_streamer_details(displayed_streamer,
					streamer_id, self.streamer_name, url_by_id,
					url_by_name=url_by_name, num_matches=2,
					prev_time=self.time3, prev_match_id=self.match_id3,
					next_time=self.time4, next_match_id=self.match_id4)
			# Assert the partial list of paginated matches.
			match = displayed_streamer.matches[0]
			self._assert_displayed_match(match,
					self.match_id3, self.time3, num_streams=1, game=self.game, league=self.league)
			self._assert_displayed_team(match.team1, self.team1_id, self.team1_name)
			self._assert_displayed_team(match.team2, self.team3_id, self.team3_name)
			match = displayed_streamer.matches[1]
			self._assert_displayed_match(match,
					self.match_id4, self.time4, num_streams=1, game=self.game, league=self.league)
			self._assert_displayed_team(match.team1, self.team1_id, self.team1_name)
			self._assert_displayed_team(match.team2, self.team2_id, self.team2_name)

		def _assert_third_page():
			self._assert_displayed_streamer_details(displayed_streamer,
					streamer_id, self.streamer_name, url_by_id,
					url_by_name=url_by_name, num_matches=1,
					prev_time=self.time5, prev_match_id=self.match_id5)
			# Assert the partial list of paginated matches.
			match = displayed_streamer.matches[0]
			self._assert_displayed_match(match,
					self.match_id5, self.time5, num_streams=1, game=self.game, league=self.league)
			self._assert_displayed_team(match.team1, self.team1_id, self.team1_name)
			self._assert_displayed_team(match.team2, self.team3_id, self.team3_name)

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

	"""Tests pagination of matches when displaying a team.
	"""
	def test_get_displayed_team_pagination(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)

		def _get_next_page():
			return db.get_displayed_team(client_id, self.team1_id, page_limit=2,
					next_time=displayed_team.next_time,
					next_match_id=displayed_team.next_match_id)
		
		def _get_prev_page():
			return db.get_displayed_team(client_id, self.team1_id, page_limit=2,
					prev_time=displayed_team.prev_time,
					prev_match_id=displayed_team.prev_match_id)
	
		def _assert_first_page():
			self._assert_displayed_team_details(displayed_team,
					self.team1_id, self.team1_name, self.game, self.league,
					self.team1_fingerprint, num_matches=2,
					next_time=self.time2, next_match_id=self.match_id2)
			# Assert the partial list of paginated matches.
			match = displayed_team.matches[0]
			self._assert_displayed_match(match, self.match_id1, self.time)
			self.assertIsNone(match.team1)
			self._assert_displayed_team(match.team2, self.team2_id, self.team2_name)
			match = displayed_team.matches[1]
			self._assert_displayed_match(match, self.match_id2, self.time2)
			self.assertIsNone(match.team1)
			self._assert_displayed_team(match.team2, self.team3_id, self.team3_name)

		def _assert_second_page():		
			self._assert_displayed_team_details(displayed_team,
					self.team1_id, self.team1_name, self.game, self.league,
					self.team1_fingerprint, num_matches=2,
					prev_time=self.time3, prev_match_id=self.match_id3,
					next_time=self.time4, next_match_id=self.match_id4)
			# Assert the partial list of paginated matches.
			match = displayed_team.matches[0]
			self._assert_displayed_match(match, self.match_id3, self.time3)
			self.assertIsNone(match.team1)
			self._assert_displayed_team(match.team2, self.team3_id, self.team3_name)
			match = displayed_team.matches[1]
			self._assert_displayed_match(match, self.match_id4, self.time4)
			self.assertIsNone(match.team1)
			self._assert_displayed_team(match.team2, self.team2_id, self.team2_name)

		def _assert_third_page():
			self._assert_displayed_team_details(displayed_team,
					self.team1_id, self.team1_name, self.game, self.league,
					self.team1_fingerprint, num_matches=1,
					prev_time=self.time5, prev_match_id=self.match_id5)
			# Assert the partial list of paginated matches.
			match = displayed_team.matches[0]
			self._assert_displayed_match(match, self.match_id5, self.time5)
			self.assertIsNone(match.team1)
			self._assert_displayed_team(match.team2, self.team3_id, self.team3_name)

		# Assert that, clicking Next, the pages are correct.
		displayed_team = db.get_displayed_team(client_id, self.team1_id, page_limit=2)
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

	def _assert_displayed_match_list(self, displayed_match_list, num_matches=0,
			prev_time=None, prev_match_id=None, next_time=None, next_match_id=None):
		# Begin optional arguments.
		self.assertEqual(num_matches, len(displayed_match_list.matches))
		self.assertEqual(prev_time, displayed_match_list.prev_time)
		self.assertEqual(prev_match_id, displayed_match_list.prev_match_id)
		self.assertEqual(next_time, displayed_match_list.next_time)
		self.assertEqual(next_match_id, displayed_match_list.next_match_id)

	def _test_get_matches_pagination(self,
			displayed_matches, get_next_page, get_prev_page, match_num_stars=0):
		def _assert_first_page():
			self._assert_displayed_match_list(displayed_matches, num_matches=2,
					next_time=self.time2, next_match_id=self.match_id2)
			# Assert the partial list of paginated matches.
			match = displayed_matches.matches[0]
			self._assert_displayed_match(match,
					self.match_id1, self.time, game=self.game, league=self.league,
					num_stars=match_num_stars)
			self._assert_displayed_team(match.team1, self.team1_id, self.team1_name)
			self._assert_displayed_team(match.team2, self.team2_id, self.team2_name)
			match = displayed_matches.matches[1]
			self._assert_displayed_match(match,
					self.match_id2, self.time2, game=self.game, league=self.league,
					num_stars=match_num_stars)
			self._assert_displayed_team(match.team1, self.team1_id, self.team1_name)
			self._assert_displayed_team(match.team2, self.team3_id, self.team3_name)

		def _assert_second_page():
			self._assert_displayed_match_list(displayed_matches, num_matches=2,
					prev_time=self.time3, prev_match_id=self.match_id3,
					next_time=self.time4, next_match_id=self.match_id4)
			# Assert the partial list of paginated matches.
			match = displayed_matches.matches[0]
			self._assert_displayed_match(match,
					self.match_id3, self.time3, game=self.game, league=self.league,
					num_stars=match_num_stars)
			self._assert_displayed_team(match.team1, self.team1_id, self.team1_name)
			self._assert_displayed_team(match.team2, self.team3_id, self.team3_name)
			match = displayed_matches.matches[1]
			self._assert_displayed_match(match,
					self.match_id4, self.time4, game=self.game, league=self.league,
					num_stars=match_num_stars)
			self._assert_displayed_team(match.team1, self.team1_id, self.team1_name)
			self._assert_displayed_team(match.team2, self.team2_id, self.team2_name)

		def _assert_third_page():
			self._assert_displayed_match_list(displayed_matches, num_matches=1,
					prev_time=self.time5, prev_match_id=self.match_id5)
			# Assert the partial list of paginated matches.
			match = displayed_matches.matches[0]
			self._assert_displayed_match(match,
					self.match_id5, self.time5, game=self.game, league=self.league,
					num_stars=match_num_stars)
			self._assert_displayed_team(match.team1, self.team1_id, self.team1_name)
			self._assert_displayed_team(match.team2, self.team3_id, self.team3_name)

		# Assert that, clicking Next, the pages are correct.
		_assert_first_page()
		displayed_matches = get_next_page(displayed_matches)
		_assert_second_page()
		displayed_matches = get_next_page(displayed_matches)
		_assert_third_page()

		# Assert that, clicking Previous, the pages are correct.
		displayed_matches = get_prev_page(displayed_matches)
		_assert_second_page()
		displayed_matches = get_prev_page(displayed_matches)
		_assert_first_page()

	"""Tests pagination when displaying all matches.
	"""
	def test_get_all_matches_pagination(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)

		def _get_next_page(displayed_matches):
			return db.get_all_matches(client_id, page_limit=2,
					next_time=displayed_matches.next_time,
					next_match_id=displayed_matches.next_match_id)
		
		def _get_prev_page(displayed_matches):
			return db.get_all_matches(client_id, page_limit=2,
					prev_time=displayed_matches.prev_time,
					prev_match_id=displayed_matches.prev_match_id)

		displayed_matches = db.get_all_matches(client_id, page_limit=2)
		self._test_get_matches_pagination(
				displayed_matches, _get_next_page, _get_prev_page)
	
	"""Tests pagination when dispaying matches starred by the client.
	"""
	def test_get_starred_matches_pagination(self):
		# Add a match that will not be streamed.
		match_fingerprint6 = 'match_fingerprint6'
		match_id6 = db.add_match(self.team1_id, self.team2_id, self.time,
				self.game, self.league, match_fingerprint6, now=None)

		# Create the client, who stars the other five matches.
		client_steam_id, client_id = self._create_steam_user(self.client_name)
		for match_id in (
				self.match_id1, self.match_id2, self.match_id3, self.match_id4, self.match_id5):
			db.add_star_match(client_id, match_id)

		def _get_next_page(displayed_matches):
			return db.get_starred_matches(client_id, page_limit=2,
					next_time=displayed_matches.next_time,
					next_match_id=displayed_matches.next_match_id)
		
		def _get_prev_page(displayed_matches):
			return db.get_starred_matches(client_id, page_limit=2,
					prev_time=displayed_matches.prev_time,
					prev_match_id=displayed_matches.prev_match_id)

		displayed_matches = db.get_starred_matches(client_id, page_limit=2)
		self._test_get_matches_pagination(
				displayed_matches, _get_next_page, _get_prev_page, match_num_stars=1)


class FinderDbTestCase(AbstractFinderDbTestCase):
	"""Test that fails to create a match because one team identifier is unknown.
	"""
	def test_add_match_unknown_team(self):
		missing_team2_id = 99
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_fingerprint)
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)

		with self.assertRaises(common_db.DbException):
			db.add_match(team1_id, missing_team2_id, self.time, self.game, self.league,
					self.match_fingerprint, now=self.now)

	"""Test that fails to star a match because the client identifier is unknown.
	"""
	def test_add_match_star_unknown_client(self):
		missing_client_id = 99
		# Create the match.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_fingerprint)
		match_id = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_fingerprint, now=None)

		with self.assertRaises(common_db.DbException):
			db.add_star_match(missing_client_id, match_id, now=self.now)

	"""Test that fails to star a match because the match identifier is unknown.
	"""
	def test_add_match_star_unknown_match(self):
		missing_match_id = 99
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)

		with self.assertRaises(common_db.DbException):
			db.add_star_match(client_id, missing_match_id, now=self.now)
	
	"""Test that fails to star a team because the client identifier is unknown.
	"""
	def test_add_team_star_unknown_client(self):
		missing_client_id = 99
		# Create the team.
		team_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_fingerprint)
	
		with self.assertRaises(common_db.DbException):
			db.add_star_team(missing_client_id, team_id, now=self.now)

	"""Test that fails to star a match because the team identifier is unknown.
	"""
	def test_add_team_star_unknown_team(self):
		missing_team_id = 99
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)

		with self.assertRaises(common_db.DbException):
			db.add_star_team(client_id, missing_team_id, now=self.now)
	
	"""Test that fails to star a streamer because the client identifier is unknown.
	"""
	def test_add_streamer_star_unknown_client(self):
		missing_client_id = 99
		# Create the streaming user.
		streamer_steam_id, streamer_id = self._create_steam_user(self.streamer_name)

		with self.assertRaises(common_db.DbException):
			db.add_star_team(missing_client_id, streamer_id, now=self.now)
	
	"""Test that fails to star a streamer because the streamer identifier is unknown.
	"""
	def test_add_streamer_star_unknown_team(self):
		missing_streamer_id = 99
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
				self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_fingerprint)
		match_id = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_fingerprint, now=None)

		# Add a star for the match.
		db.add_star_match(client_id, match_id, now=self.now)
		# Assert that the match has a star.
		displayed_match = db.get_displayed_match(client_id, match_id)
		self._assert_displayed_match_details(displayed_match,
				match_id, self.time, self.game, self.league, self.match_fingerprint,
				num_stars=1, is_starred=True)
		self._assert_displayed_team(displayed_match.team1, team1_id, self.team1_name)
		self._assert_displayed_team(displayed_match.team2, team2_id, self.team2_name)
		# Assert that the user's calendar is empty.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)

		# Add a star for the match again.
		with self.assertRaises(common_db.DbException):
			db.add_star_match(client_id, match_id, now=self.now)
		# Assert that this had no effect.
		displayed_match = db.get_displayed_match(client_id, match_id)
		self._assert_displayed_match_details(displayed_match,
				match_id, self.time, self.game, self.league, self.match_fingerprint,
				num_stars=1, is_starred=True)
		self._assert_displayed_team(displayed_match.team1, team1_id, self.team1_name)
		self._assert_displayed_team(displayed_match.team2, team2_id, self.team2_name)
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)

		# Remove the star for the match.
		db.remove_star_match(client_id, match_id, now=self.now)
		# Assert that the match no longer has a star.
		displayed_match = db.get_displayed_match(client_id, match_id)
		self._assert_displayed_match_details(displayed_match,
				match_id, self.time, self.game, self.league, self.match_fingerprint)
		self._assert_displayed_team(displayed_match.team1, team1_id, self.team1_name)
		self._assert_displayed_team(displayed_match.team2, team2_id, self.team2_name)
		# Assert that the user's calendar is empty.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)

		# Remove the star for the match again.
		db.remove_star_match(client_id, match_id, now=self.now)
		# Assert that this had no effect.
		displayed_match = db.get_displayed_match(client_id, match_id)
		self._assert_displayed_match_details(displayed_match,
				match_id, self.time, self.game, self.league, self.match_fingerprint)
		self._assert_displayed_team(displayed_match.team1, team1_id, self.team1_name)
		self._assert_displayed_team(displayed_match.team2, team2_id, self.team2_name)
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)

	"""Test that adds and removes a star for a match that is casted.
	"""
	def test_add_remove_match_star_casted(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)
		# Create the match.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_fingerprint)
		match_id = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_fingerprint, now=None)

		# Create the streaming user.
		streamer_steam_id, streamer_id = self._create_steam_user(self.streamer_name)
		url_by_id, url_by_name = self._get_steam_urls(streamer_steam_id, self.streamer_name)
		# Stream the match.
		db.add_stream_match(streamer_id, match_id)

		# Add a star for the match.
		db.add_star_match(client_id, match_id, now=self.now)
		# Assert that the match has a star.
		displayed_match = db.get_displayed_match(client_id, match_id)
		self._assert_displayed_match_details(displayed_match,
				match_id, self.time, self.game, self.league, self.match_fingerprint,
				num_stars=1, num_streams=1, is_starred=True)
		self._assert_displayed_team(displayed_match.team1, team1_id, self.team1_name)
		self._assert_displayed_team(displayed_match.team2, team2_id, self.team2_name)
		self._assert_displayed_streamer(displayed_match.streamers[0],
				streamer_id, self.streamer_name, url_by_id, url_by_name=url_by_name)
		# Assert that the user's calendar has the match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		next_match = displayed_calendar.next_match
		self._assert_displayed_match(next_match, match_id,
				self.time, num_stars=1, num_streams=1, game=self.game, league=self.league)

		# Remove the star for the match.
		db.remove_star_match(client_id, match_id, now=self.now)
		# Assert that the match no longer has a star.
		displayed_match = db.get_displayed_match(client_id, match_id)
		self._assert_displayed_match_details(displayed_match,
				match_id, self.time, self.game, self.league, self.match_fingerprint,
				num_streams=1)
		self._assert_displayed_team(displayed_match.team1, team1_id, self.team1_name)
		self._assert_displayed_team(displayed_match.team2, team2_id, self.team2_name)
		self._assert_displayed_streamer(displayed_match.streamers[0],
				streamer_id, self.streamer_name, url_by_id, url_by_name=url_by_name)
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
				self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_fingerprint)
		match_id = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_fingerprint, now=None)

		# Add a star for team2.
		db.add_star_team(client_id, team2_id, now=self.now)
		# Assert that the team has a star.
		displayed_team = db.get_displayed_team(client_id, team2_id)
		self._assert_displayed_team_details(displayed_team,
				team2_id, self.team2_name, self.game, self.league, self.team2_fingerprint,
				num_stars=1, is_starred=True, num_matches=1)
		match = displayed_team.matches[0]
		self._assert_displayed_match(match, match_id, self.time)
		self.assertIsNone(match.team1)
		self._assert_displayed_team(match.team2, team1_id, self.team1_name)
		# Assert that the user's calendar is empty.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)
		
		# Add a star for team2 again.
		with self.assertRaises(common_db.DbException):
			db.add_star_team(client_id, team2_id, now=self.now)
		# Assert that this had no effect.
		displayed_team = db.get_displayed_team(client_id, team2_id)
		self._assert_displayed_team_details(displayed_team,
				team2_id, self.team2_name, self.game, self.league, self.team2_fingerprint,
				num_stars=1, is_starred=True, num_matches=1)
		match = displayed_team.matches[0]
		self._assert_displayed_match(match, match_id, self.time)
		self.assertIsNone(match.team1)
		self._assert_displayed_team(match.team2, team1_id, self.team1_name)
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)
		
		# Remove the star for team2.
		db.remove_star_team(client_id, team2_id, now=self.now)
		# Assert that team2 no longer has a star.
		displayed_team = db.get_displayed_team(client_id, team2_id)
		self._assert_displayed_team_details(displayed_team,
				team2_id, self.team2_name, self.game, self.league, self.team2_fingerprint,
				num_matches=1)
		match = displayed_team.matches[0]
		self._assert_displayed_match(match, match_id, self.time)
		self.assertIsNone(match.team1)
		self._assert_displayed_team(match.team2, team1_id, self.team1_name)
		# Assert that the user's calendar is empty.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)
	
		# Remove the star for team2 again.
		db.remove_star_team(client_id, team2_id, now=self.now)
		# Assert that this had no effect.
		displayed_team = db.get_displayed_team(client_id, team2_id)
		self._assert_displayed_team_details(displayed_team,
				team2_id, self.team2_name, self.game, self.league, self.team2_fingerprint,
				num_matches=1)
		match = displayed_team.matches[0]
		self._assert_displayed_match(match, match_id, self.time)
		self.assertIsNone(match.team1)
		self._assert_displayed_team(match.team2, team1_id, self.team1_name)
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)
		
	"""Test that adds and removes a star for a team in a match that is casted.
	"""
	def test_add_remove_team_star_casted(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)
		# Create the match.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_fingerprint)
		match_id = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_fingerprint, now=None)

		# Create the streaming user.
		streamer_steam_id, streamer_id = self._create_steam_user(self.streamer_name)
		# Stream the match.
		db.add_stream_match(streamer_id, match_id)

		# Add a star for team2.
		db.add_star_team(client_id, team2_id, now=self.now)
		# Assert that the team has a star.
		displayed_team = db.get_displayed_team(client_id, team2_id)
		self._assert_displayed_team_details(displayed_team,
				team2_id, self.team2_name, self.game, self.league, self.team2_fingerprint,
				num_stars=1, is_starred=True, num_matches=1)
		match = displayed_team.matches[0]
		self._assert_displayed_match(match, match_id, self.time, num_streams=1)
		self.assertIsNone(match.team1)
		self._assert_displayed_team(match.team2, team1_id, self.team1_name)
		# Assert that the user's calendar has the match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		next_match = displayed_calendar.next_match
		self._assert_displayed_match(next_match, match_id,
				self.time, num_streams=1, game=self.game, league=self.league)

		# Remove the star for team2.
		db.remove_star_team(client_id, team2_id, now=self.now)
		# Assert that team2 no longer has a star.
		displayed_team = db.get_displayed_team(client_id, team2_id)
		self._assert_displayed_team_details(displayed_team,
				team2_id, self.team2_name, self.game, self.league, self.team2_fingerprint,
				num_matches=1)
		match = displayed_team.matches[0]
		self._assert_displayed_match(match, match_id, self.time, num_streams=1)
		self.assertIsNone(match.team1)
		self._assert_displayed_team(match.team2, team1_id, self.team1_name)
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
		url_by_id, url_by_name = self._get_steam_urls(streamer_steam_id, self.streamer_name)

		# Add a star for the streamer.
		db.add_star_streamer(client_id, streamer_id, now=self.now)
		# Assert that the streamer has a star.
		displayed_streamer = db.get_displayed_streamer(client_id, streamer_id)
		self._assert_displayed_streamer_details(displayed_streamer,
				streamer_id, self.streamer_name, url_by_id,
				num_stars=1, url_by_name=url_by_name, is_starred=True)
		# Assert that the user's calendar is empty.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)

		# Add the star for the streamer again.
		with self.assertRaises(common_db.DbException):
			db.add_star_streamer(client_id, streamer_id, now=self.now)
		# Assert that this had no effect.
		displayed_streamer = db.get_displayed_streamer(client_id, streamer_id)
		self._assert_displayed_streamer_details(displayed_streamer,
				streamer_id, self.streamer_name, url_by_id,
				num_stars=1, url_by_name=url_by_name, is_starred=True)
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)
	
		# Remove the star for the streamer.
		db.remove_star_streamer(client_id, streamer_id, now=self.now)
		# Assert that the streamer no longer has a star.
		displayed_streamer = db.get_displayed_streamer(client_id, streamer_id)
		self._assert_displayed_streamer_details(displayed_streamer,
				streamer_id, self.streamer_name, url_by_id, url_by_name=url_by_name)
		# Assert that the user's calendar is empty.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)

		# Remove the star for the streamer again.
		db.remove_star_streamer(client_id, streamer_id, now=self.now)
		# Assert that this had no effect.
		displayed_streamer = db.get_displayed_streamer(client_id, streamer_id)
		self._assert_displayed_streamer_details(displayed_streamer,
				streamer_id, self.streamer_name, url_by_id, url_by_name=url_by_name)
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)

	"""Test that adds and removes a star for a streamer that is casting a match.
	"""
	def test_add_remove_streamer_star_casted(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)
		# Create the streaming user.
		streamer_steam_id, streamer_id = self._create_steam_user(self.streamer_name)
		# Create the match.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_fingerprint)
		match_id = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_fingerprint, now=None)

		# Create the streaming user.
		streamer_steam_id, streamer_id = self._create_steam_user(self.streamer_name)
		url_by_id, url_by_name = self._get_steam_urls(streamer_steam_id, self.streamer_name)
		# Stream the match.
		db.add_stream_match(streamer_id, match_id)

		# Add a star for the streamer.
		db.add_star_streamer(client_id, streamer_id, now=self.now)
		# Assert that the streamer has a star.
		displayed_streamer = db.get_displayed_streamer(client_id, streamer_id)
		self._assert_displayed_streamer_details(displayed_streamer,
				streamer_id, self.streamer_name, url_by_id,
				num_stars=1, url_by_name=url_by_name, is_starred=True, num_matches=1)
		match = displayed_streamer.matches[0]
		self._assert_displayed_match(match, match_id,
				self.time, num_streams=1, game=self.game, league=self.league)
		self._assert_displayed_team(match.team1, team1_id, self.team1_name)
		self._assert_displayed_team(match.team2, team2_id, self.team2_name)
		# Assert that the user's calendar has the match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		next_match = displayed_calendar.next_match
		self._assert_displayed_match(next_match, match_id,
				self.time, num_streams=1, game=self.game, league=self.league)
		self._assert_displayed_team(match.team1, team1_id, self.team1_name)
		self._assert_displayed_team(match.team2, team2_id, self.team2_name)

		# Remove the star for the streamer.
		db.remove_star_streamer(client_id, streamer_id, now=self.now)
		# Assert that the streamer no longer has a star.
		displayed_streamer = db.get_displayed_streamer(client_id, streamer_id)
		self._assert_displayed_streamer_details(displayed_streamer,
				streamer_id, self.streamer_name, url_by_id,
				url_by_name=url_by_name, num_matches=1)
		match = displayed_streamer.matches[0]
		self._assert_displayed_match(match, match_id,
				self.time, num_streams=1, game=self.game, league=self.league)
		self._assert_displayed_team(match.team1, team1_id, self.team1_name)
		self._assert_displayed_team(match.team2, team2_id, self.team2_name)
		# Assert that the user's calendar is empty.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)

	def _remove_multi_stars(self, client_id, streamer_id, streamer_steam_id,
			team1_id, team2_id, match_id):
		url_by_id, url_by_name = self._get_steam_urls(streamer_steam_id, self.streamer_name)

		# Assert that the user's calendar has the match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		next_match = displayed_calendar.next_match
		self._assert_displayed_match(next_match, match_id,
				self.time, num_stars=1, num_streams=1, game=self.game, league=self.league)
		self._assert_displayed_team(next_match.team1, team1_id, self.team1_name, num_stars=1)
		self._assert_displayed_team(next_match.team2, team2_id, self.team2_name, num_stars=1)
		
		# Remove the star for the match.
		db.remove_star_match(client_id, match_id, now=self.now)
		# Assert that the user's calendar still has the match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		next_match = displayed_calendar.next_match
		self._assert_displayed_match(next_match, match_id,
				self.time, num_streams=1, game=self.game, league=self.league)
		self._assert_displayed_team(next_match.team1, team1_id, self.team1_name, num_stars=1)
		self._assert_displayed_team(next_match.team2, team2_id, self.team2_name, num_stars=1)
	
		# Remove the star for both teams.
		db.remove_star_team(client_id, team1_id, now=self.now)
		db.remove_star_team(client_id, team2_id, now=self.now)
		# Assert that the user's calendar still has the match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		next_match = displayed_calendar.next_match
		self._assert_displayed_match(next_match, match_id,
				self.time, num_streams=1, game=self.game, league=self.league)
		self._assert_displayed_team(next_match.team1, team1_id, self.team1_name)
		self._assert_displayed_team(next_match.team2, team2_id, self.team2_name)
	
		# Remove the star from the streamer.
		db.remove_star_streamer(client_id, streamer_id, now=self.now)
		# Assert that the user's calendar is empty.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)

		# Assert that the match should no longer have a star.
		displayed_match = db.get_displayed_match(client_id, match_id)
		self._assert_displayed_match_details(displayed_match,
				match_id, self.time, self.game, self.league, self.match_fingerprint,
				num_streams=1)
		self._assert_displayed_team(displayed_match.team1, team1_id, self.team1_name)
		self._assert_displayed_team(displayed_match.team2, team2_id, self.team2_name)
		# Assert that team1 no longer has a star.
		displayed_team = db.get_displayed_team(client_id, team1_id)
		self._assert_displayed_team_details(displayed_team,
				team1_id, self.team1_name, self.game, self.league, self.team1_fingerprint,
				num_matches=1)
		match = displayed_team.matches[0]
		self._assert_displayed_match(match, match_id, self.time, num_streams=1)
		self.assertIsNone(match.team1)
		self._assert_displayed_team(match.team2, team2_id, self.team2_name)
		# Assert that team2 no longer has a star.
		displayed_team = db.get_displayed_team(client_id, team2_id)
		self._assert_displayed_team_details(displayed_team,
				team2_id, self.team2_name, self.game, self.league, self.team2_fingerprint,
				num_matches=1)
		match = displayed_team.matches[0]
		self._assert_displayed_match(match, match_id, self.time, num_streams=1)
		self.assertIsNone(match.team1)
		self._assert_displayed_team(match.team2, team1_id, self.team1_name)
		# The streamer should no longer have a star.
		displayed_streamer = db.get_displayed_streamer(client_id, streamer_id)
		self._assert_displayed_streamer_details(displayed_streamer,
				streamer_id, self.streamer_name, url_by_id,
				url_by_name=url_by_name, num_matches=1)
		match = displayed_streamer.matches[0]
		self._assert_displayed_match(match, match_id, self.time,
				num_streams=1, game=self.game, league=self.league)
		self._assert_displayed_team(match.team1, team1_id, self.team1_name)
		self._assert_displayed_team(match.team2, team2_id, self.team2_name)

	"""Test that adds stars to all match components, and then adds a user
	streaming the match before removing all stars.
	"""
	def test_add_multi_stars_then_stream(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)

		# Create the match.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_fingerprint)
		match_id = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_fingerprint, now=None)
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
		self._remove_multi_stars(
				client_id, streamer_id, streamer_steam_id, team1_id, team2_id, match_id)

	"""Test that adds a user streaming a match, and then adds stars to all match
	components before removing all stars.
	"""
	def test_stream_then_add_multi_stars(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)

		# Create the match.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_fingerprint)
		match_id = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_fingerprint, now=None)
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
		self._remove_multi_stars(
				client_id, streamer_id, streamer_steam_id, team1_id, team2_id, match_id)

	"""Test that adds and removes multiple streamers for a casted match.
	"""
	def test_add_remove_multi_streamers(self):
		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)

		# Create the match.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_fingerprint)
		match_id = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_fingerprint, now=None)
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
		next_match = displayed_calendar.next_match
		self._assert_displayed_match(next_match, match_id,
				self.time, num_stars=1, num_streams=1, game=self.game, league=self.league)
		self._assert_displayed_team(next_match.team1, team1_id, self.team1_name)
		self._assert_displayed_team(next_match.team2, team2_id, self.team2_name)
	
		# The second streamer streams the match.
		db.add_stream_match(streamer_id2, match_id)
		# Assert that the user's calendar still has the match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		next_match = displayed_calendar.next_match
		self._assert_displayed_match(next_match, match_id,
				self.time, num_stars=1, num_streams=2, game=self.game, league=self.league)
		self._assert_displayed_team(next_match.team1, team1_id, self.team1_name)
		self._assert_displayed_team(next_match.team2, team2_id, self.team2_name)
	
		# The first streamer is no longer streaming the match.
		db.remove_stream_match(streamer_id1, match_id)
		# Assert that the user's calendar still has the match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		next_match = displayed_calendar.next_match
		self._assert_displayed_match(next_match, match_id,
				self.time, num_stars=1, num_streams=1, game=self.game, league=self.league)
		self._assert_displayed_team(next_match.team1, team1_id, self.team1_name)
		self._assert_displayed_team(next_match.team2, team2_id, self.team2_name)

		# The second streamer is no longer streaming the match.
		db.remove_stream_match(streamer_id2, match_id)
		# Assert that the user's calendar is empty.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id)
		self._assert_displayed_calendar(displayed_calendar)

	# TODO: Test remove_stream_match.

	"""Test that updates the name of an existing team.
	"""
	def test_update_existing_team(self):
		updated_team_name = 'updated_name'
		updated_game = 'updated_game'
		updated_league = 'updated_league'

		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)
		# Create the team.
		team_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_fingerprint)

		# Update the team name.
		updated_team_id = db.add_team(
				updated_team_name, updated_game, updated_league, self.team1_fingerprint)
		# Assert that only the name was updated.
		self.assertEqual(team_id, updated_team_id)
		displayed_team = db.get_displayed_team(client_id, team_id)
		self._assert_displayed_team_details(displayed_team,
				team_id, updated_team_name, self.game, self.league, self.team1_fingerprint)

	"""Test that fails to add a duplicate of an existing match.
	"""
	def test_add_existing_match(self):
		updated_time = self.time + timedelta(hours=1)
		updated_game = 'updated_game'
		updated_league = 'updated_league'

		# Create the client.
		client_steam_id, client_id = self._create_steam_user(self.client_name)
		# Create the teams.
		team1_id = db.add_team(self.team1_name, self.game, self.league,
				self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_fingerprint)
		# Create the match.
		match_id = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_fingerprint, now=None)

		# Attempt to add the match again.
		updated_match_id = db.add_match(team1_id, team2_id,
				updated_time, updated_game, updated_league, self.match_fingerprint,
				now=None)
		# Assert that this had no effect.
		self.assertEqual(match_id, updated_match_id)
		displayed_match = db.get_displayed_match(client_id, match_id)
		self._assert_displayed_match_details(displayed_match,
				match_id, self.time, self.game, self.league, self.match_fingerprint)

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
				self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_fingerprint)
		# Create the first match.
		match_id1 = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_fingerprint, now=None)
		# Create the second match.
		time2 = self.time + timedelta(days=1)
		match_fingerprint2 = 'match_fingerprint2'
		match_id2 = db.add_match(team1_id, team2_id, time2, self.game, self.league,
				match_fingerprint2, now=None)

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
		self._assert_displayed_match_details(displayed_match,
				match_id1, self.time, self.game, self.league, self.match_fingerprint,
				num_stars=1, num_streams=1, is_starred=True)
		self._assert_displayed_team(displayed_match.team1, team1_id, self.team1_name)
		self._assert_displayed_team(displayed_match.team2, team2_id, self.team2_name)
		# Assert that the second match has no star by the first user.
		displayed_match = db.get_displayed_match(client_id1, match_id2)
		self._assert_displayed_match_details(displayed_match,
				match_id2, time2, self.game, self.league, match_fingerprint2,
				num_stars=1, num_streams=1)
		self._assert_displayed_team(displayed_match.team1, team1_id, self.team1_name)
		self._assert_displayed_team(displayed_match.team2, team2_id, self.team2_name)
	
		# Assert that the first match has no star by the second user.
		displayed_match = db.get_displayed_match(client_id2, match_id1)
		self._assert_displayed_match_details(displayed_match,
				match_id1, self.time, self.game, self.league, self.match_fingerprint,
				num_stars=1, num_streams=1)
		self._assert_displayed_team(displayed_match.team1, team1_id, self.team1_name)
		self._assert_displayed_team(displayed_match.team2, team2_id, self.team2_name)
		# Assert that the second match has a star by the second user.
		displayed_match = db.get_displayed_match(client_id2, match_id2)
		self._assert_displayed_match_details(displayed_match,
				match_id2, time2, self.game, self.league, match_fingerprint2,
				num_stars=1, num_streams=1, is_starred=True)
		self._assert_displayed_team(displayed_match.team1, team1_id, self.team1_name)
		self._assert_displayed_team(displayed_match.team2, team2_id, self.team2_name)

		# Assert that the first user's calendar has the first match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id1)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		next_match = displayed_calendar.next_match
		self._assert_displayed_match(next_match, match_id1,
				self.time, num_stars=1, num_streams=1, game=self.game, league=self.league)
		self._assert_displayed_team(next_match.team1, team1_id, self.team1_name)
		self._assert_displayed_team(next_match.team2, team2_id, self.team2_name)

		# Assert that the second user's calendar has the second match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id2)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		next_match = displayed_calendar.next_match
		self._assert_displayed_match(next_match, match_id2,
				time2, num_stars=1, num_streams=1, game=self.game, league=self.league)
		self._assert_displayed_team(next_match.team1, team1_id, self.team1_name)
		self._assert_displayed_team(next_match.team2, team2_id, self.team2_name)

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
				self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_fingerprint)
		team3_name = 'team3_name'
		team3_url = 'team3_url'
		team3_fingerprint = 'team3_fingerprint'
		team3_id = db.add_team(team3_name, self.game, self.league,
				team3_url, team3_fingerprint)

		# Create the first match.
		match_id1 = db.add_match(team1_id, team3_id, self.time, self.game, self.league,
				self.match_fingerprint, now=None)
		# Create the second match.
		time2 = self.time + timedelta(days=1)
		match_fingerprint2 = 'match_fingerprint2'
		match_id2 = db.add_match(team2_id, team3_id, time2, self.game, self.league,
				match_fingerprint2, now=None)

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
		self._assert_displayed_team_details(displayed_team,
				team1_id, self.team1_name, self.game, self.league, self.team1_fingerprint,
				num_stars=1, is_starred=True, num_matches=1)
		# Assert that the second team has no star by the first user.
		displayed_team = db.get_displayed_team(client_id1, team2_id)
		self._assert_displayed_team_details(displayed_team,
				team2_id, self.team2_name, self.game, self.league, self.team2_fingerprint,
				num_stars=1, num_matches=1)

		# Assert that the first team has no star by the second user.
		displayed_team = db.get_displayed_team(client_id2, team1_id)
		self._assert_displayed_team_details(displayed_team,
				team1_id, self.team1_name, self.game, self.league, self.team1_fingerprint,
				num_stars=1, num_matches=1)
		# Assert that the second team has a star by the second user.
		displayed_team = db.get_displayed_team(client_id2, team2_id)
		self._assert_displayed_team_details(displayed_team,
				team2_id, self.team2_name, self.game, self.league, self.team2_fingerprint,
				num_stars=1, is_starred=True, num_matches=1)

		# Assert that the first user's calendar has the first match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id1)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		next_match = displayed_calendar.next_match
		self._assert_displayed_match(next_match, match_id1,
				self.time, num_streams=1, game=self.game, league=self.league)
		self._assert_displayed_team(next_match.team1, team1_id, self.team1_name,
				num_stars=1)
		self._assert_displayed_team(next_match.team2, team3_id, team3_name)

		# Assert that the second user's calendar has the second match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id2)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		next_match = displayed_calendar.next_match
		self._assert_displayed_match(next_match, match_id2,
				time2, num_streams=1, game=self.game, league=self.league)
		self._assert_displayed_team(next_match.team1, team2_id, self.team2_name,
				num_stars=1)
		self._assert_displayed_team(next_match.team2, team3_id, team3_name)

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
				self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_fingerprint)
		# Create the first match.
		match_id1 = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_fingerprint, now=None)
		# Create the second match.
		time2 = self.time + timedelta(days=1)
		match_fingerprint2 = 'match_fingerprint2'
		match_id2 = db.add_match(team1_id, team2_id, time2, self.game, self.league,
				match_fingerprint2, now=None)

		# Create the first streaming user and stream the first match.
		streamer_steam_id1, streamer_id1 = self._create_steam_user(self.streamer_name)
		url_by_id1, url_by_name1 = self._get_steam_urls(
				streamer_steam_id1, self.streamer_name)
		db.add_stream_match(streamer_id1, match_id1)
		# Create the second streaming user and stream the second match.
		streamer_name2 = 'streamer_name2'
		streamer_steam_id2, streamer_id2 = self._create_steam_user(streamer_name2)
		url_by_id2, url_by_name2 = self._get_steam_urls(streamer_steam_id2, streamer_name2)
		db.add_stream_match(streamer_id2, match_id2)

		# The first user adds a star for the first streaming user.
		db.add_star_streamer(client_id1, streamer_id1)
		# The second user adds a star for the second streaming user.
		db.add_star_streamer(client_id2, streamer_id2)

		# Assert that the first streamer has a star by the first user.
		displayed_streamer = db.get_displayed_streamer(client_id1, streamer_id1)
		self._assert_displayed_streamer_details(displayed_streamer,
				streamer_id1, self.streamer_name, url_by_id1,
				num_stars=1, url_by_name=url_by_name1, is_starred=True, num_matches=1)
		# Assert that the second streamer has no star by the first user.
		displayed_streamer = db.get_displayed_streamer(client_id1, streamer_id2)
		self._assert_displayed_streamer_details(displayed_streamer,
				streamer_id2, streamer_name2, url_by_id2,
				num_stars=1, url_by_name=url_by_name2, num_matches=1)

		# Assert that the first team has no star by the second user.
		displayed_streamer = db.get_displayed_streamer(client_id2, streamer_id1)
		self._assert_displayed_streamer_details(displayed_streamer,
				streamer_id1, self.streamer_name, url_by_id1,
				num_stars=1, url_by_name=url_by_name1, num_matches=1)
		# Assert that the second team has a star by the second user.
		displayed_streamer = db.get_displayed_streamer(client_id2, streamer_id2)
		self._assert_displayed_streamer_details(displayed_streamer,
				streamer_id2, streamer_name2, url_by_id2,
				num_stars=1, url_by_name=url_by_name2, is_starred=True, num_matches=1)

		# Assert that the first user's calendar has the first match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id1)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		next_match = displayed_calendar.next_match
		self._assert_displayed_match(next_match, match_id1,
				self.time, num_streams=1, game=self.game, league=self.league)
		self._assert_displayed_team(next_match.team1, team1_id, self.team1_name)
		self._assert_displayed_team(next_match.team2, team2_id, self.team2_name)

		# Assert that the second user's calendar has the second match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id2)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		next_match = displayed_calendar.next_match
		self._assert_displayed_match(next_match, match_id2,
				time2, num_streams=1, game=self.game, league=self.league)
		self._assert_displayed_team(next_match.team1, team1_id, self.team1_name)
		self._assert_displayed_team(next_match.team2, team2_id, self.team2_name)

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
				self.team1_fingerprint)
		team2_id = db.add_team(self.team2_name, self.game, self.league,
				self.team2_fingerprint)
		# Create the first match.
		match_id1 = db.add_match(team1_id, team2_id, self.time, self.game, self.league,
				self.match_fingerprint, now=None)
		# Create the second match.
		time2 = self.time + timedelta(days=1)
		match_fingerprint2 = 'match_fingerprint2'
		match_id2 = db.add_match(team1_id, team2_id, time2, self.game, self.league,
				match_fingerprint2, now=None)

		# Create the first streaming user.
		streamer_steam_id1, streamer_id1 = self._create_steam_user(self.streamer_name)
		url_by_id1, url_by_name1 = self._get_steam_urls(
				streamer_steam_id1, self.streamer_name)
		# Create the second streaming user.
		streamer_name2 = 'streamer_name2'
		streamer_steam_id2, streamer_id2 = self._create_steam_user(streamer_name2)
		url_by_id2, url_by_name2 = self._get_steam_urls(streamer_steam_id2, streamer_name2)
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
		self._assert_displayed_streamer_details(displayed_streamer,
				streamer_id1, self.streamer_name, url_by_id1,
				num_stars=1, url_by_name=url_by_name1, is_starred=True, num_matches=1)
		# Assert that the second streamer has no star by the first user.
		displayed_streamer = db.get_displayed_streamer(client_id1, streamer_id2)
		self._assert_displayed_streamer_details(displayed_streamer,
				streamer_id2, streamer_name2, url_by_id2,
				num_stars=1, url_by_name=url_by_name2, num_matches=1)

		# Assert that the second streamer has no star by the first user.
		displayed_streamer = db.get_displayed_streamer(client_id2, streamer_id1)
		self._assert_displayed_streamer_details(displayed_streamer,
				streamer_id1, self.streamer_name, url_by_id1,
				num_stars=1, url_by_name=url_by_name1, num_matches=1)
		# Assert that the second streamer has a star by the second user.
		displayed_streamer = db.get_displayed_streamer(client_id2, streamer_id2)
		self._assert_displayed_streamer_details(displayed_streamer,
				streamer_id2, streamer_name2, url_by_id2,
				num_stars=1, url_by_name=url_by_name2, is_starred=True, num_matches=1)

		# Assert that the first user's calendar has the first match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id1)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		next_match = displayed_calendar.next_match
		self._assert_displayed_match(next_match, match_id1,
				self.time, num_streams=1, game=self.game, league=self.league)
		self._assert_displayed_team(next_match.team1, team1_id, self.team1_name)
		self._assert_displayed_team(next_match.team2, team2_id, self.team2_name)

		# Assert that the second user's calendar has the second match.
		displayed_calendar = db.get_displayed_viewer_calendar(client_id2)
		self._assert_displayed_calendar(displayed_calendar,
				has_next_match=True, num_matches=1)
		next_match = displayed_calendar.next_match
		self._assert_displayed_match(next_match, match_id2,
				time2, num_streams=1, game=self.game, league=self.league)
		self._assert_displayed_team(next_match.team1, team1_id, self.team1_name)
		self._assert_displayed_team(next_match.team2, team2_id, self.team2_name)

