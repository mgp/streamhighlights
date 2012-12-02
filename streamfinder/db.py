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
		match = session.query(Match).filter(Match.id == match_id).one()
	except sa.exc.NoResultFound:
		# The flush failed because the client is already streaming this match.
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
	def __init__(self, team_id, name, game, league, is_starred, num_stars, matches, prev_time, prev_match_id, next_time, next_match_id):
		self.team_id = team_id
		self.name = name
		self.game = game
		self.league = league
		self.is_starred = is_starred
		self.num_stars = num_stars
		self.matches = matches
		self.prev_time = prev_time
		self.prev_match_id = prev_match_id
		self.next_time = next_time
		self.next_match_id = next_match_id

	def __repr__(self):
		return 'DisplayedTeam(team_id=%r, name=%r, game=%r, league=%r, is_starred=%r, num_stars=%r, matches=%r, prev_time=%r, prev_match_id=%r, next_time=%r, next_match_id=%r)' % (
				self.team_id,
				self.name,
				self.game,
				self.league,
				self.is_starred,
				self.num_stars,
				self.matches,
				self.prev_time,
				self.prev_match_id,
				self.next_time,
				self.next_match_id)


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
	def __init__(self, streamer_id, name, is_starred, num_stars, matches, prev_time, prev_match_id, next_time, next_match_id):
		self.streamer_id = streamer_id
		self.name = name
		self.is_starred = is_starred
		self.num_stars = num_stars
		self.matches = matches
		self.prev_time = prev_time
		self.prev_match_id = prev_match_id
		self.next_time = next_time
		self.next_match_id = next_match_id

	def __repr__(self):
		return 'DisplayedStreamer(streamer_id=%r, name=%r, is_starred=%r, num_stars=%r, matches=%r, prev_time=%r, prev_match_id=%r, next_time=%r, next_match_id=%r)' % (
				self.streamer_id,
				self.name,
				self.is_starred,
				self.num_stars,
				self.matches,
				self.prev_time,
				self.prev_match_id,
				self.next_time,
				self.next_match_id)


"""An entry in the partial list of matches.
"""
class DisplayedMatchListEntry:
	def __init__(self, match_id, team1, team2, time, game, league):
		self.match_id = match_id
		self.team1 = team1
		self.team2 = team2
		self.time = time
		self.game = game
		self.league = league
	
	def __repr__(self):
		return 'DisplayedMatchListEntry(match_id=%r, team1=%r, team2=%r, time=%r, game=%r, league=%r)' % (
				self.match_id,
				self.team1,
				self.team2,
				self.time,
				self.game,
				self.league)

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


"""An entry in the partial list of teams.
"""
class DisplayedTeamListEntry:
	def __init__(self, team_id, name, game, league):
		self.team_id = team_id
		self.name = name
		self.game = game
		self.league = league
	
	def __repr__(self):
		return 'DisplayedTeamListEntry(team_id=%r, name=%r, game=%r, league=%r)' % (
				self.team_id,
				self.name,
				self.game,
				self.league)

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


"""An entry in the partial list of streaming users.
"""
class DisplayedStreamerListEntry:
	def __init__(self, streamer_id, name):
		self.streamer_id = streamer_id
		self.name = name
	
	def __repr__(self):
		return 'DisplayedStreamerListEntry(streamer_id=%r, name=%r)' % (
				self.streamer_id,
				self.name)

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


# The default number of entities per page.
_PAGE_LIMIT = 30

def _paginate(paginator, prev_col1, prev_col2, next_col1, next_col2, page_limit,
		first_id=None):
	if first_id is None:
		first_id = paginator.get_first_id()
	if first_id is not None:
		query = paginator.get_partial_list_query()

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
						sa.and_(col1 == next_col1, col2 > next_col2), col2 > next_col2))\
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
			if len(items) == page_limit:
				next_col1, next_col2 = paginator.get_pagination_values(last_item)
		elif clicked_prev:
			if (len(items) == page_limit) and not paginator.has_first_id(first_id, first_item):
				prev_col1, prev_col2 = paginator.get_pagination_values(first_item)
			# Came from the following page, so display a Next link.
			next_col1, next_col2 = paginator.get_pagination_values(last_item)
		elif clicked_next:
			if len(items) == page_limit:
				next_col1, next_col2 = paginator.get_pagination_values(last_item)
			# Came from the previous page, so display a Previous link.
			prev_col1, prev_col2 = paginator.get_pagination_values(first_item)
	else:
		items = ()
		prev_col1 = None
		prev_col2 = None
		next_col1 = None
		next_col2 = None

	session.close()
	return (items, prev_col1, prev_col2, next_col1, next_col2)


