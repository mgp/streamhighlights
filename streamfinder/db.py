from datetime import datetime, timedelta
import re
import sqlalchemy as sa
import sqlalchemy.engine as sa_engine
import sqlalchemy.ext.declarative as sa_ext_declarative
import sqlalchemy.orm as sa_orm
import sqlalchemy.schema as sa_schema
import sys

import common_db
from common_db import _get_now, session, close_session

"""A user of the site.
"""
class User(common_db.UserMixin, common_db._Base):
	__tablename__ = 'Users'

	num_stars = sa.Column(sa.Integer, default=0, nullable=False)
	can_stream = sa.Column(sa.Boolean, default=False, nullable=False)
	stream_description = sa.Column(sa.String)

	def __repr__(self):
		return 'User(id=%r, name=%r, image_url_small=%r, image_url_large=%r, created=%r, last_seen=%r, url_by_id=%r, url_by_name=%r, num_stars=%r, can_stream=%r, stream_description=%r, steam_user=%r, twitch_user=%r)' % (
				self.id,
				self.name,
				self.image_url_small,
				self.image_url_large,
				self.created.isoformat(),
				self.last_seen.isoformat() if self.last_seen else None,
				self.url_by_id,
				self.url_by_name,
				self.num_stars,
				self.can_stream,
				self.stream_description,
				self.steam_user,
				self.twitch_user)


_SETTINGS_TIME_FORMATS = ('12_hour', '24_hour')
_DEFAULT_SETTINGS_TIME_FORMAT = '24_hour'

class Settings(common_db._Base):
	__tablename__ = 'Settings'

	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'), primary_key=True)
	time_format = sa.Column(
			sa.Enum(*_SETTINGS_TIME_FORMATS, name='SettingsTimeFormat'),
			nullable=False, default=_DEFAULT_SETTINGS_TIME_FORMAT)
	country = sa.Column(sa.String)
	time_zone = sa.Column(sa.String)

	def __repr__(self):
		return 'Settings(user_id=%r, time_format=%r, country=%r, time_zone=%r)' % (
				self.user_id,
				self.time_format,
				self.country,
				self.time_zone)


"""A team in a match.
"""
class Team(common_db._Base):
	__tablename__ = 'Teams'

	id = sa.Column(sa.Integer, primary_key=True)
	display_name = sa.Column(sa.String, nullable=False)
	indexed_name = sa.Column(sa.String, nullable=False)
	game = sa.Column(sa.String, nullable=False)
	division = sa.Column(sa.String, nullable=False)
	num_stars = sa.Column(sa.Integer, default=0, nullable=False)
	fingerprint = sa.Column(sa.String, nullable=False)

	def __repr__(self):
		return 'Team(id=%r, display_name=%r, indexed_name=%r, game=%r, division=%r, num_stars=%r, fingerprint=%r)' % (
				self.id,
				self.display_name,
				self.indexed_name,
				self.game,
				self.division,
				self.num_stars,
				self.url,
				self.fingerprint)


"""A match between teams.
"""
class Match(common_db._Base):
	__tablename__ = 'Matches'

	id = sa.Column(sa.Integer, primary_key=True)
	team1_id = sa.Column(sa.Integer, sa.ForeignKey('Teams.id'), nullable=False)
	team2_id = sa.Column(sa.Integer, sa.ForeignKey('Teams.id'), nullable=False)
	time = sa.Column(sa.DateTime, nullable=False)
	game = sa.Column(sa.String, nullable=False)
	division = sa.Column(sa.String, nullable=False)
	num_stars = sa.Column(sa.Integer, default=0, nullable=False)
	num_streams = sa.Column(sa.Integer, default=0, nullable=False)
	is_streamed = sa.Column(sa.Boolean, default=False, nullable=False)
	fingerprint = sa.Column(sa.String, nullable=False)

	def __repr__(self):
		return 'Match(id=%r, team1_id=%r, team2_id=%r, time=%r, game=%r, division=%r, num_stars=%r, num_streams=%r, is_streamed=%r, fingerprint=%r)' % (
				self.id,
				self.team1_id,
				self.team2_id,
				self.time,
				self.game,
				self.division,
				self.num_stars,
				self.num_streams,
				self.is_streamed,
				self.fingerprint)


"""The association between a team in a match and its opponent.
"""
class MatchOpponent(common_db._Base):
	__tablename__ = 'MatchOpponents'

	team_id = sa.Column(sa.Integer, sa.ForeignKey('Teams.id'), primary_key=True)
	match_id = sa.Column(sa.Integer, sa.ForeignKey('Matches.id'), primary_key=True)
	is_streamed = sa.Column(sa.Boolean, default=False, nullable=False)
	time = sa.Column(sa.DateTime, nullable=False)
	opponent_id = sa.Column(sa.Integer, sa.ForeignKey('Teams.id'), nullable=False)

	def __repr__(self):
		return 'MatchOpponent(team_id=%r, match_id=%r, is_streamed=%r, time=%r, opponent_id=%r)' % (
				self.team_id,
				self.match_id,
				self.is_streamed,
				self.time,
				self.opponent_id)


"""An edit for a match.
"""
class MatchEdit(common_db._Base):
	__tablename__ = 'MatchEdits'

	id = sa.Column(sa.Integer, primary_key=True)
	match_id = sa.Column(sa.Integer, sa.ForeignKey('Matches.id'), nullable=False)
	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'), nullable=False)
	action = sa.Column(sa.Enum('edit_time', 'cancel', name='MatchEditAction'), nullable=False)
	data = sa.Column(sa.String)
	comment = sa.Column(sa.String)

	def __repr__(self):
		return 'MatchEdit(id=%r, match_id=%r, user_id=%r, action=%r, data=%r, comment=%r)' % (
				self.id,
				self.match_id,
				self.user_id,
				self.action,
				self.data,
				self.comment)


"""The association from users to their starred matches.
"""
class StarredMatch(common_db._Base):
	__tablename__ = 'StarredMatches'

	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'), primary_key=True)
	match_id = sa.Column(sa.Integer, sa.ForeignKey('Matches.id'), primary_key=True)
	time = sa.Column(sa.DateTime, nullable=False)
	added = sa.Column(sa.DateTime, nullable=False)

	def __repr__(self):
		return 'StarredMatch(user_id=%r, match_id=%r, time=%r, added=%r)' % (
				self.user_id,
				self.match_id,
				self.time,
				self.added)


"""The association from users to their starred teams.
"""
class StarredTeam(common_db._Base):
	__tablename__ = 'StarredTeams'

	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'), primary_key=True)
	team_id = sa.Column(sa.Integer, sa.ForeignKey('Teams.id'), primary_key=True)
	indexed_name = sa.Column(sa.String, nullable=False)
	added = sa.Column(sa.DateTime, nullable=False)

	def __repr__(self):
		return 'StarredTeam(user_id=%r, team_id=%r, indexed_name=%r, added=%r)' % (
				self.user_id,
				self.team_id,
				self.indexed_name,
				self.added)


"""The association from users to their starred streaming users.
"""
class StarredStreamer(common_db._Base):
	__tablename__ = 'StarredStreamers'

	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'), primary_key=True)
	streamer_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'), primary_key=True)
	indexed_name = sa.Column(sa.String, nullable=False)
	added = sa.Column(sa.DateTime, nullable=False)

	def __repr__(self):
		return 'StarredStreamer(user_id=%r, streamer_id=%r, indexed_name=%r, added=%r)' % (
				self.user_id,
				self.streamer_id,
				self.indexed_name,
				self.added)


"""The association from streaming users to their streamed matches.
"""
class StreamedMatch(common_db._Base):
	__tablename__ = 'StreamedMatches'

	streamer_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'), primary_key=True)
	match_id = sa.Column(sa.Integer, sa.ForeignKey('Matches.id'), primary_key=True)
	time = sa.Column(sa.DateTime, nullable=False)
	added = sa.Column(sa.DateTime, nullable=False)
	comment = sa.Column(sa.String)

	def __repr__(self):
		return 'StreamedMatch(streamer_id=%r, match_id=%r, time=%r, added=%r, comment=%r)' % (
				self.streamer_id,
				self.match_id,
				self.time,
				self.added,
				self.comment)


"""An entry in a user's calendar.
"""
class CalendarEntry(common_db._Base):
	__tablename__ = 'CalendarEntries'

	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'), primary_key=True)
	match_id = sa.Column(sa.Integer, sa.ForeignKey('Matches.id'), primary_key=True)
	time = sa.Column(sa.DateTime, nullable=False)
	num_user_stars = sa.Column(sa.Integer, default=0, nullable=False)

	def __repr__(self):
		return 'CalendarEntry(user_id=%r, match_id=%r, time=%r, num_user_stars=%r)' %  (
				self.user_id,
				self.match_id,
				self.time,
				self.num_user_stars)


