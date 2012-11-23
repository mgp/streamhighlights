from datetime import datetime
import re
import sqlalchemy as sa
import sqlalchemy.engine as sa_engine
import sqlalchemy.ext.declarative as sa_ext_declarative
import sqlalchemy.orm as sa_orm
import sqlalchemy.schema as sa_schema
import sys

import common_db

"""A user of the site.
"""
class User(common_db.UserMixin, common_db._Base):
	__tablename__ = 'Users'

	can_stream = sa.Column(sa.Boolean, nullable=False)
	stream_info = sa.Column(sa.String)

	def __repr__(self):
		return 'User(id=%r, name=%r, image_url_small=%r, image_url_large=%r, created=%r, last_seen=%r, url_by_id=%r, url_by_name=%r, can_stream=%r, stream_info=%r, steam_user=%r, twitch_user=%r)' % (
				self.id,
				self.name,
				self.image_url_small,
				self.image_url_large,
				self.created.isoformat(),
				self.last_seen.isoformat() if self.last_seen else None,
				self.url_by_id,
				self.url_by_name,
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
	fingerprint = sa.Column(sa.String, nullable=False)

	def __repr__(self):
		print 'Team(id=%r, name=%r, game=%r, league=%r, num_stars=%r, fingerprint=%r)' % (
				self.id,
				self.name,
				self.game,
				self.league,
				self.num_stars,
				self.fingerprint)


"""A match between teams.
"""
class Match(common_db._Base):
	__tablename__ = 'Matches'

	id = sa.Column(sa.Integer, primary_key=True)
	team1_id = sa.Column(sa.Integer, sa.ForeignKey('Teams.id'))
	team2_id = sa.Column(sa.Integer, sa.ForeignKey('Teams.id'))
	time = sa.Column(sa.DateTime, nullable=False)
	game = sa.Column(sa.String, nullable=False)
	league = sa.Column(sa.String, nullable=False)
	num_stars = sa.Column(sa.Integer, default=0, nullable=False)
	num_streams = sa.Column(sa.Integer, default=0, nullable=False)
	is_streamed = sa.Column(sa.Boolean, default=False, nullable=False)
	fingerprint = sa.Column(sa.String, nullable=False)

	def __repr__(self):
		print 'Match(id=%r, team1_id=%r, team2_id=%r, time=%r, game=%r, league=%r, num_stars=%r, num_streams=%r, is_streamed=%r, fingerprint=%r)' % (
				self.id,
				self.team1_id,
				self.team2_id,
				self.time,
				self.game,
				self.league,
				self.num_stars,
				self.num_streams,
				self.is_streamed,
				self.fingerprint)


"""An edit for a match.
"""
class MatchEdit(common_db._Base):
	__tablename__ = 'MatchEdits'

	id = sa.Column(sa.Integer, primary_key=True)
	match_id = sa.Column(sa.Integer, sa.ForeignKey('Matches.id'))
	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'))
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
class CalendaryEntry(common_db._Base):
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


def create_all():
	common_db.create_all()

	global Teams
	global Matches
	global MatchEdits
	global StarredMatches
	global StarredTeams
	global StarredStreamers
	global StreamedMatches
	global CalendarEntries

	# Create aliases for each table.
	Teams = Team.__table__
	Matches = Match.__table__
	MatchEdits = MatchEdit.__table__
	StarredMatches = StarredMatch.__table__
	StarredTeams = StarredTeam.__table__
	StarredStreamers = StarredStreamer.__table__
	StreamedMatches = StreamedMatch.__table__
	CalendarEntries = CalendarEntry.__table__

def drop_all():
	global Teams
	global Matches
	global MatchEdits
	global StarredMatches
	global StarredTeams
	global StarredStreamers
	global StreamedMatches

	# Clear aliases for each table.
	Teams = None
	Matches = None
	MatchEdits = None
	StarredMatches = None
	StarredTeams = None
	StarredStreamers = None
	StreamedMatches = None
	CalendarEntries = None

	common_db.drop_all()


"""Adds a match between two teams at a given time.
"""
def add_match(team1_id, team2_id, time, game, league, now=None):
	try:
		match = Match(team1_id=team1_id, team2_id=team2_id, game=game, league=league, time=time)
		session.add(match)
		session.commit()
		return match.id
	except sa.exc.IntegrityError:
		# The commit failed because teams with the given identifiers are missing.
		session.rollback()
		raise common_db.DbException._chain()

"""Adds a team in the given game and league.
"""
def add_team(name, game, league):
	team = Team(name=name, game=game, league=league)
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
	matches_cursor = session.query(Match)\
			.filter(Match.team1_id == team_id, Match.is_streamed == True)
	for match in matches_cursor:
		_increment_num_user_stars(client_id, match, now)
	matches_cursor = session.query(Match)\
			.filter(Match.team2_id == team_id, Match.is_streamed == True)
	for match in matches_cursor:
		_increment_num_user_stars(client_id, match, now)
	
	session.commit()


"""Removes a star by the client for the team with the given identifier.
"""
def remove_star_team(client_id, team_id, now=None):
	now = _get_now(now)

	# Remove the client's star for the team.
	result = session.execute(StarredTeam.delete().where(sa.and_(
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
	match_ids_cursor = session.query(Match.id)\
			.filter(Match.team1_id == team_id, Match.is_streamed == True)
	for match_id in match_ids_cursor:
		_decrement_num_user_stars(client_id, match_id, now)
	match_ids_cursor = session.query(Match.id)\
			.filter(Match.team2_id == team_id, Match.is_streamed == True)
	for match_id in match_ids_cursor:
		_decrement_num_user_stars(client_id, match_id, now)

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
	matches_cursor = session.query(Match)\
			.join(Match, StreamedMatch.match_id == Match.id)\
			.filter(StreamedMatch.streamer_id == streamer_id)
	for match in matches_cursor:
		_increment_num_user_stars(client_id, match, now)

	session.commit()

"""Removes a star by the client for the streaming user with the given identifier.
"""
def remove_star_streamer(client_id, streamer_id, now=None):
	now = _get_now(now)

	# Remove the client's star for the streaming user.
	result = session.execute(StarredStreamer.delete().where(sa.and_(
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
	for match_id in match_ids_cursor:
		_decrement_num_user_stars(client_id, match_id, now)

	session.commit()


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
		match.num_streams = 1
		match.is_streamed = True
		_add_first_stream_calendar_entries(client_id, match, now)

	session.commit()

"""Removes a stream by the client for the match with the given identifier.
"""
def remove_stream_match(client_id, match_id, now=None):
	now = _get_now(now)

	# Remove the client as a user streaming the match.
	result = session.execute(StreamedMatch.delete().where(sa.and_(
			StreamedMatch.user_id == client_id,
			StreamedMatch.match_id == match_id)))
	if not result.rowcount:
		session.rollback()
		return
	
	num_streams = session.query(Match.num_streams)\
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
def _decrement_num_user_stars(user_ids, match_id, now):
	num_user_stars = session.query(CalendarEntry.num_user_stars)\
			.filter(
				CalendarEntry.user_id == user_id,
				CalendarEntry.match_id == match_id)\
			.one()
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
	for user_id in user_ids_cursor:
		entry = _get_calendar_entry(user_id, match)
		session.add(entry)

	# Add a CalendarEntry for each user who starred the first steam.
	user_ids_cursor = session.query(StarredTeam.user_id)\
			.filter(StarredTeam.team_id == match.team1_id)
	_multi_increment_num_user_stars(user_ids_cursor, match, now)
	# Add a CalendarEntry for each user who starred the second team.
	user_ids_cursor = session.query(StarredTeam.user_id)\
			.filter(StarredTeam.team_id == match.team2_id)
	_multi_increment_num_user_stars(user_ids_cursor, match, now)

	# Add a CalendarEntry for each user who starred the streaming user.
	user_ids_cursor = session.query(StarredStreamer.user_id)\
			.filter(StarredStreamer.streamer_id == client_id)
	_multi_increment_num_user_stars(user_ids_cursor, match, now)

"""Updates or creates CalendarEntries for users, given that the client was
added as a streamer, but not the first one.
"""
def _add_not_first_stream_calendar_entries(client_id, match, now):
	# If needed, add a CalendarEntry for each user who starred the streaming user.
	user_ids_cursor = session.query(StarredStreamer.user_id)\
			.filter(StarredStreamer.streamer_id == client_id)
	_multi_increment_num_user_stars(user_ids_cursor, match, now)


"""Updates or deletes CalendarEntries for users, given that the client was
removed as a streamer, but not the last one.
"""
def _remove_not_last_stream_calendar_entries(client_id, match_id, now):
	# If needed, remove a CalendarEntry for each user who starred the streaming user.
	user_ids_cursor = session.query(StarredStreamer.user_id)\
			.filter(StarredStreamer.streamer_id == client_id)
	_multi_decrement_num_user_stars(user_ids_cursor, match_id, now)

"""Updates or deletes CalendarEntries for users, given that the client was
removed as the last streaming user.
"""
def _remove_last_stream_calendar_entries(client_id, match_id, now):	
	# Remove every CalendarEntry for this match.
	result = session.execute(
			CalendarEntries.delete().where(CalendarEntry.user_id == client_id))



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
	def __init__(self, next_match, matches, prev_key, next_key):
		self.next_match = next_match
		self.matches = matches
		self.prev_key = prev_key
		self.next_key = next_key
	
	def __repr__(self):
		return 'DisplayedCalendar(next_match=%r, matches=%r, next_key=%r, prev_key=%r)' % (
				self.next_match,
				self.matches,
				self.prev_key,
				self.next_key)


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
	def __init__(self, match_id, team1, team2, time, game, league, num_stars, streamers, prev_key, next_key):
		self.match_id = match_id
		self.team1 = team1
		self.team2 = team2
		self.time = time
		self.game = game
		self.league = league
		self.num_stars = num_stars
		self.streamers = streamers
		self.prev_key = prev_key
		self.next_key = next_key
	
	def __repr__(self):
		return 'DisplayedMatch(match_id=%r, team1=%r, team2=%r, time=%r, game=%r, league=%r, streamers=%r, prev_key=%r, next_key=%r)' % (
				self.match_id,
				self.team1,
				self.team2,
				self.time,
				self.game,
				self.league,
				self.streamers,
				self.prev_key,
				self.next_key)


"""A match for a DisplayedTeam.
"""
class DisplayedTeamMatch:
	def __init__(self, opponent_id, opponent_name, time, num_stars, num_streams):
		self.opponent_id = opponent_id
		self.opponent_name = opponent_name
		self.time = time
		self.num_stars = num_stars
		self.num_streams = num_streams
	
	def __repr__(self):
		return 'DisplayedTeamMatch(opponent_id=%r, opponent_name=%r, time=%r, num_stars=%r, num_streams=%r)' % (
				self.opponent_id,
				self.opponent_name,
				self.time,
				self.num_stars,
				self.num_streams)

"""A detailed view of a team.
"""
class DisplayedTeam:
	def __init__(self, team_id, name, game, league, num_stars, matches, prev_key, next_key):
		self.team_id = team_id
		self.name = name
		self.game = game
		self.league = league
		self.num_stars = num_stars
		self.matches = matches
		self.prev_key = prev_key
		self.next_key = next_key

	def __repr__(self):
		return 'DisplayedTeam(team_id=%r, name=%r, game=%r, league=%r, num_stars=%r, matches=%r, prev_key=%r, next_key=%r)' % (
				self.team_id,
				self.name,
				self.game,
				self.league,
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
	def __init__(self, streamer_id, name, num_stars, matches, prev_key, next_key):
		self.streamer_id = streamer_id
		self.name = name
		self.num_stars = num_stars
		self.matches = matches
		self.prev_key = prev_key
		self.next_key = next_key

	def __repr__(self):
		return 'DisplayedStreamer(streamer_id=%r, name=%r, num_stars=%r, matches=%r, prev_key=%r, next_key=%r)' % (
				self.streamer_id,
				self.name,
				self.num_stars,
				self.matches,
				self.prev_key,
				self.next_key)