"""Returns a DisplayedCalendarMatch from the given match and teams.
"""
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

def _get_calendar_entry_query(client_id, team_alias1, team_alias2):
	return session\
			.query(CalendarEntry.match_id, Match, team_alias1, team_alias2)\
			.join(Match, CalendarEntry.match_id == Match.id)\
			.join(team_alias1, Match.team1_id == team_alias1.id)\
			.join(team_alias2, Match.team2_id == team_alias2.id)\
			.filter(CalendarEntry.user_id == client_id)\

def _get_next_viewer_match(client_id, team_alias1, team_alias2):
	result = common_db.optional_one(
			_get_calendar_entry_query(client_id, team_alias1, team_alias2)
				.order_by(CalendarEntry.time.asc(), CalendarEntry.match_id.asc()))
	if result is None:
		return None

	next_match_id, next_match, next_match_team1, next_match_team2 = result
	return _get_displayed_calendar_match(
			next_match, next_match_team1, next_match_team2)

"""A paginator for entries on the client's viewing calendar.
"""
class CalendarEntriesPaginator:
	def __init__(self, client_id, team_alias1, team_alias2):
		self.client_id = client_id
		self.team_alias1 = team_alias1
		self.team_alias2 = team_alias2
	
	def get_partial_list_query(self):
		return _get_calendar_entry_query(
				self.client_id, self.team_alias1, self.team_alias2)

	def get_order_by_columns(self):
		return (CalendarEntry.time, CalendarEntry.match_id)
	
	def execute_query(self, matches_query):
		return tuple((match, team1, team2)
				for match_id, match, team1, team2 in matches_query)
	
	def get_pagination_values(self, item):
		match, team1, team2 = item
		return (match.time, match.id)
	
	def has_first_id(self, first_id, item):
		match, team1, team2 = item
		return (match.id == first_id)

"""Returns a DisplayedCalendar containing calendar entries for streamed matches
where the client has starred the match, either team, or a streamer.
"""
def get_displayed_viewer_calendar(client_id,
		prev_time=None, prev_match_id=None, next_time=None, next_match_id=None,
		page_limit=None):
	# Get the next match for viewing by the client.
	team_alias1 = sa_orm.aliased(Team)
	team_alias2 = sa_orm.aliased(Team)
	first_match = _get_next_viewer_match(client_id, team_alias1, team_alias2)
	if first_match is None:
		# No next match, so return an empty calendar.
		session.close()
		return DisplayedCalendar(None, ())

	# Get the partial list of matches.
	paginator = CalendarEntriesPaginator(client_id, team_alias1, team_alias2)
	matches, prev_time, prev_match_id, next_time, next_match_id = _paginate(
			paginator, prev_time, prev_match_id, next_time, next_match_id, page_limit,
			first_id=first_match.match_id)

	# Return the calendar.
	return DisplayedCalendar(first_match,
			tuple(_get_displayed_calendar_match(match, team1, team2)
					for match, team1, team2 in matches),
			prev_time,
			prev_match_id,
			next_time,
			next_match_id)


def _get_streamed_match_query(streamer_id, team_alias1, team_alias2):
	return session\
			.query(StreamedMatch.match_id, Match, team_alias1, team_alias2)\
			.join(Match, StreamedMatch.match_id == Match.id)\
			.join(team_alias1, Match.team1_id == team_alias1.id)\
			.join(team_alias2, Match.team2_id == team_alias2.id)\
			.filter(StreamedMatch.streamer_id == streamer_id)

def _get_next_streamer_match(client_id, team_alias1, team_alias2):
	result = common_db.optional_one(
			_get_streamed_match_query(client_id, team_alias1, team_alias2)
				.order_by(StreamedMatch.time.asc(), StreamedMatch.match_id.asc()))
	if result is None:
		return None

	next_match_id, next_match, next_match_team1, next_match_team2 = result
	return _get_displayed_calendar_match(
			next_match, next_match_team1, next_match_team2)