# Used by method add_match.
sa_schema.Index('TeamsByFingerprint', Team.fingerprint, unique=True)
# Used by method add_team.
sa_schema.Index('MatchesByFingerprint', Match.fingerprint, unique=True)
# Used by methods _add_star_team, _remove_star_team.
sa_schema.Index('MatchOpponentsByTeamIdAndIsStreamed',
		MatchOpponent.team_id, MatchOpponent.is_streamed)
# Used by method _add_first_stream_calendar_entries.
sa_schema.Index('MatchOpponentsByMatchId', MatchOpponent.match_id)
sa_schema.Index('StarredMatchesByMatchId', StarredMatch.match_id)
sa_schema.Index('StarredTeamsByTeamId', StarredTeam.team_id)
sa_schema.Index('StarredStreamersByStreamerId', StarredStreamer.streamer_id)
# Used by method _remove_last_stream_calendar_entries.
sa_schema.Index('CalendarEntriesByMatchId', CalendarEntry.match_id)

# Used by method get_displayed_calendar.
sa_schema.Index('CalendarEntriesByUserIdAndTimeAndMatchId',
		CalendarEntry.user_id, CalendarEntry.time, CalendarEntry.match_id)
# Used by method get_displayed_match.
sa_schema.Index('StreamedMatchesByMatchIdAndAddedAndStreamerId',
		StreamedMatch.match_id, StreamedMatch.added, StreamedMatch.streamer_id)
# Used by method get_displayed_team.
sa_schema.Index('MatchOpponentsByTeamIdAndTimeAndMatchId',
		MatchOpponent.team_id, MatchOpponent.time, MatchOpponent.match_id)
# Used by method get_displayed_streamer.
sa_schema.Index('StreamedMatchesByStreamerIdAndTimeAndMatchId',
		StreamedMatch.streamer_id, StreamedMatch.time, StreamedMatch.match_id)


def create_all():
	common_db.create_all()

	global Users
	global SettingsTable
	global Teams
	global Matches
	global MatchOpponents
	global MatchEdits
	global StarredMatches
	global StarredTeams
	global StarredStreamers
	global StreamedMatches
	global CalendarEntries

	# Create aliases for each table.
	Users = User.__table__
	SettingsTable = Settings.__table__
	Teams = Team.__table__
	Matches = Match.__table__
	MatchOpponents = MatchOpponent.__table__
	MatchEdits = MatchEdit.__table__
	StarredMatches = StarredMatch.__table__
	StarredTeams = StarredTeam.__table__
	StarredStreamers = StarredStreamer.__table__
	StreamedMatches = StreamedMatch.__table__
	CalendarEntries = CalendarEntry.__table__

def drop_all():
	global Users
	global SettingsTable
	global Teams
	global Matches
	global MatchOpponents
	global MatchEdits
	global StarredMatches
	global StarredTeams
	global StarredStreamers
	global StreamedMatches

	# Clear aliases for each table.
	Users = None
	SettingsTable = None
	Teams = None
	Matches = None
	MatchOpponents = None
	MatchEdits = None
	StarredMatches = None
	StarredTeams = None
	StarredStreamers = None
	StreamedMatches = None
	CalendarEntries = None

	common_db.drop_all()


@close_session
def add_match(team1_id, team2_id, time, game, division, fingerprint, now=None):
	"""Adds a match between two teams at a given time."""
	try:
		match_id = session.query(Match)\
				.filter(Match.fingerprint == fingerprint)\
				.one()\
				.id
		return match_id
	except sa_orm.exc.NoResultFound:
		# This match does not exist; continue to add the match.
		session.rollback()

	try:
		# Add the match.
		match = Match(team1_id=team1_id, team2_id=team2_id, game=game, division=division, time=time,
				fingerprint=fingerprint)
		session.add(match)
		session.flush()
		match_id = match.id

		# Add each opponent for the match.
		match_opponent1 = MatchOpponent(
				team_id=team1_id, match_id=match_id, time=time, opponent_id=team2_id)
		match_opponent2 = MatchOpponent(
				team_id=team2_id, match_id=match_id, time=time, opponent_id=team1_id)
		session.add(match_opponent1)
		session.add(match_opponent2)
		session.commit()

		return match.id
	except sa.exc.IntegrityError:
		# The commit failed because teams with the given identifiers are missing.
		session.rollback()
		raise common_db.DbException._chain()

@close_session
def add_team(display_name, indexed_name, game, division, fingerprint, now=None):
	"""Adds a team in the given game and division."""
	try:
		team = session.query(Team).filter(Team.fingerprint == fingerprint).one()
		team.display_name = display_name
		team.indexed_name = indexed_name
	except sa_orm.exc.NoResultFound:
		team = Team(display_name=display_name, indexed_name=indexed_name,
				game=game, division=division, fingerprint=fingerprint)
		session.add(team)

	session.commit()
	return team.id

@close_session
def add_star_match(client_id, match_id, now=None):
	"""Adds a star by the client for the match with the given identifier."""
	now = _get_now(now)

	try:
		# Get the time of the match.
		match_time = session.query(Match.time)\
				.filter(Match.id == match_id)\
				.one()\
				.time
		# Add the client's star for the match.
		starred_match = StarredMatch(user_id=client_id,
				match_id=match_id,
				time=match_time,
				added=now)
		session.add(starred_match)
		session.flush()
	except sa_orm.exc.NoResultFound:
		session.rollback()
		raise common_db.DbException._chain()
	except sa.exc.IntegrityError:
		# The flush failed because the client has already starred this match.
		session.rollback()
		raise common_db.DbException._chain()

	# Increment the count of stars for the match.
	match = session.query(Match).filter(Match.id == match_id).one()
	match.num_stars += 1

	# If needed, add a CalendarEntry for the streamed match.
	if match.is_streamed:
		_increment_num_user_stars(client_id, match, now)

	session.commit()

@close_session
def remove_star_match(client_id, match_id, now=None):
	"""Removes a star by the client for the match with the given identifier."""
	now = _get_now(now)

	# Remove the client's star for the match.
	result = session.execute(StarredMatches.delete().where(sa.and_(
			StarredMatch.user_id == client_id,
			StarredMatch.match_id == match_id)))
	if not result.rowcount:
		session.rollback()
		return

	# Decrement the count of stars for the match.
	session.execute(Matches.update()
			.where(Match.id == match_id)
			.values({Match.num_stars: Match.num_stars - 1}))

	# If needed, remove a CalendarEntry for the streamed match.
	is_streamed = session.query(Match.is_streamed)\
			.filter(Match.id == match_id)\
			.one()\
			.is_streamed
	if is_streamed:
		_decrement_num_user_stars(client_id, match_id, now)

	session.commit()

@close_session
def add_star_team(client_id, team_id, now=None):
	"""Adds a star by the client for the team with the given identifier."""
	now = _get_now(now)

	try:
		# Get the indexed name of the team.
		team_indexed_name = session.query(Team.indexed_name)\
				.filter(Team.id == team_id)\
				.one()\
				.indexed_name
		# Add the client's star for the team.
		starred_team = StarredTeam(user_id=client_id,
				team_id=team_id,
				indexed_name=team_indexed_name,
				added=now)
		session.add(starred_team)
		session.flush()
	except sa_orm.exc.NoResultFound:
		session.rollback()
		raise common_db.DbException._chain()
	except sa.exc.IntegrityError:
		# The flush failed because the client has already starred this team.
		session.rollback()
		raise common_db.DbException._chain()

	# Increment the count of stars for the team.
	session.execute(Teams.update()
			.where(Team.id == team_id)
			.values({Team.num_stars: Team.num_stars + 1}))

	# If needed, add a CalendarEntry for each streamed match.
	matches_cursor = session.query(MatchOpponent.match_id, Match)\
			.join(Match, MatchOpponent.match_id == Match.id)\
			.filter(MatchOpponent.team_id == team_id, MatchOpponent.is_streamed == True)
	for match_id, match in matches_cursor:
		_increment_num_user_stars(client_id, match, now)
	
	session.commit()

@close_session
def remove_star_team(client_id, team_id, now=None):
	"""Removes a star by the client for the team with the given identifier."""
	now = _get_now(now)

	# Remove the client's star for the team.
	result = session.execute(StarredTeams.delete().where(sa.and_(
			StarredTeam.user_id == client_id,
			StarredTeam.team_id == team_id)))
	if not result.rowcount:
		session.rollback()
		return

	# Decrement the count of stars for the team.
	session.execute(Teams.update()
			.where(Team.id == team_id)
			.values({Team.num_stars: Team.num_stars - 1}))

	# If needed, remove a CalendarEntry for each streamed match.
	match_ids_cursor = session.query(MatchOpponent.match_id)\
			.filter(MatchOpponent.team_id == team_id, MatchOpponent.is_streamed == True)
	for row in match_ids_cursor:
		_decrement_num_user_stars(client_id, row.match_id, now)

	session.commit()

