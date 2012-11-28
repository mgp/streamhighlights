from datetime import datetime
import re
import sqlalchemy as sa
import sqlalchemy.engine as sa_engine
import sqlalchemy.ext.declarative as sa_ext_declarative
import sqlalchemy.orm as sa_orm
import sqlalchemy.schema as sa_schema
import sys

import common_db
from common_db import _get_now, session

"""A user of the site.
"""
class User(common_db.UserMixin, common_db._Base):
	__tablename__ = 'Users'

	num_stars = sa.Column(sa.Integer, default=0, nullable=False)
	can_stream = sa.Column(sa.Boolean, default=False, nullable=False)
	stream_info = sa.Column(sa.String)

	def __repr__(self):
		return 'User(id=%r, name=%r, image_url_small=%r, image_url_large=%r, created=%r, last_seen=%r, url_by_id=%r, url_by_name=%r, num_stars=%r, can_stream=%r, stream_info=%r, steam_user=%r, twitch_user=%r)' % (
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
				self.stream_info,
				self.steam_user,
				self.twitch_user)


"""A team in a match.
"""
class Team(common_db._Base):
	__tablename__ = 'Teams'

	id = sa.Column(sa.Integer, primary_key=True)
	name = sa.Column(sa.String, nullable=False)
	game = sa.Column(sa.String, nullable=False)
	league = sa.Column(sa.String, nullable=False)
	num_stars = sa.Column(sa.Integer, default=0, nullable=False)
	url = sa.Column(sa.String, nullable=False)
	fingerprint = sa.Column(sa.String, nullable=False)

	def __repr__(self):
		print 'Team(id=%r, name=%r, game=%r, league=%r, num_stars=%r, url=%r, fingerprint=%r)' % (
				self.id,
				self.name,
				self.game,
				self.league,
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
	league = sa.Column(sa.String, nullable=False)
	num_stars = sa.Column(sa.Integer, default=0, nullable=False)
	num_streams = sa.Column(sa.Integer, default=0, nullable=False)
	is_streamed = sa.Column(sa.Boolean, default=False, nullable=False)
	url = sa.Column(sa.String, nullable=False)
	fingerprint = sa.Column(sa.String, nullable=False)

	def __repr__(self):
		print 'Match(id=%r, team1_id=%r, team2_id=%r, time=%r, game=%r, league=%r, num_stars=%r, num_streams=%r, is_streamed=%r, url=%r, fingerprint=%r)' % (
				self.id,
				self.team1_id,
				self.team2_id,
				self.time,
				self.game,
				self.league,
				self.num_stars,
				self.num_streams,
				self.is_streamed,
				self.url,
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
	action = sa.Column(sa.Enum('edit_time', 'cancel'), nullable=False)
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
	added = sa.Column(sa.DateTime, nullable=False)

	def __repr__(self):
		return 'StarredMatch(user_id=%r, match_id=%r, added=%r)' % (
				self.user_id,
				self.match_id,
				self.added)


"""The association from users to their starred teams.
"""
class StarredTeam(common_db._Base):
	__tablename__ = 'StarredTeams'

	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'), primary_key=True)
	team_id = sa.Column(sa.Integer, sa.ForeignKey('Teams.id'), primary_key=True)
	added = sa.Column(sa.DateTime, nullable=False)

	def __repr__(self):
		return 'StarredTeam(user_id=%r, team_id=%r, added=%r)' % (
				self.user_id,
				self.team_id,
				self.added)


"""The association from users to their starred streaming users.
"""
class StarredStreamer(common_db._Base):
	__tablename__ = 'StarredStreamers'

	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'), primary_key=True)
	streamer_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'), primary_key=True)
	added = sa.Column(sa.DateTime, nullable=False)

	def __repr__(self):
		return 'StarredStreamer(user_id=%r, streamer_id=%r, added=%r)' % (
				self.user_id,
				self.streamer_id,
				self.added)


"""The association from streaming users to their streamed matches.
"""
class StreamedMatch(common_db._Base):
	__tablename__ = 'StreamedMatches'

	streamer_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'), primary_key=True)
	match_id = sa.Column(sa.Integer, sa.ForeignKey('Matches.id'), primary_key=True)
	added = sa.Column(sa.DateTime, nullable=False)
	comment = sa.Column(sa.String)

	def __repr__(self):
		return 'StreamedMatch(streamer_id=%r, match_id=%r, added=%r, comment=%r)' % (
				self.streamer_id,
				self.match_id,
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
# Used by method _get_displayed_match.
sa_schema.Index('StreamedMatchesByMatchId', StreamedMatch.match_id)
# Used by method get_displayed_calendar.
sa_schema.Index('CalendarEntriesByUserIdAndTimeAndMatchId',
		CalendarEntry.user_id.asc(), CalendarEntry.time.asc(), CalendarEntry.match_id.asc())


def create_all():
	common_db.create_all()

	global Users
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


"""Adds a match between two teams at a given time.
"""
def add_match(team1_id, team2_id, time, game, league, url, fingerprint, now=None):
	try:
		match_id = session.query(Match)\
				.filter(Match.fingerprint == fingerprint)\
				.one()\
				.id
		session.close()
		return match_id
	except sa_orm.exc.NoResultFound:
		# This match does not exist; continue to add the match.
		session.rollback()

	try:
		# Add the match.
		match = Match(team1_id=team1_id, team2_id=team2_id, game=game, league=league, time=time,
				url=url, fingerprint=fingerprint)
		session.add(match)
		session.flush()

		# Add each opponent for the match.
		match_opponent1 = MatchOpponent(
				team_id=team1_id, match_id=match.id, time=time, opponent_id=team2_id)
		match_opponent2 = MatchOpponent(
				team_id=team2_id, match_id=match.id, time=time, opponent_id=team1_id)
		session.add(match_opponent1)
		session.add(match_opponent2)
		session.commit()

		return match.id
	except sa.exc.IntegrityError:
		# The commit failed because teams with the given identifiers are missing.
		session.rollback()
		raise common_db.DbException._chain()

"""Adds a team in the given game and league.
"""
def add_team(name, game, league, url, fingerprint, now=None):
	try:
		team = session.query(Team).filter(Team.fingerprint == fingerprint).one()
		team.name = name
	except sa_orm.exc.NoResultFound:
		team = Team(name=name, game=game, league=league, url=url, fingerprint=fingerprint)
		session.add(team)

	session.commit()
	return team.id


"""Adds a star by the client for the match with the given identifier.
"""
def add_star_match(client_id, match_id, now=None):
	now = _get_now(now)

	try:
		# Add the client's star for the match.
		starred_match = StarredMatch(user_id=client_id,
				match_id=match_id,
				added=now)
		session.add(starred_match)
		session.flush()
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

"""Removes a star by the client for the match with the given identifier.
"""
def remove_star_match(client_id, match_id, now=None):
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


"""Adds a star by the client for the team with the given identifier.
"""
def add_star_team(client_id, team_id, now=None):
	now = _get_now(now)

	try:
		# Add the client's star for the team.
		starred_team = StarredTeam(user_id=client_id,
				team_id=team_id,
				added=now)
		session.add(starred_team)
		session.flush()
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


"""Removes a star by the client for the team with the given identifier.
"""
def remove_star_team(client_id, team_id, now=None):
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


"""Adds a star by the client for the streaming user with the given identifier.
"""
def add_star_streamer(client_id, streamer_id, now=None):
	now = _get_now(now)

	try:
		# Add the client's star for the streaming user.
		starred_streamer = StarredStreamer(user_id=client_id,
				streamer_id=streamer_id,
				added=now)
		session.add(starred_streamer)
		session.flush()
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

"""Removes a star by the client for the streaming user with the given identifier.
"""
def remove_star_streamer(client_id, streamer_id, now=None):
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

"""Adds a stream by the client for the match with the given identifier.
"""
def add_stream_match(client_id, match_id, comment=None, now=None):
	now = _get_now(now)

	try:
		# Add the client as a user streaming the match.
		streamed_match = StreamedMatch(streamer_id=client_id,
				match_id=match_id,
				added=now,
				comment=comment)
		session.add(streamed_match)
		session.flush()
	except sa.exc.IntegrityError:
		# The flush failed because the client is already streaming this match.
		session.rollback()
		raise common_db.DbException._chain()

	match = session.query(Match).filter(Match.id == match_id).one()
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

"""Removes a stream by the client for the match with the given identifier.
"""
def remove_stream_match(client_id, match_id, now=None):
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


"""Returns a CalendarEntry created with the given user identifier and match.
"""
def _get_calendar_entry(user_id, match):
	return CalendarEntry(user_id=user_id,
			match_id=match.id,
			time=match.time,
			num_user_stars=1)


def _multi_increment_num_user_stars(user_ids, match, now):
	for user_id in user_ids:
		_increment_num_user_stars(user_id, match, now)

"""Updates or creates a CalendarEntry for the given user identifier and match.
"""
def _increment_num_user_stars(user_id, match, now):
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

"""Updates or deletes a CalendarEntry for the given user and match identifier.
"""
def _decrement_num_user_stars(user_id, match_id, now):
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


"""Updates or creates CalendarEntries for users, given that the client was
added as the first streaming user.
"""
def _add_first_stream_calendar_entries(client_id, match, now):
	# Add a CalendarEntry for each user who starred the match.
	user_ids_cursor = session.query(StarredMatch.user_id)\
			.filter(StarredMatch.match_id == match.id)
	for row in user_ids_cursor:
		entry = _get_calendar_entry(row.user_id, match)
		session.add(entry)

	# Add a CalendarEntry for each user who starred either team.
	user_ids_cursor = session.query(MatchOpponent.match_id, StarredTeam.user_id)\
			.join(StarredTeam, MatchOpponent.team_id == StarredTeam.team_id)\
			.filter(MatchOpponent.match_id == match.id)
	user_ids_cursor = (row.user_id for row in user_ids_cursor)
	_multi_increment_num_user_stars(user_ids_cursor, match, now)

	# Add a CalendarEntry for each user who starred the streaming user.
	user_ids_cursor = session.query(StarredStreamer.user_id)\
			.filter(StarredStreamer.streamer_id == client_id)
	user_ids_cursor = (row.user_id for row in user_ids_cursor)
	_multi_increment_num_user_stars(user_ids_cursor, match, now)

"""Updates or creates CalendarEntries for users, given that the client was
added as a streamer, but not the first one.
"""
def _add_not_first_stream_calendar_entries(client_id, match, now):
	# If needed, add a CalendarEntry for each user who starred the streaming user.
	user_ids_cursor = session.query(StarredStreamer.user_id)\
			.filter(StarredStreamer.streamer_id == client_id)
	user_ids_cursor = (row.user_id for row in user_ids_cursor)
	_multi_increment_num_user_stars(user_ids_cursor, match, now)


"""Updates or deletes CalendarEntries for users, given that the client was
removed as a streamer, but not the last one.
"""
def _remove_not_last_stream_calendar_entries(client_id, match_id, now):
	# If needed, remove a CalendarEntry for each user who starred the streaming user.
	user_ids_cursor = session.query(StarredStreamer.user_id)\
			.filter(StarredStreamer.streamer_id == client_id)
	user_ids_cursor = (row.user_id for row in user_ids_cursor)
	_multi_decrement_num_user_stars(user_ids_cursor, match_id, now)

"""Updates or deletes CalendarEntries for users, given that the client was
removed as the last streaming user.
"""
def _remove_last_stream_calendar_entries(client_id, match_id, now):	
	# Remove every CalendarEntry for this match.
	result = session.execute(
			CalendarEntries.delete().where(CalendarEntry.match_id == match_id))


"""A match in a DisplayedCalendar.
"""
class DisplayedCalendarMatch:
	def __init__(self, match_id, team1_id, team1_name, team2_id, team2_name,
			time, game, league, num_stars, num_streams):
		self.match_id = match_id
		self.team1_id = team1_id
		self.team1_name = team1_name
		self.team2_id = team2_id
		self.team2_name = team2_name
		self.time = time
		self.game = game
		self.league = league
		self.num_stars = num_stars
		self.num_streams = num_streams

	def __repr__(self):
		return 'DisplayedCalendarMatch(match_id=%r, team1_id=%r, team1_name=%r, team2_id=%r, team2_name=%r, time=%r, game=%r, league=%r, num_stars=%r, num_streams=%r)' % (
				self.match_id,
				self.team1_id,
				self.team1_name,
				self.team2_id,
				self.team2_name,
				self.time,
				self.game,
				self.league,
				self.num_stars,
				self.num_streams)

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


"""A team in a DisplayedMatch.
"""
class DisplayedMatchTeam:
	def __init__(self, team_id, name, num_stars):
		self.team_id = team_id
		self.name = name
		self.num_stars = num_stars

	def __repr__(self):
		return 'DisplayedMatchTeam(team_id=%r, name=%r, num_stars=%r)' % (
				self.team_id,
				self.name,
				self.num_stars)

"""A streaming user for a DisplayedMatch.
"""
class DisplayedMatchStreamer:
	def __init__(self, user_id, name, num_stars, image_url, url_by_id, url_by_name):
		self.user_id = user_id
		self.name = name
		self.num_stars = num_stars
		self.image_url = image_url
		self.url_by_id = url_by_id
		self.url_by_name = url_by_name

	def __repr__(self):
		return 'DisplayedMatchStreamer(user_id=%r, name=%r, num_stars=%r, image_url=%r, url_by_id=%r, url_by_name=%r)' % (
				self.user_id,
				self.name,
				self.num_stars,
				self.image_url,
				self.url_by_id,
				self.url_by_name)

"""A detailed view of a match.
"""
class DisplayedMatch:
	def __init__(self, match_id, team1, team2, time, game, league, is_starred, num_stars, streamers, prev_time, prev_streamer_id, next_time, next_streamer_id):
		self.match_id = match_id
		self.team1 = team1
		self.team2 = team2
		self.time = time
		self.game = game
		self.league = league
		self.is_starred = is_starred
		self.num_stars = num_stars
		self.streamers = streamers
		self.prev_time = prev_time
		self.prev_streamer_id = prev_streamer_id
		self.next_time = next_time
		self.next_streamer_id = next_streamer_id
	
	def __repr__(self):
		return 'DisplayedMatch(match_id=%r, team1=%r, team2=%r, time=%r, game=%r, league=%r, is_starred=%r, num_stars=%r, streamers=%r, prev_time=%r, prev_streamer_id=%r, next_time=%r, next_streamer_id=%r)' % (
				self.match_id,
				self.team1,
				self.team2,
				self.time,
				self.game,
				self.league,
				self.is_starred,
				self.num_stars,
				self.streamers,
				self.prev_time,
				self.prev_streamer_id,
				self.next_time,
				self.next_streamer_id)


"""A match for a DisplayedTeam.
"""
class DisplayedTeamMatch:
	def __init__(self, opponent_id, opponent_name, match_id, time, num_stars, num_streams):
		self.opponent_id = opponent_id
		self.opponent_name = opponent_name
		self.match_id = match_id
		self.time = time
		self.num_stars = num_stars
		self.num_streams = num_streams
	
	def __repr__(self):
		return 'DisplayedTeamMatch(opponent_id=%r, opponent_name=%r, match_id=%r, time=%r, num_stars=%r, num_streams=%r)' % (
				self.opponent_id,
				self.opponent_name,
				self.match_id,
				self.time,
				self.num_stars,
				self.num_streams)

"""A detailed view of a team.
"""
class DisplayedTeam:
	def __init__(self, team_id, name, game, league, is_starred, num_stars, matches, prev_key, next_key):
		self.team_id = team_id
		self.name = name
		self.game = game
		self.league = league
		self.is_starred = is_starred
		self.num_stars = num_stars
		self.matches = matches
		self.prev_key = prev_key
		self.next_key = next_key

	def __repr__(self):
		return 'DisplayedTeam(team_id=%r, name=%r, game=%r, league=%r, is_starred=%r, num_stars=%r, matches=%r, prev_key=%r, next_key=%r)' % (
				self.team_id,
				self.name,
				self.game,
				self.league,
				self.is_starred,
				self.num_stars,
				self.matches,
				self.prev_key,
				self.next_key)


"""A match for a DisplayedStreamer.
"""
class DisplayedStreamerMatch:
	def __init__(self, match_id, team1_id, team1_name, team2_id, team2_name,
			time, game, league, num_stars, num_streams):
		self.match_id = match_id
		self.team1_id = team1_id
		self.team1_name = team1_name
		self.team2_id = team2_id
		self.team2_name = team2_name
		self.time = time
		self.game = game
		self.league = league
		self.num_stars = num_stars
		self.num_streams = num_streams
	
	def __repr__(self):
		return 'DisplayedStreamerMatch(match_id=%r, team1_id=%r, team1_name=%r, team2_id=%r, team2_name=%r, time=%r, game=%r, league=%r, num_stars=%r, num_streams=%r)' % (
				self.match_id,
				self.team1_id,
				self.team1_name,
				self.team2_id,
				self.team2_name,
				self.time,
				self.game,
				self.league,
				self.num_stars,
				self.num_streams)

"""A detailed view of a streamer.
"""
class DisplayedStreamer:
	def __init__(self, streamer_id, name, is_starred, num_stars, matches, prev_key, next_key):
		self.streamer_id = streamer_id
		self.name = name
		self.is_starred = is_starred
		self.num_stars = num_stars
		self.matches = matches
		self.prev_key = prev_key
		self.next_key = next_key

	def __repr__(self):
		return 'DisplayedStreamer(streamer_id=%r, name=%r, is_starred=%r, num_stars=%r, matches=%r, prev_key=%r, next_key=%r)' % (
				self.streamer_id,
				self.name,
				self.is_starred,
				self.num_stars,
				self.matches,
				self.prev_key,
				self.next_key)


# The number of entities per page.
_PAGE_LIMIT = 30

"""Returns whether the user clicked Previous.
"""
def _clicked_prev(prev_time, prev_id):
	return (prev_time and prev_id)

"""Returns whether the user clicked Next.
"""
def _clicked_next(next_time, next_id):
	return (next_time and next_id)

"""Returns a query that adds pagination to the given query.
"""
def _add_pagination_to_query(query, time_column, id_column, page_limit,
		clicked_prev, clicked_next, prev_time, prev_id, next_time, next_id):
	if clicked_prev:
		query = query\
				.filter(sa.or_(
					sa.and_(time_column == prev_time, id_column < prev_id),
					time_column < prev_time))\
				.order_by(time_column.desc(), id_column.desc())
	elif clicked_next:
		query = query\
				.filter(sa.or_(
					sa.and_(time_column == next_time, id_column > next_id),
					time_column > next_time))\
				.order_by(time_column.asc(), id_column.asc())
		pass
	else:
		# Show the first page.
		query = query.order_by(time_column.asc(), id_column.asc())

	return query.limit(page_limit)

def _get_next_pagination(last_item, time_getter, id_getter):
	return time_getter(last_item), id_getter(last_item)

def _get_prev_pagination(first_item, time_getter, id_getter):
	return time_getter(first_item), id_getter(first_item)

"""Returns the pagination query parameters from the given partial list of items.
"""
def _get_adjacent_pagination(
		clicked_prev, clicked_next, items, time_getter, id_getter, first_id,
		page_limit):
	prev_time = None
	prev_id = None
	next_time = None
	next_id = None

	# No pagination for an empty list.
	if items:
		first_item = items[0]
		last_item = items[-1]
		if not clicked_prev and not clicked_next:
			if len(items) == page_limit:
				next_time, next_id = _get_next_pagination(last_item, time_getter, id_getter)
		elif clicked_prev:
			if (len(items) == page_limit) and (id_getter(first_item) != first_id):
				prev_time, prev_id = _get_prev_pagination(first_item, time_getter, id_getter)
			# Came from the following page, so display a Next link.
			next_time, next_id = _get_next_pagination(last_item, time_getter, id_getter)
		elif clicked_next:
			if len(items) == page_limit:
				next_time, next_id = _get_next_pagination(last_item, time_getter, id_getter)
			# Came from the previous page, so display a Previous link.
			prev_time, prev_id = _get_prev_pagination(first_item, time_getter, id_getter)

	return (prev_time, prev_id, next_time, next_id)


def _get_displayed_calendar_match(match, team1, team2):
	return DisplayedCalendarMatch(match.id,
			team1.id,
			team1.name,
			team2.id,
			team2.name,
			match.time,
			match.game,
			match.league,
			match.num_stars,
			match.num_streams)

def _get_next_match(client_id, team_alias1, team_alias2):
	try:
		next_match_id, next_match, next_match_team1, next_match_team2 = session\
				.query(CalendarEntry.match_id, Match, team_alias1, team_alias2)\
				.join(Match, CalendarEntry.match_id == Match.id)\
				.join(team_alias1, Match.team1_id == team_alias1.id)\
				.join(team_alias2, Match.team2_id == team_alias2.id)\
				.filter(CalendarEntry.user_id == client_id)\
				.order_by(CalendarEntry.time.asc())\
				.limit(1)\
				.one()
		next_match = _get_displayed_calendar_match(
				next_match, next_match_team1, next_match_team2)
		return next_match
	except sa_orm.exc.NoResultFound:
		# There are no matches.
		session.close()
	return None

"""Returns a DisplayedCalendar containing calendar entries for the given user.
"""
def get_displayed_calendar(client_id,
		prev_time=None, prev_match_id=None, next_time=None, next_match_id=None,
		page_limit=None):
	if page_limit is None:
		page_limit = _PAGE_LIMIT
	team_alias1 = sa_orm.aliased(Team)
	team_alias2 = sa_orm.aliased(Team)

	# Get the next match.
	next_match = _get_next_match(client_id, team_alias1, team_alias2)
	if next_match is None:
		return DisplayedCalendar(None, ())
	matches_query = session\
			.query(CalendarEntry.match_id, Match, team_alias1, team_alias2)\
			.join(Match, CalendarEntry.match_id == Match.id)\
			.join(team_alias1, Match.team1_id == team_alias1.id)\
			.join(team_alias2, Match.team2_id == team_alias2.id)\
			.filter(CalendarEntry.user_id == client_id)

	clicked_prev = (prev_time and prev_match_id)
	if clicked_prev:
		# The user clicked on Previous.
		matches_query = matches_query\
				.filter(sa.or_(
					sa.and_(
						CalendarEntry.time == prev_time,
						CalendarEntry.match_id < prev_match_id),
					CalendarEntry.time < prev_time))\
				.order_by(CalendarEntry.time.desc(), CalendarEntry.match_id.desc())
	elif next_time and next_match_id:
		# The user clicked on Next.
		matches_query = matches_query\
				.filter(sa.or_(
					sa.and_(
						CalendarEntry.time == next_time,
						CalendarEntry.match_id > next_match_id),
					CalendarEntry.time > next_time))\
				.order_by(CalendarEntry.time.asc(), CalendarEntry.match_id.asc())
	else:
		# Show the first page.
		matches_query = matches_query\
				.order_by(CalendarEntry.time.asc(), CalendarEntry.match_id.asc())

	matches_query = matches_query.limit(page_limit)
	matches = tuple(
			_get_displayed_calendar_match(match, team1, team2)
				for match_id, match, team1, team2 in matches_query)
	session.close()

	if clicked_prev:
		matches = tuple(reversed(matches))

	# Get the pagination values for the previous page.
	on_first_page = (next_match.match_id == matches[0].match_id)
	if not on_first_page:
		prev_time = matches[0].time
		prev_match_id = matches[0].match_id
	else:
		prev_time = None
		prev_match_id = None
	# Get the pagination values for the next page.
	on_last_page = (len(matches) < page_limit)
	if not on_last_page:
		next_time = matches[-1].time
		next_match_id = matches[-1].match_id
	else:
		next_time = None
		next_match_id = None
	
	return DisplayedCalendar(next_match, matches,
			prev_time, prev_match_id, next_time, next_match_id)


def _get_displayed_match_team(team):
	return DisplayedMatchTeam(team.id,
			team.name,
			team.num_stars)

def _get_displayed_match_streamer(streamer):
	return DisplayedMatchStreamer(streamer.id,
			streamer.name,
			streamer.num_stars,
			streamer.image_url_small,
			streamer.url_by_id,
			streamer.url_by_name)

def _streamed_match_time_getter(item):
	added, user = item
	return added

def _streamed_match_id_getter(item):
	added, user = item
	return user.id

"""Returns a DisplayedMatch containing streaming users.
"""
def get_displayed_match(client_id, match_id,
		prev_time=None, prev_streamer_id=None, next_time=None, next_streamer_id=None,
		page_limit=None):
	if page_limit is None:
		page_limit = _PAGE_LIMIT
	clicked_prev = _clicked_prev(prev_time, prev_streamer_id)
	clicked_next = _clicked_next(next_time, next_streamer_id)

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
	is_starred = (starred_match is not None)
	
	streamers = ()
	first_streamer_id = None
	if match.num_streams:
		first_streamer_id = session.query(StreamedMatch.streamer_id)\
				.filter(StreamedMatch.match_id == match_id)\
				.order_by(StreamedMatch.added.asc(), StreamedMatch.streamer_id.asc())\
				.limit(1)\
				.one()\
				.streamer_id

		# Get the partial list of streamers.
		streamers_query = session\
				.query(StreamedMatch.streamer_id, StreamedMatch.added, User)\
				.join(User, StreamedMatch.streamer_id == User.id)\
				.filter(StreamedMatch.match_id == match_id)
		streamers_query = _add_pagination_to_query(
				streamers_query, StreamedMatch.added, StreamedMatch.streamer_id, page_limit,
				clicked_prev, clicked_next,
				prev_time, prev_streamer_id, next_time, next_streamer_id)
		streamers = tuple(
				(added, streamer) for streamer_id, added, streamer in streamers_query)
		if clicked_prev:
			# Reverse the partial list if clicked on Previous.
			streamers = streamers[::-1]

	session.close()

	# Get pagination for the adjacent partial lists.
	prev_time, prev_streamer_id, next_time, next_streamer_id = _get_adjacent_pagination(
			clicked_prev, clicked_next, streamers,
			_streamed_match_time_getter, _streamed_match_id_getter, first_streamer_id,
			page_limit)
	# Return the displayed match.
	return DisplayedMatch(match_id,
			displayed_team1,
			displayed_team2,
			match.time,
			match.game,
			match.league,
			is_starred,
			match.num_stars,
			tuple(_get_displayed_match_streamer(streamer) for added, streamer in streamers),
			prev_time,
			prev_streamer_id,
			next_time,
			next_streamer_id)


def _get_displayed_team_match(match, opponent_team):
	return DisplayedTeamMatch(opponent_team.id,
			opponent_team.name,
			match.id,
			match.time,
			match.num_stars,
			match.num_streams)

"""Returns a DisplayedTeam containing scheduled matches.
"""
def get_displayed_team(client_id, team_id, prev_key=None, next_key=None):
	team, starred_team = session.query(Team, StarredTeam)\
			.outerjoin(StarredTeam, sa.and_(
				StarredTeam.team_id == team_id,
				StarredTeam.user_id == client_id))\
			.filter(Team.id == team_id)\
			.one()
	is_starred = (starred_team is not None)

	matches_query = session\
			.query(MatchOpponent.match_id, MatchOpponent.team_id, Match, Team)\
			.join(Match, MatchOpponent.match_id == Match.id)\
			.join(Team, MatchOpponent.opponent_id == Team.id)\
			.filter(MatchOpponent.team_id == team_id)
	if prev_key:
		# TODO: Add filter, limit.
		pass
	elif next_key:
		# TODO: Add filter, limit.
		pass

	matches = [
			_get_displayed_team_match(match, opponent_team)
				for match_id, team_id, match, opponent_team in matches_query]
	session.close()

	if prev_key:
		# TODO: Set new_prev_key, new_next_key
		new_prev_key = None
		new_next_key = None
	else:
		# TODO: Set new_prev_key, new_next_key
		new_prev_key = None
		new_next_key = None
	return DisplayedTeam(team_id,
			team.name,
			team.game,
			team.league,
			is_starred,
			team.num_stars,
			matches,
			new_prev_key,
			new_next_key)


def _get_displayed_streamer_match(match, team1, team2):
	return DisplayedStreamerMatch(match.id,
			team1.id,
			team1.name,
			team2.id,
			team2.name,
			match.time,
			match.game,
			match.league,
			match.num_stars,
			match.num_streams)

def get_displayed_streamer(client_id, streamer_id, prev_key=None, next_key=None):
	streamer, starred_streamer = session.query(User, StarredStreamer)\
			.outerjoin(StarredStreamer, sa.and_(
				StarredStreamer.streamer_id == streamer_id,
				StarredStreamer.user_id == client_id))\
			.filter(User.id == streamer_id)\
			.one()
	is_starred = (starred_streamer is not None)

	team_alias1 = sa_orm.aliased(Team)
	team_alias2 = sa_orm.aliased(Team)
	matches_query = session.query(StreamedMatch.match_id, Match, team_alias1, team_alias2)\
			.join(Match, StreamedMatch.match_id == Match.id)\
			.join(team_alias1, Match.team1_id == team_alias1.id)\
			.join(team_alias2, Match.team2_id == team_alias2.id)\
			.filter(StreamedMatch.streamer_id == streamer_id)
	if prev_key:
		# TODO: Add filter, limit.
		pass
	elif next_key:
		# TODO: Add filter, limit.
		pass

	matches = [
			_get_displayed_streamer_match(match, team1, team2)
				for match_id, match, team1, team2 in matches_query]
	session.close()

	if prev_key:
		# TODO: Set new_prev_key, new_next_key
		new_prev_key = None
		new_next_key = None
	else:
		# TODO: Set new_prev_key, new_next_key
		new_prev_key = None
		new_next_key = None
	return DisplayedStreamer(streamer_id,
			streamer.name,
			is_starred,
			streamer.num_stars,
			matches,
			new_prev_key,
			new_next_key)