"""Returns a DisplayedCalendar containing calendar entries for matches that the
client is streaming.
"""
def get_displayed_streamer_calendar(client_id,
		prev_time=None, prev_match_id=None, next_time=None, next_match_id=None,
		page_limit=None):
	# Get the next match streamed by the client.
	team_alias1 = sa_orm.aliased(Team)
	team_alias2 = sa_orm.aliased(Team)
	first_match = _get_next_streamer_match(client_id, team_alias1, team_alias2)
	if first_match is None:
		# No next match, so return an empty calendar.
		session.close()
		return DisplayedCalendar(None, ())

	# Get the partial list of matches.
	paginator = StreamedMatchesPaginator(client_id, team_alias1, team_alias2)
	matches, prev_time, prev_match_id, next_time, next_match_id = _paginate(
			paginator, prev_time, prev_match_id, next_time, next_match_id, page_limit,
			first_id=first_match.match_id)

	# Return the calendar.
	return DisplayedCalendar(first_match,
			tuple(_get_displayed_calendar_match(match, team1, team2)
					for match, team1, team2 in matches),
			prev_time,
			prev_match_id,
			next_time,
			next_match_id)


class _MatchesPaginator:
	def get_pagination_values(self, item):
		match, team1, team2 = item
		return (match.time, match.id)

	def has_first_id(self, first_id, item):
		match, team1, team2 = item
		return (match.id == first_id)

"""A paginator for matches starred by the client.
"""
class StarredMatchesPaginator(_MatchesPaginator):
	def __init__(self, client_id):
		self.team_alias1 = sa_orm.aliased(Team)
		self.team_alias2 = sa_orm.aliased(Team)
		self.client_id = client_id

	def get_first_id(self):
		first_starred_match = common_db.optional_one(
				session.query(StarredMatch.match_id)
					.order_by(StarredMatch.time.asc(), StarredMatch.match_id.asc()))
		return first_starred_match.match_id if first_starred_match else None
	
	def get_partial_list_query(self):
		return session\
				.query(StarredMatch.match_id, Match, self.team_alias1, self.team_alias2)\
				.join(Match, StarredMatch.match_id == Match.id)\
				.join(self.team_alias1, Match.team1_id == self.team_alias1.id)\
				.join(self.team_alias2, Match.team2_id == self.team_alias2.id)\
				.filter(StarredMatch.user_id == self.client_id)
	
	def get_order_by_columns(self):
		return (StarredMatch.time, StarredMatch.match_id)

	def execute_query(self, matches_query):
		return tuple(
				(match, team1, team2) for match_id, match, team1, team2 in matches_query)

"""A paginator for all matches.
"""
class AllMatchesPaginator(_MatchesPaginator):
	def __init__(self):
		self.team_alias1 = sa_orm.aliased(Team)
		self.team_alias2 = sa_orm.aliased(Team)

	def get_first_id(self):
		first_match = common_db.optional_one(
				session.query(Match.id).order_by(Match.time.asc(), Match.id.asc()))
		return first_match.id if first_match else None
	
	def get_partial_list_query(self):
		return session.query(Match, team_alias1, team_alias2)\
				.join(team_alias1, Match.team1_id == team_alias1.id)\
				.join(team_alias2, Match.team2_id == team_alias2.id)

	def get_order_by_columns(self):
		return (Match.time, Match.id)

	def execute_query(self, matches_query):
		return tuple(matches_query)


class _TeamsPaginator:
	def get_pagination_values(self, team):
		return (team.name, team.id)

	def has_first_id(self, first_id, team):
		return (team.id == first_id)

"""A paginator for teams starred by the client.
"""
class StarredTeamsPaginator(_TeamsPaginator):
	def __init__(self, client_id):
		self.client_id = client_id
	
	def get_first_id(self):
		first_starred_team = common_db.optional_one(
				session.query(StarredTeam.team_id)
					.order_by(StarredTeam.name.asc(), StarredTeam.team_id.asc()))
		return first_starred_team.team_id if first_starred_team else None
	
	def get_partial_list_query(self):
		return session.query(StarredTeam.team_id, Team)\
				.join(Team, StarredTeam.team_id == Team.id)\
				.filter(StarredTeam.user_id == self.client_id)

	def get_order_by_columns(self):
		return (StarredTeam.name, StarredTeam.team_id)

	def execute_query(self, teams_query):
		return tuple(team for team_id, team in teams_query)