@close_session
def add_star_streamer(client_id, streamer_id, now=None):
	"""Adds a star by the client for the streaming user with the given identifier."""
	now = _get_now(now)

	try:
		# Get the indexed name of the streaming user.
		streamer_indexed_name = session.query(User.indexed_name)\
				.filter(User.id == streamer_id)\
				.one()\
				.indexed_name
		# Add the client's star for the streaming user.
		starred_streamer = StarredStreamer(user_id=client_id,
				streamer_id=streamer_id,
				indexed_name=streamer_indexed_name,
				added=now)
		session.add(starred_streamer)
		session.flush()
	except sa_orm.exc.NoResultFound:
		session.rollback()
		raise common_db.DbException._chain()
	except sa.exc.IntegrityError:
		# The flush failed because the client has already starred this streaming user.
		session.rollback()
		raise common_db.DbException._chain()

	# Increment the count of stars for the streaming user.
	session.execute(Users.update()
			.where(User.id == streamer_id)
			.values({User.num_stars: User.num_stars + 1}))

	# If needed, add a CalendarEntry for each streamed match.
	matches_cursor = session.query(StreamedMatch.match_id, Match)\
			.join(Match, StreamedMatch.match_id == Match.id)\
			.filter(StreamedMatch.streamer_id == streamer_id)
	for match_id, match in matches_cursor:
		_increment_num_user_stars(client_id, match, now)

	session.commit()

@close_session
def remove_star_streamer(client_id, streamer_id, now=None):
	"""Removes a star by the client for the streaming user with the given identifier."""
	now = _get_now(now)

	# Remove the client's star for the streaming user.
	result = session.execute(StarredStreamers.delete().where(sa.and_(
			StarredStreamer.user_id == client_id,
			StarredStreamer.streamer_id == streamer_id)))
	if not result.rowcount:
		session.rollback()
		return

	# Decrement the count of stars for the streaming user.
	session.execute(Users.update()
			.where(User.id == streamer_id)
			.values({User.num_stars: User.num_stars - 1}))

	# If needed, remove a CalendarEntry for each streamed match.
	match_ids_cursor = session.query(StreamedMatch.match_id)\
			.filter(StreamedMatch.streamer_id == streamer_id)
	for row in match_ids_cursor:
		_decrement_num_user_stars(client_id, row.match_id, now)

	session.commit()


def _set_match_opponent_streaming(match_id, is_streamed):
		session.execute(MatchOpponents.update()
				.where(MatchOpponent.match_id == match_id)
				.values({MatchOpponent.is_streamed: is_streamed}))

@close_session
def add_stream_match(client_id, match_id, comment=None, now=None):
	"""Adds a stream by the client for the match with the given identifier."""
	now = _get_now(now)

	try:
		match = session.query(Match).filter(Match.id == match_id).one()
	except sa_orm.exc.NoResultFound:
		session.rollback()
		raise common_db.DbException._chain()

	# Add the client as a user streaming the match.
	streamed_match = StreamedMatch(streamer_id=client_id,
			match_id=match_id,
			time=match.time,
			added=now,
			comment=comment)
	session.add(streamed_match)

	if match.num_streams > 0:
		# This is not the first streaming user for the match.
		match.num_streams += 1
		_add_not_first_stream_calendar_entries(client_id, match, now)
	else:
		# This is the first streaming user for the match.
		_set_match_opponent_streaming(match_id, True)

		match.num_streams = 1
		match.is_streamed = True
		_add_first_stream_calendar_entries(client_id, match, now)

	session.commit()

@close_session
def remove_stream_match(client_id, match_id, now=None):
	"""Removes a stream by the client for the match with the given identifier."""
	now = _get_now(now)

	# Remove the client as a user streaming the match.
	result = session.execute(StreamedMatches.delete().where(sa.and_(
			StreamedMatch.streamer_id == client_id,
			StreamedMatch.match_id == match_id)))
	if not result.rowcount:
		session.rollback()
		return
	
	num_streams, team1_id, team2_id = session\
			.query(Match.num_streams, Match.team1_id, Match.team2_id)\
			.filter(Match.id == match_id)\
			.one()
	if num_streams > 1:
		# This was not the last streaming user for the match.
		session.execute(Matches.update()
				.where(Match.id == match_id)
				.values({Match.num_streams: num_streams - 1}))
		_remove_not_last_stream_calendar_entries(client_id, match_id, now)
	else:
		# This was the last streaming user for the match.
		_set_match_opponent_streaming(match_id, False)

		session.execute(Matches.update()
				.where(Match.id == match_id)
				.values({Match.num_streams: 0, Match.is_streamed: False}))
		_remove_last_stream_calendar_entries(client_id, match_id, now)
	
	session.commit()


def _get_calendar_entry(user_id, match):
	"""Returns a CalendarEntry created with the given user identifier and match."""
	return CalendarEntry(user_id=user_id,
			match_id=match.id,
			time=match.time,
			num_user_stars=1)


def _multi_increment_num_user_stars(user_ids, match, now):
	for user_id in user_ids:
		_increment_num_user_stars(user_id, match, now)

def _increment_num_user_stars(user_id, match, now):
	"""Updates or creates a CalendarEntry for the given user identifier and match."""
	assert match.is_streamed

	missing = session.query(CalendarEntry)\
			.filter(
				CalendarEntry.user_id == user_id,
				CalendarEntry.match_id == match.id)\
			.count() == 0
	if missing:
		# No existing CalendarEntry; create a new one.
		entry = _get_calendar_entry(user_id, match)
		session.add(entry)
	else:
		# Increment the count of stars for an existing CalendarEntry.
		session.execute(CalendarEntries.update()
				.where(sa.and_(
					CalendarEntry.user_id == user_id,
					CalendarEntry.match_id == match.id))
				.values({CalendarEntry.num_user_stars: CalendarEntry.num_user_stars + 1}))


def _multi_decrement_num_user_stars(user_ids, match_id, now):
	for user_id in user_ids:
		_decrement_num_user_stars(user_id, match_id, now)

def _decrement_num_user_stars(user_id, match_id, now):
	"""Updates or deletes a CalendarEntry for the given user and match identifier."""
	num_user_stars = session.query(CalendarEntry.num_user_stars)\
			.filter(
				CalendarEntry.user_id == user_id,
				CalendarEntry.match_id == match_id)\
			.one()\
			.num_user_stars
	if num_user_stars > 1:
		# Decrement the count of stars for the CalendarEntry to a positive integer.
		session.execute(CalendarEntries.update()
				.where(sa.and_(
					CalendarEntry.user_id == user_id,
					CalendarEntry.match_id == match_id))
				.values({CalendarEntry.num_user_stars: num_user_stars - 1}))
	else:
		# Delete the CalendarEntry becuase the count of stars is now zero.
		session.execute(CalendarEntries.delete().where(sa.and_(
				CalendarEntry.user_id == user_id,
				CalendarEntry.match_id == match_id)))


def _add_first_stream_calendar_entries(client_id, match, now):
	"""Updates or creates CalendarEntries for users, given that the client was
	added as the first streaming user.
	"""
	# Add a CalendarEntry for each user who starred the match.
	user_ids_cursor = session.query(StarredMatch.user_id)\
			.filter(StarredMatch.match_id == match.id)
	for row in user_ids_cursor:
		entry = _get_calendar_entry(row.user_id, match)
		session.add(entry)
	session.flush()

	# Add a CalendarEntry for each user who starred either team.
	user_ids_cursor = session.query(MatchOpponent.match_id, StarredTeam.user_id)\
			.join(StarredTeam, MatchOpponent.team_id == StarredTeam.team_id)\
			.filter(MatchOpponent.match_id == match.id)
	user_ids_cursor = (row.user_id for row in user_ids_cursor)
	_multi_increment_num_user_stars(user_ids_cursor, match, now)
	session.flush()

	# Add a CalendarEntry for each user who starred the streaming user.
	user_ids_cursor = session.query(StarredStreamer.user_id)\
			.filter(StarredStreamer.streamer_id == client_id)
	user_ids_cursor = (row.user_id for row in user_ids_cursor)
	_multi_increment_num_user_stars(user_ids_cursor, match, now)
	session.flush()

def _add_not_first_stream_calendar_entries(client_id, match, now):
	"""Updates or creates CalendarEntries for users, given that the client was
	added as a streamer, but not the first one.
	"""
	# If needed, add a CalendarEntry for each user who starred the streaming user.
	user_ids_cursor = session.query(StarredStreamer.user_id)\
			.filter(StarredStreamer.streamer_id == client_id)
	user_ids_cursor = (row.user_id for row in user_ids_cursor)
	_multi_increment_num_user_stars(user_ids_cursor, match, now)


def _remove_not_last_stream_calendar_entries(client_id, match_id, now):
	"""Updates or deletes CalendarEntries for users, given that the client was
	removed as a streamer, but not the last one.
	"""
	# If needed, remove a CalendarEntry for each user who starred the streaming user.
	user_ids_cursor = session.query(StarredStreamer.user_id)\
			.filter(StarredStreamer.streamer_id == client_id)
	user_ids_cursor = (row.user_id for row in user_ids_cursor)
	_multi_decrement_num_user_stars(user_ids_cursor, match_id, now)

