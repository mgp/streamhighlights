from datetime import datetime, timedelta
import db
import flask
import pytz
import unittest
import views
from views import app

class ViewsTestCase(unittest.TestCase):
	def setUp(self):
		unittest.TestCase.setUp(self)

		self.now = datetime(2013, 1, 5, 22, 30, 0)

	def _get_displayed_team_details(self, team_id=None,
			name=None, num_stars=None, is_starred=None, game=None, division=None,
			fingerprint=None, matches=None,
			prev_time=None, prev_match_id=None, next_time=None, next_match_id=None):
		"""Returns a DisplayedTeamDetails."""
		return db.DisplayedTeamDetails(team_id,
				name, num_stars, is_starred, game, division, fingerprint, matches,
				prev_time, prev_match_id, next_time, next_match_id)

	def _get_displayed_match_details(self, match_id=None,
			team1=None, team2=None, time=None, num_stars=None, num_streams=None, is_starred=None,
			game=None, division=None, fingerprint=None, streamers=None,
			prev_time=None, prev_streamer_id=None, next_time=None, next_streamer_id=None):
		"""Returns a DisplayedMatchDetails."""
		return db.DisplayedMatchDetails(match_id,
				team1, team2, time, num_stars, num_streams, is_starred,
				game, division, fingerprint, streamers,
				prev_time, prev_streamer_id, next_time, next_streamer_id)

	def _get_displayed_streamer(self, streamer_id=None,
			name=None, num_stars=None, is_starred=None,
			image_url_small=None, image_url_large=None):
		"""Returns a DisplayedStreamer."""
		return db.DisplayedStreamer(streamer_id,
				name, num_stars, is_starred, image_url_small, image_url_large)

	def test_resize_large_picture(self):
		large_size = 300
		image_url_format = 'http://static-cdn.jtvnw.net/jtv_user_pictures/seanbud-%sx%s.jpeg'
		image_url_large = image_url_format % (large_size, large_size) 
		displayed_streamer = self._get_displayed_streamer(image_url_large=image_url_large)
		new_size = 28
		image_url_resized = views._resize_large_picture(displayed_streamer, new_size)
		expected_image_url_resized = image_url_format % (new_size, new_size)
		self.assertEqual(expected_image_url_resized, image_url_resized)

	def test_get_team_external_url(self):
		league = 'esea'
		team_url_part = 'abc'
		fingerprint = views._TEAM_URL_SEPARATOR.join((league, team_url_part))
		displayed_team = self._get_displayed_team_details(fingerprint=fingerprint)
		external_url = views._get_team_external_url(displayed_team)
		self.assertEqual('http://play.esea.net/teams/abc', external_url)
	
	def test_get_match_external_url(self):
		league = 'esea'
		match_url_part = '123'
		fingerprint = views._MATCH_URL_SEPARATOR.join((league, match_url_part))
		displayed_match = self._get_displayed_match_details(fingerprint=fingerprint)
		external_url = views._get_match_external_url(displayed_match)
		self.assertEqual('http://play.esea.net/index.php?s=stats&d=match&id=123',
				external_url)

	def test_get_readable_datetime_localized(self):
		with app.test_request_context('/'):
			# Los Angeles is 8 hours behind UTC.
			flask.g.time_zone = pytz.timezone('America/Los_Angeles')
			# Assert the 24 hour format.
			flask.g.time_format = '24_hour'
			self.assertEqual('Sat Jan 05 14:30', views._get_readable_datetime(self.now))
			# Assert the 24 hour format.
			flask.g.time_format = '12_hour'
			self.assertEqual('Sat Jan 05 02:30PM', views._get_readable_datetime(self.now))

	def test_get_readable_datetime_utc(self):
		with app.test_request_context('/'):
			# No time zone assigned so displaying UTC.
			flask.g.time_zone = None
			# Assert the 24 hour format.
			flask.g.time_format = '24_hour'
			self.assertEqual('Sat Jan 05 22:30 UTC', views._get_readable_datetime(self.now))
			# Assert the 12 hour format.
			flask.g.time_format = '12_hour'
			self.assertEqual('Sat Jan 05 10:30PM UTC', views._get_readable_datetime(self.now))

	def _assert_time_between(self,
			now, expected_days, expected_hours, expected_minutes):
		td = timedelta(days=expected_days, hours=expected_hours, minutes=expected_minutes)
		days, hours, minutes = views._get_time_between(now + td, now)
		self.assertEqual(expected_days, days)
		self.assertEqual(expected_hours, hours)
		self.assertEqual(expected_minutes, minutes)

	def test_get_time_between(self):
		self._assert_time_between(self.now, 0, 0, 0)
		self._assert_time_between(self.now, 0, 0, 5)
		self._assert_time_between(self.now, 0, 5, 0)
		self._assert_time_between(self.now, 0, 5, 5)
		self._assert_time_between(self.now, 5, 0, 0)
		self._assert_time_between(self.now, 5, 0, 5)
		self._assert_time_between(self.now, 5, 5, 0)
		self._assert_time_between(self.now, 5, 5, 5)

	def _assert_time_between_string(self, days, hours, minutes, expected_string):
		self.assertEqual(
				expected_string, views._get_time_between_string(days, hours, minutes))

	def test_get_time_between_string(self):
		self._assert_time_between_string(5, 5, 5, "5 days, 5 hours, 5 minutes")
		self._assert_time_between_string(5, 5, 0, "5 days, 5 hours")
		self._assert_time_between_string(5, 1, 0, "5 days, 1 hour")
		self._assert_time_between_string(5, 0, 5, "5 days, 5 minutes")
		self._assert_time_between_string(5, 0, 1, "5 days, 1 minute")
		self._assert_time_between_string(5, 0, 0, "5 days")

		self._assert_time_between_string(1, 5, 5, "1 day, 5 hours, 5 minutes")
		self._assert_time_between_string(1, 5, 0, "1 day, 5 hours")
		self._assert_time_between_string(1, 1, 0, "1 day, 1 hour")
		self._assert_time_between_string(1, 0, 5, "1 day, 5 minutes")
		self._assert_time_between_string(1, 0, 1, "1 day, 1 minute")
		self._assert_time_between_string(1, 0, 0, "1 day")

		self._assert_time_between_string(0, 5, 5, "5 hours, 5 minutes")
		self._assert_time_between_string(0, 5, 1, "5 hours, 1 minute")
		self._assert_time_between_string(0, 5, 0, "5 hours")

		self._assert_time_between_string(0, 1, 5, "1 hour, 5 minutes")
		self._assert_time_between_string(0, 1, 1, "1 hour, 1 minute")
		self._assert_time_between_string(0, 1, 0, "1 hour")

		self._assert_time_between_string(0, 0, 5, "5 minutes")
		self._assert_time_between_string(0, 0, 1, "1 minute")
		self._assert_time_between_string(0, 0, 0, "")