"""A paginator for all teams.
"""
class AllTeamsPaginator(_TeamsPaginator):
	def get_first_id(self):
		first_team = common_db.optional_one(
				session.query(Team.id).order_by(Team.name.asc(), Team.id.asc()))
		return first_team.id if first_team else None

	def get_partial_list_query(self):
		return session.query(Team)
	
	def get_order_by_columns(self):
		return (Team.name, Team.id)

	def execute_query(self, teams_query):
		return tuple(teams_query)


class _StreamersPaginator:
	def get_pagination_values(self, streamer):
		return (streamer.name, streamer.id)
	
	def has_first_id(self, first_id, streamer):
		return (streamer.id == first_id)

"""A paginator for streaming users starred by the client.
"""
class StarredStreamersPaginator(_StreamersPaginator):
	def __init__(self, client_id):
		self.client_id = client_id
	
	def get_first_id(self):
		first_starred_streamer = common_db.optional_one(
				session.query(StarredStreamer.streamer_id)
					.order_by(StarredStreamer.name.asc(), StarredStreamer.streamer_id.asc()))
		return first_starred_streamer.streamer_id if first_starred_streamer else None
	
	def get_partial_list_query(self):
		return session.query(StarredStreamer.streamer_id, User)\
				.join(User, StarredStreamer.streamer_id == User.id)\
				.filter(StarredStreamer.user_id == self.client_id)
	
	def get_order_by_columns(self):
		return (StarredStreamer.name, StarredStreamer.streamer_id)

	def execute_query(self, streamers_query):
		return tuple(streamer for streamer_id, streamer in streamers_query)

"""A paginator for all streaming users.
"""
class AllStreamersPaginator(_StreamersPaginator):
	def get_first_id(self):
		first_streamer = common_db.optional_one(
				session.query(User.id)
					.filter(User.can_stream == True)
					.order_by(User.name.asc(), User.id.asc()))
		return first_streamer.id if first_streamer else None
	
	def get_partial_list_query(self):
		return session.query(User).filter(User.can_stream == True)

	def get_order_by_columns(self):
		return (User.name, User.id)
	
	def execute_query(self, streamers_query):
		return tuple(streamers_query)


def _get_match_list(
		client_id, prev_time, prev_match_id, next_time, next_match_id, page_limit,
		paginator):
	matches, prev_time, prev_match_id, next_time, next_match_id = _paginate(
			paginator, prev_time, prev_match_id, next_time, next_match_id, page_limit)
	return DisplayedMatchList(
			tuple(_get_displayed_match_list_entry(match, team1, team2)
				for match, team1, team2 in matches),
			prev_time,
			prev_match_id,
			next_time,
			next_match_id)

"""Returns matches starred by the client.
"""
def get_starred_matches(client_id,
		prev_time=None, prev_match_id=None, next_time=None, next_match_id=None,
		page_limit=None):
	paginator = StarredMatchesPaginator(client_id)
	return _get_match_list(prev_time, prev_match_id, next_time, next_match_id, page_limit,
			paginator)

_ALL_MATCHES_PAGINATOR = AllMatchesPaginator()

"""Returns all matches.
"""
def get_all_matches(client_id,
		prev_time=None, prev_match_id=None, next_time=None, next_match_id=None,
		page_limit=None):
	return _get_match_list(prev_time, prev_match_id, next_time, next_match_id, page_limit,
			_ALL_MATCHES_PAGINATOR)


def _get_team_list_entry(team):
	return DisplayedTeamListEntry(team.id, team.name, team.game, team.league)

def _get_team_list(
		prev_name, prev_team_id, next_name, next_team_id, page_limit,
		paginator):
	teams, prev_name, prev_team_id, next_name, next_team_id = _paginate(
			paginator, prev_name, prev_team_id, next_name, next_team_id, page_limit)
	return DisplayedTeamList(
			tuple(_get_team_list_entry(team) for team in teams),
			prev_name,
			prev_team_id,
			next_name,
			next_team_id)

"""Returns teams starred by the client.
"""
def get_starred_teams(client_id,
		prev_name=None, prev_team_id=None, next_name=None, next_team_id=None,
		page_limit=None):
	paginator = StarredTeamsPaginator(client_id)
	return _get_team_list(prev_name, prev_team_id, next_name, next_team_id, page_limit,
			paginator)