def _remove_last_stream_calendar_entries(client_id, match_id, now):	
	"""Updates or deletes CalendarEntries for users, given that the client was
	removed as the last streaming user.
	"""
	# Remove every CalendarEntry for this match.
	result = session.execute(
			CalendarEntries.delete().where(CalendarEntry.match_id == match_id))


"""Settings for a user."""
class DisplayedSettings:
	def __init__(self, time_format, country, time_zone):
		self.time_format = time_format
		self.country = country
		self.time_zone = time_zone

	def __repr__(self):
		return 'Settings(time_format=%r, country=%r, time_zone=%r)' % (
				self.time_format,
				self.country,
				self.time_zone)

@close_session
def get_settings(client_id):
	"""Returns the DisplayedSettings for the given client.

	If no settings have yet been saved by the user, default values are returned.
	"""
	try:
		settings = session.query(Settings)\
				.filter(Settings.user_id == client_id)\
				.one()
		return DisplayedSettings(settings.time_format,
				settings.country,
				settings.time_zone)
	except sa_orm.exc.NoResultFound:
		session.rollback()
		return DisplayedSettings(_DEFAULT_SETTINGS_TIME_FORMAT, None, None)

@close_session
def save_settings(client_id, time_format, country, time_zone):
	"""Saves settings for the given client."""
	settings = Settings(user_id=client_id,
			time_format=time_format,
			country=country,
			time_zone=time_zone)
	session.merge(settings)
	session.commit()


"""A view of a match."""
class DisplayedMatch:
	def __init__(self, match_id, team1, team2, time, num_stars, num_streams, is_starred,
			game=None, division=None):
		self.match_id = match_id
		self.team1 = team1
		self.team2 = team2
		self.time = time
		self.num_stars = num_stars
		self.num_streams = num_streams
		self.is_starred = is_starred
		# Begin optional arguments.
		self.game = game
		self.division = division

	def __repr__(self):
		return 'DisplayedMatch(match_id=%r, team1=%r, team2=%r, time=%r, num_stars=%r, num_streams=%r, is_starred=%r, game=%r, division=%r)' % (
				self.match_id,
				self.team1,
				self.team2,
				self.time,
				self.num_stars,
				self.num_streams,
				self.is_starred,
				self.game,
				self.division)

"""A detailed view of a match.

Includes whether the client has starred the match, and all of the match's
streamers.
"""
class DisplayedMatchDetails(DisplayedMatch):
	def __init__(self, match_id, team1, team2, time, num_stars, num_streams, is_starred,
			game, division, fingerprint, streamers,
			prev_time, prev_streamer_id, next_time, next_streamer_id):
		DisplayedMatch.__init__(self,
				match_id, team1, team2, time, num_stars, num_streams, is_starred,
				game, division)
		self.fingerprint = fingerprint
		self.streamers = streamers
		self.prev_time = prev_time
		self.prev_streamer_id = prev_streamer_id
		self.next_time = next_time
		self.next_streamer_id = next_streamer_id

	def __repr__(self):
		return 'DisplayedMatchDetails(match_id=%r, team1=%r, team2=%r, time=%r, num_stars=%r, num_streams=%r, is_starred=%r, game=%r, division=%r, fingerprint=%r, streamers=%r, prev_time=%r, prev_streamer_id=%r, next_time=%r, next_streamer_id=%r)' % (
				self.match_id,
				self.team1,
				self.team2,
				self.time,
				self.num_stars,
				self.num_streams,
				self.is_starred,
				self.game,
				self.division,
				self.fingerprint,
				self.streamers,
				self.prev_time,
				self.prev_streamer_id,
				self.next_time,
				self.next_streamer_id)


"""A view of a team."""
class DisplayedTeam:
	def __init__(self, team_id, name, num_stars, is_starred, game=None, division=None):
		self.team_id = team_id
		self.name = name
		self.num_stars = num_stars
		self.is_starred = is_starred
		# Optional arguments.
		self.game = game
		self.division = division

	def __repr__(self):
		return 'DisplayedTeam(team_id=%r, name=%r, num_stars=%r, is_starred=%r, game=%r, division=%r)' % (
				self.team_id,
				self.name,
				self.num_stars,
				self.is_starred,
				self.game,
				self.division)

"""A detailed view of a team.

Includes whether the client has starred the team, and all of the team's matches.
"""
class DisplayedTeamDetails(DisplayedTeam):
	def __init__(self, team_id, name, num_stars, is_starred, game, division,
			fingerprint, matches,
			prev_time, prev_match_id, next_time, next_match_id):
		DisplayedTeam.__init__(self, team_id, name, num_stars, is_starred, game, division)
		self.fingerprint = fingerprint
		self.matches = matches
		self.prev_time = prev_time
		self.prev_match_id = prev_match_id
		self.next_time = next_time
		self.next_match_id = next_match_id

	def __repr__(self):
		return 'DisplayedTeamDetails(team_id=%r, name=%r, num_stars=%r, is_starred=%r, game=%r, division=%r, fingerprint=%r, matches=%r, prev_time=%r, prev_match_id=%r, next_time=%r, next_match_id=%r)' % (
				self.team_id,
				self.name,
				self.num_stars,
				self.is_starred,
				self.game,
				self.division,
				self.fingerprint,
				self.matches,
				self.prev_time,
				self.prev_match_id,
				self.next_time,
				self.next_match_id)


"""A view of a streaming user."""
class DisplayedStreamer:
	def __init__(self,
			streamer_id, name, num_stars, is_starred, image_url_small, image_url_large,
			url_by_id=None, url_by_name=None):
		self.streamer_id = streamer_id
		self.name = name
		self.num_stars = num_stars
		self.is_starred = is_starred
		self.image_url_small = image_url_small
		self.image_url_large = image_url_large
		self.url_by_id = url_by_id
		self.url_by_name = url_by_name

	def __repr__(self):
		return 'DisplayedStreamer(streamer_id=%r, name=%r, num_stars=%r, is_starred=%r, image_url_small=%r, image_url_large=%r, url_by_id=%r, url_by_name=%r)' % (
				self.streamer_id,
				self.name,
				self.num_stars,
				self.is_starred,
				self.image_url_small,
				self.image_url_large,
				self.url_by_id,
				self.url_by_name)

"""A detailed view of a streaming user.

Includes whether the client has starred the streaming user, and all of the
matches the user is streaming.
"""
class DisplayedStreamerDetails(DisplayedStreamer):
	def __init__(self,
			streamer_id, name, num_stars, is_starred, image_url_small, image_url_large,
			url_by_id, url_by_name, matches,
			prev_time, prev_match_id, next_time, next_match_id):
		DisplayedStreamer.__init__(self,
				streamer_id, name, num_stars, is_starred, image_url_small, image_url_large,
				url_by_id, url_by_name)
		self.matches = matches
		self.prev_time = prev_time
		self.prev_match_id = prev_match_id
		self.next_time = next_time
		self.next_match_id = next_match_id
	
	def __repr__(self):
		return 'DisplayedStreamerDetails(streamer_id=%r, name=%r, num_stars=%r, is_starred=%r, image_url_small=%r, image_url_large=%r, url_by_id=%r, url_by_name=%r, matches=%r, prev_time=%r, prev_match_id=%r, next_time=%r, next_match_id=%r)' % (
				self.streamer_id,
				self.name,
				self.num_stars,
				self.is_starred,
				self.image_url_small,
				self.image_url_large,
				self.url_by_id,
				self.url_by_name,
				self.matches,
				self.prev_time,
				self.prev_match_id,
				self.next_time,
				self.next_match_id)


"""A list of matches in the Calendar tab.
"""
class DisplayedCalendar:
	def __init__(self, next_match, matches,
			prev_time=None, prev_match_id=None, next_time=None, next_match_id=None):
		self.next_match = next_match
		self.matches = matches
		self.prev_time = prev_time
		self.prev_match_id = prev_match_id
		self.next_time = next_time
		self.next_match_id = next_match_id
	
	def __repr__(self):
		return 'DisplayedCalendar(next_match=%r, matches=%r, prev_time=%r, prev_match_id=%r, next_time=%r, next_match_id=%r)' % (
				self.next_match,
				self.matches,
				self.prev_time,
				self.prev_match_id,
				self.next_time,
				self.next_match_id)


"""A partial list of matches.
"""
class DisplayedMatchList:
	def __init__(self, matches, prev_time, prev_match_id, next_time, next_match_id):
		self.matches = matches
		self.prev_time = prev_time
		self.prev_match_id = prev_match_id
		self.next_time = next_time
		self.next_match_id = next_match_id

	def __repr__(self):
		return 'DisplayedMatchList(matches=%r, prev_time=%r, prev_match_id=%r, next_time=%r, next_match_id=%r)' % (
				self.matches,
				self.prev_time,
				self.prev_match_id,
				self.next_time,
				self.next_match_id)

"""A partial list of teams.
"""
class DisplayedTeamList:
	def __init__(self, teams, prev_name, prev_team_id, next_name, next_team_id):
		self.teams = teams
		self.prev_name = prev_name
		self.prev_team_id = prev_team_id
		self.next_name = next_name
		self.next_team_id = next_team_id

	def __repr__(self):
		return 'DisplayedTeamList(teams=%r, prev_name=%r, prev_team_id=%r, next_name=%r, next_team_id=%r)' % (
				self.teams,
				self.prev_name,
				self.prev_team_id,
				self.next_name,
				self.next_team_id)

"""A partial list of streaming users.
"""
class DisplayedStreamerList:
	def __init__(self, streamers, prev_name, prev_streamer_id, next_name, next_streamer_id):
		self.streamers = streamers
		self.prev_name = prev_name
		self.prev_streamer_id = prev_streamer_id
		self.next_name = next_name
		self.next_streamer_id = next_streamer_id

	def __repr__(self):
		return 'DisplayedStreamerList(streamers=%r, prev_name=%r, prev_streamer_id=%r, next_name=%r, next_streamer_id=%r)' % (
				self.streamers,
				self.prev_name,
				self.prev_streamer_id,
				self.next_name,
				self.next_streamer_id)


_UPCOMING_MATCHES_CUTOFF = timedelta(minutes=-60)

def _get_upcoming_matches_cutoff(now):
	return now + _UPCOMING_MATCHES_CUTOFF

# The default number of entities per page.
_PAGE_LIMIT = 2

def _paginate(paginator, prev_col1, prev_col2, next_col1, next_col2, page_limit,
		first_id=None):
	if first_id is None:
		first_id = paginator.get_first_id()
	if first_id is not None:
		query = paginator.get_partial_list_query()
		last_id = paginator.get_last_id()

		# Add pagination to the query.
		col1, col2 = paginator.get_order_by_columns()
		clicked_prev = prev_col1 and prev_col2
		clicked_next = next_col1 and next_col2
		if clicked_prev:
			query = query\
					.filter(sa.or_(
						sa.and_(col1 == prev_col1, col2 < prev_col2), col1 < prev_col1))\
					.order_by(col1.desc(), col2.desc())
		elif clicked_next:
			query = query\
					.filter(sa.or_(
						sa.and_(col1 == next_col1, col2 > next_col2), col1 > next_col1))\
					.order_by(col1.asc(), col2.asc())
		else:
			# Show the first page.
			query = query.order_by(col1.asc(), col2.asc())

		if page_limit is None:
			page_limit = _PAGE_LIMIT
		query = query.limit(page_limit)

		items = paginator.execute_query(query)
		if clicked_prev:
			# Reverse the partial list if clicked on Previous.
			items = items[::-1]

		prev_col1 = None
		prev_col2 = None
		next_col1 = None
		next_col2 = None
		first_item = items[0]
		last_item = items[-1]
		if not clicked_prev and not clicked_next:
			if (len(items) == page_limit) and not paginator.has_id(last_id, last_item):
				next_col1, next_col2 = paginator.get_pagination_values(last_item)
		elif clicked_prev:
			if (len(items) == page_limit) and not paginator.has_id(first_id, first_item):
				prev_col1, prev_col2 = paginator.get_pagination_values(first_item)
			# Came from the following page, so display a Next link.
			next_col1, next_col2 = paginator.get_pagination_values(last_item)
		elif clicked_next:
			if (len(items) == page_limit) and not paginator.has_id(last_id, last_item):
				next_col1, next_col2 = paginator.get_pagination_values(last_item)
			# Came from the previous page, so display a Previous link.
			prev_col1, prev_col2 = paginator.get_pagination_values(first_item)
	else:
		items = ()
		prev_col1 = None
		prev_col2 = None
		next_col1 = None
		next_col2 = None

	return (items, prev_col1, prev_col2, next_col1, next_col2)


def _get_displayed_match_team(team):
	return DisplayedTeam(team.id, team.display_name, team.num_stars, False)

def _get_displayed_match(match, team1, team2, is_starred):
	"""Returns a DisplayedMatch from the given match and teams."""
	displayed_team1 = _get_displayed_match_team(team1)
	displayed_team2 = _get_displayed_match_team(team2)
	return DisplayedMatch(match.id,
			displayed_team1,
			displayed_team2,
			match.time,
			match.num_stars,
			match.num_streams,
			is_starred,
			match.game,
			match.division)

def _get_calendar_entry_query(client_id, team_alias1, team_alias2, now):
	cutoff_time = _get_upcoming_matches_cutoff(now)
	return session\
			.query(CalendarEntry.match_id, Match, team_alias1, team_alias2)\
			.join(Match, CalendarEntry.match_id == Match.id)\
			.join(team_alias1, Match.team1_id == team_alias1.id)\
			.join(team_alias2, Match.team2_id == team_alias2.id)\
			.filter(CalendarEntry.user_id == client_id)\
			.filter(CalendarEntry.time > cutoff_time)

def _get_next_viewer_match(client_id, team_alias1, team_alias2, now):
	result = common_db.optional_one(
			_get_calendar_entry_query(client_id, team_alias1, team_alias2, now)
				.order_by(CalendarEntry.time.asc(), CalendarEntry.match_id.asc()))
	if result is None:
		return None

	next_match_id, next_match, next_match_team1, next_match_team2 = result
	return _get_displayed_match(
			next_match, next_match_team1, next_match_team2, False)

"""A paginator for entries on the client's viewing calendar.
"""
class CalendarEntriesPaginator:
	def __init__(self, client_id, team_alias1, team_alias2, now):
		self.client_id = client_id
		self.team_alias1 = team_alias1
		self.team_alias2 = team_alias2
		self.now = now
	
	def get_last_id(self):
		cutoff_time = _get_upcoming_matches_cutoff(self.now)
		order_by_columns = (column.desc() for column in self.get_order_by_columns())
		query = session.query(CalendarEntry.match_id)\
				.filter(CalendarEntry.user_id == self.client_id)\
				.filter(CalendarEntry.time > cutoff_time)\
				.order_by(*order_by_columns)
		calendar_entry = common_db.optional_one(query)
		return calendar_entry.match_id

	def get_partial_list_query(self):
		return _get_calendar_entry_query(
				self.client_id, self.team_alias1, self.team_alias2, self.now)

	def get_order_by_columns(self):
		return (CalendarEntry.time, CalendarEntry.match_id)
	
	def execute_query(self, matches_query):
		return tuple((match, team1, team2)
				for match_id, match, team1, team2 in matches_query)
	
	def get_pagination_values(self, item):
		match = item[0]
		return (match.time, match.id)
	
	def has_id(self, queried_id, item):
		match = item[0]
		return (match.id == queried_id)

@close_session
def get_displayed_viewer_calendar(client_id,
		prev_time=None, prev_match_id=None, next_time=None, next_match_id=None,
		page_limit=None, now=None):
	"""Returns a DisplayedCalendar containing calendar entries for streamed matches
	where the client has starred the match, either team, or a streamer.
	"""
	now = _get_now(now)

	# Get the next match for viewing by the client.
	team_alias1 = sa_orm.aliased(Team)
	team_alias2 = sa_orm.aliased(Team)
	first_match = _get_next_viewer_match(client_id, team_alias1, team_alias2, now)
	if first_match is None:
		# No next match, so return an empty calendar.
		return DisplayedCalendar(None, ())

	# Get the partial list of matches.
	paginator = CalendarEntriesPaginator(client_id, team_alias1, team_alias2, now)
	matches, prev_time, prev_match_id, next_time, next_match_id = _paginate(
			paginator, prev_time, prev_match_id, next_time, next_match_id, page_limit,
			first_id=first_match.match_id)

	# Return the calendar.
	return DisplayedCalendar(first_match,
			tuple(_get_displayed_match(match, team1, team2, False)
					for match, team1, team2 in matches),
			prev_time,
			prev_match_id,
			next_time,
			next_match_id)


def _get_streamed_match_query(streamer_id, client_id, team_alias1, team_alias2, now):
	if client_id:
		query = session\
				.query(StreamedMatch.match_id, Match, team_alias1, team_alias2, StarredMatch)\
				.outerjoin(StarredMatch, sa.and_(
					StarredMatch.match_id == StreamedMatch.match_id,
					StarredMatch.user_id == client_id))
	else:
		query = session\
				.query(StreamedMatch.match_id, Match, team_alias1, team_alias2)
	cutoff_time = _get_upcoming_matches_cutoff(now)
	return query\
			.join(Match, StreamedMatch.match_id == Match.id)\
			.join(team_alias1, Match.team1_id == team_alias1.id)\
			.join(team_alias2, Match.team2_id == team_alias2.id)\
			.filter(StreamedMatch.streamer_id == streamer_id)\
			.filter(StreamedMatch.time > cutoff_time)