_ALL_TEAMS_PAGINATOR = AllTeamsPaginator()

"""Returns all teams.
"""
def get_all_teams(client_id,
		prev_name=None, prev_team_id=None, next_name=None, next_team_id=None,
		page_limit=None):
	return _get_team_list(prev_name, prev_team_id, next_name, next_team_id, page_limit,
			_ALL_TEAMS_PAGINATOR)


def _get_streamer_list_entry(streamer):
	return DisplayedStreamerListEntry(streamer.id, streamer.name)

def _get_streamer_list(
		prev_name, prev_streamer_id, next_name, next_streamer_id, page_limit,
		paginator):
	streamers, prev_name, prev_streamer_id, next_name, next_streamer_id = _paginate(
			paginator, prev_name, prev_streamer_id, next_name, next_streamer_id, page_limit)
	return DisplayedStreamerList(
			tuple(_get_streamer_list_entry(streamer) for streamer in streamers),
			prev_name,
			prev_streamer_id,
			next_name,
			next_streamer_id)

"""Returns streaming users starred by the client.
"""
def get_starred_streamers(client_id,
		prev_time=None, prev_streamer_id=None, next_time=None, next_streamer_id=None,
		page_limit=None):
	paginator = StarredStreamersPaginator(client_id)
	return _get_streamer_list(
			prev_name, prev_streamer_id, next_name, next_streamer_id, page_limit, paginator)

_ALL_STREAMERS_PAGINATOR = AllStreamersPaginator()

"""Returns all streaming users.
"""
def get_all_streamers(client_id,
		prev_name=None, prev_streamer_id=None, next_name=None, next_streamer_id=None,
		page_limit=None):
	return _get_streamer_list(
			prev_name, prev_streamer_id, next_name, next_streamer_id, page_limit,
			_ALL_STREAMERS_PAGINATOR)


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

"""A paginator for streaming users of a match.
"""
class MatchStreamersPaginator:
	def __init__(self, match_id):
		self.match_id = match_id

	def get_first_id(self):
		first_streamed_match = common_db.optional_one(
				session.query(StreamedMatch.streamer_id)
					.filter(StreamedMatch.match_id == self.match_id)
					.order_by(StreamedMatch.added.asc(), StreamedMatch.streamer_id.asc()))
		return first_streamed_match.streamer_id if first_streamed_match else None

	def get_partial_list_query(self):
		return session.query(StreamedMatch.streamer_id, StreamedMatch.added, User)\
				.join(User, StreamedMatch.streamer_id == User.id)\
				.filter(StreamedMatch.match_id == self.match_id)

	def get_order_by_columns(self):
		return (StreamedMatch.added, StreamedMatch.streamer_id)

	def execute_query(self, streamers_query):
		return tuple((added, streamer) for streamer_id, added, streamer in streamers_query)

	def get_pagination_values(self, item):
		added, streamer = item
		return (added, streamer.id)

	def has_first_id(self, first_id, item):
		added, streamer = item
		return (streamer.id == first_id)

"""Returns a DisplayedMatch containing streaming users.
"""
def get_displayed_match(client_id, match_id,
		prev_time=None, prev_streamer_id=None, next_time=None, next_streamer_id=None,
		page_limit=None):
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
	
	# Get the partial list of streamers for this match.
	if match.num_streams:
		paginator = MatchStreamersPaginator(match_id)
		streamers, prev_time, prev_streamer_id, next_time, next_streamer_id = _paginate(
				paginator, prev_time, prev_streamer_id, next_time, next_streamer_id, page_limit)
	else:
		streamers = ()
		prev_time = None
		prev_streamer_id = None
		next_time = None
		next_streamer_id = None

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