def _get_next_streamer_match(client_id, team_alias1, team_alias2, now):
	result = common_db.optional_one(
			_get_streamed_match_query(client_id, None, team_alias1, team_alias2, now)
				.order_by(StreamedMatch.time.asc(), StreamedMatch.match_id.asc()))
	if result is None:
		return None

	next_match_id, next_match, next_match_team1, next_match_team2 = result
	return _get_displayed_match(
			next_match, next_match_team1, next_match_team2, False)

@close_session
def get_displayed_streamer_calendar(client_id,
		prev_time=None, prev_match_id=None, next_time=None, next_match_id=None,
		page_limit=None, now=None):
	"""Returns a DisplayedCalendar containing calendar entries for matches that the
	client is streaming.
	"""
	now = _get_now(now)

	# Get the next match streamed by the client.
	team_alias1 = sa_orm.aliased(Team)
	team_alias2 = sa_orm.aliased(Team)
	first_match = _get_next_streamer_match(client_id, team_alias1, team_alias2, now)
	if first_match is None:
		# No next match, so return an empty calendar.
		return DisplayedCalendar(None, ())

	# Get the partial list of matches.
	paginator = StreamedMatchesPaginator(
			client_id, None, now, team_alias1, team_alias2)
	matches, prev_time, prev_match_id, next_time, next_match_id = _paginate(
			paginator, prev_time, prev_match_id, next_time, next_match_id, page_limit,
			first_id=first_match.match_id)

	# Return the calendar.
	return DisplayedCalendar(first_match,
			tuple(_get_displayed_match(match, team1, team2, is_streamed)
					for match, team1, team2, is_streamed in matches),
			prev_time,
			prev_match_id,
			next_time,
			next_match_id)


class _Paginator:
	def get_first_id(self):
		query = self._get_id_query()
		order_by_columns = (column.asc() for column in self.get_order_by_columns())
		query = query.order_by(*order_by_columns)
		return self._get_id(query)
	
	def get_last_id(self):
		query = self._get_id_query()
		order_by_columns = (column.desc() for column in self.get_order_by_columns())
		query = query.order_by(*order_by_columns)
		return self._get_id(query)


class _MatchesPaginator(_Paginator):
	def __init__(self, client_id, now):
		self.team_alias1 = sa_orm.aliased(Team)
		self.team_alias2 = sa_orm.aliased(Team)
		self.client_id = client_id
		self.now = now

	def get_pagination_values(self, item):
		match = item[0]
		return (match.time, match.id)

	def has_id(self, queried_id, item):
		match = item[0]
		return (match.id == queried_id)
	

"""A paginator for matches starred by the client.
"""
class StarredMatchesPaginator(_MatchesPaginator):
	def _get_id_query(self):
		cutoff_time = _get_upcoming_matches_cutoff(self.now)
		query = session.query(StarredMatch.match_id)\
				.filter(StarredMatch.user_id == self.client_id)\
				.filter(StarredMatch.time > cutoff_time)
		return query

	def _get_id(self, query):
		starred_match = common_db.optional_one(query)
		return starred_match.match_id if starred_match else None

	def get_partial_list_query(self):
		cutoff_time = _get_upcoming_matches_cutoff(self.now)
		return session\
				.query(StarredMatch.match_id, Match, self.team_alias1, self.team_alias2)\
				.join(Match, StarredMatch.match_id == Match.id)\
				.join(self.team_alias1, Match.team1_id == self.team_alias1.id)\
				.join(self.team_alias2, Match.team2_id == self.team_alias2.id)\
				.filter(StarredMatch.user_id == self.client_id)\
				.filter(StarredMatch.time > cutoff_time)
	
	def get_order_by_columns(self):
		return (StarredMatch.time, StarredMatch.match_id)

	def execute_query(self, matches_query):
		return tuple((match, team1, team2, True)
				for match_id, match, team1, team2 in matches_query)

"""A paginator for all matches.
"""
class AllMatchesPaginator(_MatchesPaginator):
	def _get_id_query(self):
		cutoff_time = _get_upcoming_matches_cutoff(self.now)
		return session.query(Match.id).filter(Match.time > cutoff_time)

	def _get_id(self, query):
		match = common_db.optional_one(query)
		return match.id if match else None

	def get_partial_list_query(self):
		cutoff_time = _get_upcoming_matches_cutoff(self.now)
		if self.client_id:
			query = session.query(Match, self.team_alias1, self.team_alias2, StarredMatch)\
					.join(self.team_alias1, Match.team1_id == self.team_alias1.id)\
					.join(self.team_alias2, Match.team2_id == self.team_alias2.id)\
					.outerjoin(StarredMatch, sa.and_(
						StarredMatch.match_id == Match.id,
						StarredMatch.user_id == self.client_id))
		else:
			query = session.query(Match, self.team_alias1, self.team_alias2)\
					.join(self.team_alias1, Match.team1_id == self.team_alias1.id)\
					.join(self.team_alias2, Match.team2_id == self.team_alias2.id)
		query = query.filter(Match.time > cutoff_time)
		return query

	def get_order_by_columns(self):
		return (Match.time, Match.id)

	def execute_query(self, matches_query):
		if self.client_id:
			return tuple((match, team1, team2, bool(starred_match))
					for match, team1, team2, starred_match in matches_query)
		else:
			return tuple((match, team1, team2, False)
					for match, team1, team2 in matches_query)


class _TeamsPaginator(_Paginator):
	def __init__(self, client_id):
		self.client_id = client_id
	
	def get_pagination_values(self, item):
		team = item[0]
		return (team.indexed_name, team.id)

	def has_id(self, queried_id, item):
		team = item[0] 
		return (team.id == queried_id)

"""A paginator for teams starred by the client.
"""
class StarredTeamsPaginator(_TeamsPaginator):
	def _get_id_query(self):
		query = session.query(StarredTeam.team_id)\
				.filter(StarredTeam.user_id == self.client_id)
		return query

	def _get_id(self, query):
		starred_team = common_db.optional_one(query)
		return starred_team.team_id if starred_team else None

	def get_partial_list_query(self):
		return session.query(StarredTeam.team_id, Team)\
				.join(Team, StarredTeam.team_id == Team.id)\
				.filter(StarredTeam.user_id == self.client_id)

	def get_order_by_columns(self):
		return (StarredTeam.indexed_name, StarredTeam.team_id)

	def execute_query(self, teams_query):
		return tuple((team, True) for team_id, team in teams_query)

"""A paginator for all teams.
"""
class AllTeamsPaginator(_TeamsPaginator):
	def _get_id_query(self):
		return session.query(Team.id)

	def _get_id(self, query):
		team = common_db.optional_one(query)
		return team.id if team else None

	def get_partial_list_query(self):
		if self.client_id:
			query = session.query(Team, StarredTeam)\
					.outerjoin(StarredTeam, sa.and_(
						StarredTeam.team_id == Team.id,
						StarredTeam.user_id == self.client_id))
		else:
			query = session.query(Team)
		return query
	
	def get_order_by_columns(self):
		return (Team.indexed_name, Team.id)

	def execute_query(self, teams_query):
		if self.client_id:
			return tuple((team, bool(starred_team))
					for team, starred_team in teams_query)
		else:
			return tuple((team, False) for team in teams_query)


class _StreamersPaginator(_Paginator):
	def __init__(self, client_id):
		self.client_id = client_id
	
	def get_pagination_values(self, item):
		streamer = item[0]
		return (streamer.indexed_name, streamer.id)
	
	def has_id(self, queried_id, item):
		streamer = item[0]
		return (streamer.id == queried_id)

"""A paginator for streaming users starred by the client.
"""
class StarredStreamersPaginator(_StreamersPaginator):
	def _get_id_query(self):
		query = session.query(StarredStreamer.streamer_id)\
				.filter(StarredStreamer.user_id == self.client_id)
		return query

	def _get_id(self, query):
		starred_streamer = common_db.optional_one(query)
		return starred_streamer.streamer_id if starred_streamer else None

	def get_partial_list_query(self):
		return session.query(StarredStreamer.streamer_id, User)\
				.join(User, StarredStreamer.streamer_id == User.id)\
				.filter(StarredStreamer.user_id == self.client_id)
	
	def get_order_by_columns(self):
		return (StarredStreamer.indexed_name, StarredStreamer.streamer_id)

	def execute_query(self, streamers_query):
		return tuple((streamer, True) for streamer_id, streamer in streamers_query)

"""A paginator for all streaming users.
"""
class AllStreamersPaginator(_StreamersPaginator):
	def _get_id_query(self):
		return session.query(User.id).filter(User.can_stream == True)

	def _get_id(self, query):
		streamer = common_db.optional_one(query)
		return streamer.id if streamer else None

	def get_partial_list_query(self):
		if self.client_id:
			query = session.query(User, StarredStreamer)\
					.outerjoin(StarredStreamer, sa.and_(
						StarredStreamer.streamer_id == User.id,
						StarredStreamer.user_id == self.client_id))
		else:
			query = session.query(User)
		return query.filter(User.can_stream == True)

	def get_order_by_columns(self):
		return (User.indexed_name, User.id)
	
	def execute_query(self, streamers_query):
		if self.client_id:
			return tuple((streamer, bool(starred_streamer))
					for streamer, starred_streamer in streamers_query)
		else:
			return tuple((streamer, False) for streamer in streamers_query)


def _get_match_list(
		prev_time, prev_match_id, next_time, next_match_id, page_limit,
		paginator):
	matches, prev_time, prev_match_id, next_time, next_match_id = _paginate(
			paginator, prev_time, prev_match_id, next_time, next_match_id, page_limit)
	return DisplayedMatchList(
			tuple(_get_displayed_match(match, team1, team2, is_starred)
				for match, team1, team2, is_starred in matches),
			prev_time,
			prev_match_id,
			next_time,
			next_match_id)

@close_session
def get_starred_matches(client_id,
		prev_time=None, prev_match_id=None, next_time=None, next_match_id=None,
		page_limit=None, now=None):
	"""Returns matches starred by the client."""
	now = _get_now(now)
	paginator = StarredMatchesPaginator(client_id, now)
	return _get_match_list(prev_time, prev_match_id, next_time, next_match_id, page_limit,
			paginator)

@close_session
def get_all_matches(client_id,
		prev_time=None, prev_match_id=None, next_time=None, next_match_id=None,
		page_limit=None, now=None):
	"""Returns all matches."""
	now = _get_now(now)
	paginator = AllMatchesPaginator(client_id, now)
	return _get_match_list(prev_time, prev_match_id, next_time, next_match_id, page_limit,
			paginator)


def _get_displayed_team(team, is_starred):
	return DisplayedTeam(team.id, team.display_name, team.num_stars, is_starred,
			team.game, team.division)

def _get_team_list(
		prev_name, prev_team_id, next_name, next_team_id, page_limit,
		paginator):
	teams, prev_name, prev_team_id, next_name, next_team_id = _paginate(
			paginator, prev_name, prev_team_id, next_name, next_team_id, page_limit)
	return DisplayedTeamList(
			tuple(_get_displayed_team(team, is_starred) for team, is_starred in teams),
			prev_name,
			prev_team_id,
			next_name,
			next_team_id)

@close_session
def get_starred_teams(client_id,
		prev_name=None, prev_team_id=None, next_name=None, next_team_id=None,
		page_limit=None):
	"""Returns teams starred by the client."""
	paginator = StarredTeamsPaginator(client_id)
	return _get_team_list(prev_name, prev_team_id, next_name, next_team_id, page_limit,
			paginator)

@close_session
def get_all_teams(client_id,
		prev_name=None, prev_team_id=None, next_name=None, next_team_id=None,
		page_limit=None):
	"""Returns all teams."""
	paginator = AllTeamsPaginator(client_id)
	return _get_team_list(prev_name, prev_team_id, next_name, next_team_id, page_limit,
			paginator)


def _get_displayed_streamer(streamer, is_starred):
	"""Returns a DisplayedStreamer for the given streamer."""
	return DisplayedStreamer(streamer.id,
			streamer.display_name,
			streamer.num_stars,
			is_starred,
			streamer.image_url_small,
			streamer.image_url_large,
			streamer.url_by_id,
			streamer.url_by_name)

def _get_streamer_list(
		prev_name, prev_streamer_id, next_name, next_streamer_id, page_limit,
		paginator):
	streamers, prev_name, prev_streamer_id, next_name, next_streamer_id = _paginate(
			paginator, prev_name, prev_streamer_id, next_name, next_streamer_id, page_limit)
	return DisplayedStreamerList(
			tuple(_get_displayed_streamer(streamer, is_starred)
					for streamer, is_starred in streamers),
			prev_name,
			prev_streamer_id,
			next_name,
			next_streamer_id)

@close_session
def get_starred_streamers(client_id,
		prev_name=None, prev_streamer_id=None, next_name=None, next_streamer_id=None,
		page_limit=None):
	"""Returns streaming users starred by the client."""
	paginator = StarredStreamersPaginator(client_id)
	return _get_streamer_list(
			prev_name, prev_streamer_id, next_name, next_streamer_id, page_limit, paginator)

@close_session
def get_all_streamers(client_id,
		prev_name=None, prev_streamer_id=None, next_name=None, next_streamer_id=None,
		page_limit=None):
	"""Returns all streaming users."""
	paginator = AllStreamersPaginator(client_id)
	return _get_streamer_list(
			prev_name, prev_streamer_id, next_name, next_streamer_id, page_limit,
			paginator)


"""A paginator for streaming users of a match.
"""
class MatchStreamersPaginator(_Paginator):
	def __init__(self, match_id, client_id):
		self.match_id = match_id
		self.client_id = client_id

	def _get_id_query(self):
		query = session.query(StreamedMatch.streamer_id)\
				.filter(StreamedMatch.match_id == self.match_id)
		return query

	def _get_id(self, query):
		streamed_match = common_db.optional_one(query)
		return streamed_match.streamer_id if streamed_match else None

	def get_partial_list_query(self):
		if self.client_id:
			query = session\
					.query(StreamedMatch.streamer_id, StreamedMatch.added, User, StarredStreamer)\
					.join(User, StreamedMatch.streamer_id == User.id)\
					.outerjoin(StarredStreamer, sa.and_(
						StarredStreamer.streamer_id == User.id,
						StarredStreamer.user_id == self.client_id))
		else:
			query = session.query(StreamedMatch.streamer_id, StreamedMatch.added, User)\
					.join(User, StreamedMatch.streamer_id == User.id)
		return query\
				.filter(StreamedMatch.match_id == self.match_id)

	def get_order_by_columns(self):
		return (StreamedMatch.added, StreamedMatch.streamer_id)

	def execute_query(self, streamers_query):
		if self.client_id:
			return tuple((added, streamer, bool(starred_streamer))
					for streamer_id, added, streamer, starred_streamer in streamers_query)
		else:
			return tuple((added, streamer, False)
					for streamer_id, added, streamer in streamers_query)

	def get_pagination_values(self, item):
		added, streamer = item[0], item[1]
		return (added, streamer.id)

	def has_id(self, queried_id, item):
		added, streamer = item[0], item[1]
		return (streamer.id == queried_id)

@close_session
def get_displayed_match(client_id, match_id,
		prev_time=None, prev_streamer_id=None, next_time=None, next_streamer_id=None,
		page_limit=None):
	"""Returns a DisplayedMatch containing streaming users."""
	try:
		# Get the match and teams.
		team_alias1 = sa_orm.aliased(Team)
		team_alias2 = sa_orm.aliased(Team)
		match, team1, team2, starred_match = session\
				.query(Match, team_alias1, team_alias2, StarredMatch)\
				.join(team_alias1, Match.team1_id == team_alias1.id)\
				.join(team_alias2, Match.team2_id == team_alias2.id)\
				.outerjoin(StarredMatch, sa.and_(
					StarredMatch.match_id == match_id,
					StarredMatch.user_id == client_id))\
				.filter(Match.id == match_id)\
				.one()
		displayed_team1 = _get_displayed_match_team(team1)
		displayed_team2 = _get_displayed_match_team(team2)
	except sa_orm.exc.NoResultFound:
		session.rollback()
		raise common_db.DbException._chain()
	is_starred = (starred_match is not None)
	
	# Get the partial list of streamers for this match.
	if match.num_streams:
		paginator = MatchStreamersPaginator(match_id, client_id)
		streamers, prev_time, prev_streamer_id, next_time, next_streamer_id = _paginate(
				paginator, prev_time, prev_streamer_id, next_time, next_streamer_id, page_limit)
	else:
		streamers = ()
		prev_time = None
		prev_streamer_id = None
		next_time = None
		next_streamer_id = None

	# Return the displayed match.
	return DisplayedMatchDetails(match_id,
			displayed_team1,
			displayed_team2,
			match.time,
			match.num_stars,
			match.num_streams,
			is_starred,
			match.game,
			match.division,
			match.fingerprint,
			tuple(_get_displayed_streamer(streamer, is_starred)
					for added, streamer, is_starred in streamers),
			prev_time,
			prev_streamer_id,
			next_time,
			next_streamer_id)


def _get_displayed_team_match(match, team_id, opponent_team, is_starred):
	opponent_team = DisplayedTeam(
			opponent_team.id, opponent_team.display_name, opponent_team.num_stars, False)
	if match.team1_id == team_id:
		team1 = None
		team2 = opponent_team
	else:
		team1 = opponent_team
		team2 = None
	return DisplayedMatch(match.id,
			team1,
			team2,
			match.time,
			match.num_stars,
			match.num_streams,
			is_starred)