"""A paginator for opponents of a team.
"""
class MatchOpponentsPaginator:
	def __init__(self, team_id):
		self.team_id = team_id

	def get_first_id(self):
		first_match_opponent = common_db.optional_one(
				session.query(MatchOpponent.match_id)
					.filter(MatchOpponent.team_id == self.team_id)
					.order_by(MatchOpponent.time.asc(), MatchOpponent.match_id.asc()))
		return first_match_opponent.match_id if first_match_opponent else None

	def get_partial_list_query(self):
		return session\
				.query(MatchOpponent.match_id, MatchOpponent.team_id, Match, Team)\
				.join(Match, MatchOpponent.match_id == Match.id)\
				.join(Team, MatchOpponent.opponent_id == Team.id)\
				.filter(MatchOpponent.team_id == self.team_id)

	def get_order_by_columns(self):
		return (MatchOpponent.time, MatchOpponent.match_id)

	def execute_query(self, matches_query):
		return tuple((match, opponent_team)
				for match_id, team_id, match, opponent_team in matches_query)

	def get_pagination_values(self, item):
		match, opponent_team = item
		return (match.time, match.id)

	def has_first_id(self, first_id, item):
		match, opponent_team = item
		return (match.id == first_id)

"""Returns a DisplayedTeam containing scheduled matches.
"""
def get_displayed_team(client_id, team_id,
		prev_time=None, prev_match_id=None, next_time=None, next_match_id=None,
		page_limit=None):
	# Get the team.
	team, starred_team = session.query(Team, StarredTeam)\
			.outerjoin(StarredTeam, sa.and_(
				StarredTeam.team_id == team_id,
				StarredTeam.user_id == client_id))\
			.filter(Team.id == team_id)\
			.one()
	is_starred = (starred_team is not None)

	# Get the partial list of matches for this team.
	paginator = MatchOpponentsPaginator(team_id)
	matches, prev_time, prev_match_id, next_time, next_match_id = _paginate(
			paginator, prev_time, prev_match_id, next_time, next_match_id, page_limit)
	
	# Return the displayed team.
	return DisplayedTeam(team_id,
			team.name,
			team.game,
			team.league,
			is_starred,
			team.num_stars,
			tuple(_get_displayed_team_match(match, opponent_team)
					for match, opponent_team in matches),
			prev_time,
			prev_match_id,
			next_time,
			next_match_id)


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

"""A paginator for matches streamed by a user.
"""
class StreamedMatchesPaginator:
	def __init__(self, streamer_id, team_alias1=None, team_alias2=None):
		self.streamer_id = streamer_id
		self.team_alias1 = team_alias1 if team_alias1 else sa_orm.aliased(Team)
		self.team_alias2 = team_alias2 if team_alias2 else sa_orm.aliased(Team)

	def get_first_id(self):
		first_streamed_match = common_db.optional_one(
				session.query(StreamedMatch.match_id)\
					.filter(StreamedMatch.streamer_id == self.streamer_id)\
					.order_by(StreamedMatch.time.asc(), StreamedMatch.match_id.asc()))
		return first_streamed_match.match_id if first_streamed_match else None

	def get_partial_list_query(self):
		return _get_streamed_match_query(
				self.streamer_id, self.team_alias1, self.team_alias2)

	def get_order_by_columns(self):
		return (StreamedMatch.time, StreamedMatch.match_id)

	def execute_query(self, matches_query):
		return tuple((match, team1, team2)
				for match_id, match, team1, team2 in matches_query)

	def get_pagination_values(self, item):
		match, team1, team2 = item
		return (match.time, match.id)

	def has_first_id(self, first_id, item):
		match, team1, team2 = item
		return (match.id == first_id)

"""Returns a DisplayedStreamer containing scheduled streamed matches.
"""
def get_displayed_streamer(client_id, streamer_id,
		prev_time=None, prev_match_id=None, next_time=None, next_match_id=None,
		page_limit=None):
	# Get the streamer.
	streamer, starred_streamer = session.query(User, StarredStreamer)\
			.outerjoin(StarredStreamer, sa.and_(
				StarredStreamer.streamer_id == streamer_id,
				StarredStreamer.user_id == client_id))\
			.filter(User.id == streamer_id)\
			.one()
	is_starred = (starred_streamer is not None)

	# Get the partial list of matches streamed by this user.
	paginator = StreamedMatchesPaginator(streamer_id)
	matches, prev_time, prev_match_id, next_time, next_match_id = _paginate(
			paginator, prev_time, prev_match_id, next_time, next_match_id, page_limit)
	
	# Return the displayed streaming user.
	return DisplayedStreamer(streamer_id,
			streamer.name,
			is_starred,
			streamer.num_stars,
			tuple(_get_displayed_streamer_match(match, team1, team2)
					for match, team1, team2 in matches),
			prev_time,
			prev_match_id,
			next_time,
			next_match_id)