"""A paginator for opponents of a team.
"""
class MatchOpponentsPaginator(_Paginator):
	def __init__(self, team_id, client_id, now):
		self.team_id = team_id
		self.client_id = client_id
		self.now = now

	def _get_id_query(self):
		cutoff_time = _get_upcoming_matches_cutoff(self.now)
		query = session.query(MatchOpponent.match_id)\
				.filter(MatchOpponent.team_id == self.team_id)\
				.filter(MatchOpponent.time > cutoff_time)
		return query

	def _get_id(self, query):
		first_match_opponent = common_db.optional_one(query)
		return first_match_opponent.match_id if first_match_opponent else None

	def get_partial_list_query(self):
		if self.client_id:
			query = session\
					.query(MatchOpponent.match_id, MatchOpponent.team_id, Match, Team, StarredMatch)\
					.outerjoin(StarredMatch, sa.and_(
						StarredMatch.match_id == MatchOpponent.match_id,
						StarredMatch.user_id == self.client_id))
		else:
			query = session\
					.query(MatchOpponent.match_id, MatchOpponent.team_id, Match, Team)
		cutoff_time = _get_upcoming_matches_cutoff(self.now)
		return query\
				.join(Match, MatchOpponent.match_id == Match.id)\
				.join(Team, MatchOpponent.opponent_id == Team.id)\
				.filter(MatchOpponent.team_id == self.team_id)\
				.filter(MatchOpponent.time > cutoff_time)

	def get_order_by_columns(self):
		return (MatchOpponent.time, MatchOpponent.match_id)

	def execute_query(self, matches_query):
		if self.client_id:
			# Convert any found StarredMatch to an is_starred value of True.
			return tuple((match, opponent_team, bool(starred_match))
					for match_id, team_id, match, opponent_team, starred_match
						in matches_query)
		else:
			return tuple((match, opponent_team, False)
					for match_id, team_id, match, opponent_team in matches_query)

	def get_pagination_values(self, item):
		match = item[0]
		return (match.time, match.id)

	def has_id(self, queried_id, item):
		match = item[0]
		return (match.id == queried_id)

@close_session
def get_displayed_team(client_id, team_id,
		prev_time=None, prev_match_id=None, next_time=None, next_match_id=None,
		page_limit=None, now=None):
	"""Returns a DisplayedTeam containing scheduled matches."""
	try:
		# Get the team.
		team, starred_team = session.query(Team, StarredTeam)\
				.outerjoin(StarredTeam, sa.and_(
					StarredTeam.team_id == team_id,
					StarredTeam.user_id == client_id))\
				.filter(Team.id == team_id)\
				.one()
	except sa_orm.exc.NoResultFound:
		session.rollback()
		raise common_db.DbException._chain()
	is_starred = (starred_team is not None)

	# Get the partial list of matches for this team.
	now = _get_now(now)
	paginator = MatchOpponentsPaginator(team_id, client_id, now)
	matches, prev_time, prev_match_id, next_time, next_match_id = _paginate(
			paginator, prev_time, prev_match_id, next_time, next_match_id, page_limit)
	
	# Return the displayed team.
	return DisplayedTeamDetails(team_id,
			team.display_name,
			team.num_stars,
			is_starred,
			team.game,
			team.division,
			team.fingerprint,
			tuple(_get_displayed_team_match(match, team_id, opponent_team, is_starred)
					for match, opponent_team, is_starred in matches),
			prev_time,
			prev_match_id,
			next_time,
			next_match_id)


"""A paginator for matches streamed by a user.
"""
class StreamedMatchesPaginator(_Paginator):
	def __init__(self, streamer_id, client_id, now,
			team_alias1=None, team_alias2=None):
		self.streamer_id = streamer_id
		self.client_id = client_id
		self.team_alias1 = team_alias1 if team_alias1 else sa_orm.aliased(Team)
		self.team_alias2 = team_alias2 if team_alias2 else sa_orm.aliased(Team)
		self.now = now

	def _get_id_query(self):
		cutoff_time = _get_upcoming_matches_cutoff(self.now)
		query = session.query(StreamedMatch.match_id)\
				.filter(StreamedMatch.streamer_id == self.streamer_id)\
				.filter(StreamedMatch.time > cutoff_time)
		return query
	
	def _get_id(self, query):
		first_streamed_match = common_db.optional_one(query)
		return first_streamed_match.match_id if first_streamed_match else None

	def get_partial_list_query(self):
		return _get_streamed_match_query(self.streamer_id,
				self.client_id,
				self.team_alias1,
				self.team_alias2,
				self.now)

	def get_order_by_columns(self):
		return (StreamedMatch.time, StreamedMatch.match_id)

	def execute_query(self, matches_query):
		if self.client_id:
			return tuple((match, team1, team2, bool(starred_match))
					for match_id, match, team1, team2, starred_match in matches_query)
		else:
			return tuple((match, team1, team2, False)
					for match_id, match, team1, team2 in matches_query)

	def get_pagination_values(self, item):
		match = item[0]
		return (match.time, match.id)

	def has_id(self, queried_id, item):
		match = item[0]
		return (match.id == queried_id)


@close_session
def _get_displayed_streamer_by_filter(client_id, filter_adder,
		prev_time, prev_match_id, next_time, next_match_id, page_limit, now):
	try:
		# Get the streamer.
		query = session.query(User, StarredStreamer)\
				.outerjoin(StarredStreamer, sa.and_(
					StarredStreamer.streamer_id == User.id,
					StarredStreamer.user_id == client_id))
		query = filter_adder(query)
		streamer, starred_streamer = query.one()
	except sa_orm.exc.NoResultFound:
		session.rollback()
		raise common_db.DbException._chain()
	is_starred = (starred_streamer is not None)

	# Get the partial list of matches streamed by this user.
	now = _get_now(now)
	paginator = StreamedMatchesPaginator(streamer.id, client_id, now)
	matches, prev_time, prev_match_id, next_time, next_match_id = _paginate(
			paginator, prev_time, prev_match_id, next_time, next_match_id, page_limit)
	
	# Return the displayed streaming user.
	return DisplayedStreamerDetails(streamer.id,
			streamer.display_name,
			streamer.num_stars,
			is_starred,
			streamer.image_url_small,
			streamer.image_url_large,
			streamer.url_by_id,
			streamer.url_by_name,
			tuple(_get_displayed_match(match, team1, team2, is_starred)
					for match, team1, team2, is_starred in matches),
			prev_time,
			prev_match_id,
			next_time,
			next_match_id)

def get_displayed_streamer(client_id, streamer_id,
		prev_time=None, prev_match_id=None, next_time=None, next_match_id=None,
		page_limit=None, now=None):
	"""Returns a DisplayedStreamer containing scheduled streamed matches.
	
	The returned streaming user is found by its identifier.
	"""
	def _filter_adder(query):
		return query.filter(User.id == streamer_id)
	return _get_displayed_streamer_by_filter(client_id, _filter_adder,
			prev_time, prev_match_id, next_time, next_match_id, page_limit, now)

def get_displayed_streamer_by_twitch_id(client_id, twitch_id,
		prev_time=None, prev_match_id=None, next_time=None, next_match_id=None,
		page_limit=None, now=None):
	"""Returns a DisplayedStreamer containing scheduled streamed matches.
	
	The returned streaming user is found by its Twitch identifier.
	"""
	url_by_id = common_db._get_twitch_url_by_id(twitch_id)
	def _filter_adder(query):
		return query.filter(User.url_by_id == url_by_id)
	return _get_displayed_streamer_by_filter(client_id, _filter_adder,
			prev_time, prev_match_id, next_time, next_match_id, page_limit, now)

def get_displayed_streamer_by_twitch_name(client_id, twitch_name,
		prev_time=None, prev_match_id=None, next_time=None, next_match_id=None,
		page_limit=None, now=None):
	"""Returns a DisplayedStreamer containing scheduled streamed matches.
	
	The returned streaming user is found by its Twitch username.
	"""
	url_by_name = common_db._get_twitch_url_by_name(twitch_name)
	def _filter_adder(query):
		return query.filter(User.url_by_name == url_by_name)
	return _get_displayed_streamer_by_filter(client_id, _filter_adder,
			prev_time, prev_match_id, next_time, next_match_id, page_limit, now)


def twitch_user_logged_in(twitch_id, name, display_name, indexed_name, logo,
		now=None):
	user_class_extra_kwargs = {'can_stream': True}
	return common_db.twitch_user_logged_in(
			User, Users, twitch_id, name, display_name, indexed_name, logo,
			user_class_extra_kwargs=user_class_extra_kwargs, now=now)

def steam_user_logged_in(
		steam_id, personaname, indexed_name, profile_url, avatar, avatar_full,
		now=None):
	return common_db.steam_user_logged_in(
			User, Users, steam_id, personaname, indexed_name, profile_url, avatar, avatar_full,
			now=now)

