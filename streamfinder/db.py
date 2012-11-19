from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.engine as sa_engine
import sqlalchemy.ext.declarative as sa_ext_declarative
import sqlalchemy.orm as sa_orm
import sqlalchemy.schema as sa_schema
import sys

"""Exception class raised by the database.
"""
class DbException(Exception):
	def __init__(self, reason):
		Exception.__init__(self)
		self.reason = reason
	
	def __str__(self):
		return str(self.reason)

	@staticmethod
	def _chain():
		exception_type, exception_value, traceback = sys.exc_info()
		raise DbException(exception_value), None, traceback


def get_engine(testing=True):
	if testing:
		return sa.create_engine('sqlite:///:memory:', echo=False)
	else:
		# TODO
		return None

_engine = get_engine()
_Session = sa_orm.sessionmaker(bind=_engine)
# TODO: Use a contextual session
# http://docs.sqlalchemy.org/en/rel_0_7/orm/session.html#unitofwork-contextual
session = _Session()

# http://docs.sqlalchemy.org/en/rel_0_7/dialects/sqlite.html#foreign-key-support
@sa.event.listens_for(sa_engine.Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
	cursor = dbapi_connection.cursor()
	cursor.execute("PRAGMA foreign_keys=ON")
	cursor.close()


_Base = sa_ext_declarative.declarative_base()

"""A user of the site.
"""
class User(_Base):
	__tablename__ = 'Users'

	id = sa.Column(sa.Integer, primary_key=True)
	name = sa.Column(sa.String, nullable=False)
	image_url_small = sa.Column(sa.String)
	image_url_large = sa.Column(sa.String)
	created = sa.Column(sa.DateTime, nullable=False)
	last_seen = sa.Column(sa.DateTime)

	url_by_id = sa.Column(sa.String, nullable=False)
	url_by_name = sa.Column(sa.String)

	steam_user = sa_orm.relationship('SteamUser', uselist=False, backref='user')
	twitch_user = sa_orm.relationship('TwitchUser', uselist=False, backref='user')

	def __repr__(self):
		return 'User(id=%r, name=%r, image_url_small=%r, image_url_large=%r, created=%r, last_seen=%r, url_by_id=%r, url_by_name=%r, steam_user=%r, twitch_user=%r)' % (
				self.id,
				self.name,
				self.image_url_small,
				self.image_url_large,
				self.created.isoformat(),
				self.last_seen.isoformat() if self.last_seen else None,
				self.url_by_id,
				self.url_by_name,
				self.steam_user,
				self.twitch_user)


"""If the user logged in through Steam, the details of that user on Steam.
"""
class SteamUser(_Base):
	__tablename__ = 'SteamUsers'

	steam_id = sa.Column(sa.Integer, primary_key=True)
	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'))
	# Used to construct URL to user on Steam.
	profile_url = sa.Column(sa.String)

	def __repr__(self):
		# Has backref: user.
		return 'SteamUser(steam_id=%r, user_id=%r, profile_url=%r, user=%r)' % (
				self.steam_id,
				self.user_id,
				self.profile_url,
				self.user)


"""If the user logged in through Twitch, the details of that user on Twitch.
"""
class TwitchUser(_Base):
	__tablename__ = 'TwitchUsers'

	twitch_id = sa.Column(sa.Integer, primary_key=True)
	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'))
	# Used to construct URL to user on Twitch.
	name = sa.Column(sa.String, nullable=False)
	access_token = sa.Column(sa.String)

	def __repr__(self):
		# Has backref: user.
		return 'TwitchUser(twitch_id=%r, user_id=%r, name=%r, access_token=%r)' % (
				self.twitch_id,
				self.user_id,
				self.name,
				self.access_token)


"""A match between teams.
"""
class Match(_Base):
	__tablename__ = 'Matches'

	id = sa.Column(sa.Integer, primary_key=True)
	team1 = sa.Column(sa.Integer, sa.ForeignKey('Teams.id'))
	team2 = sa.Column(sa.Integer, sa.ForeignKey('Teams.id'))
	time = sa.Column(sa.DateTime, nullable=False)
	game = sa.Column(sa.String, nullable=False)
	league = sa.Column(sa.DateTime, nullable=False)
	num_stars = sa.Column(sa.Integer, default=0, nullable=False)
	num_streams = sa.Column(sa.Integer, default=0, nullable=False)

	def __repr__(self):
		print 'Match(id=%r, team1=%r, team2=%r, time=%r, game=%r, league=%r, num_stars=%r, num_streams=%r)' % (
				self.id,
				self.team1,
				self.team2,
				self.time,
				self.game,
				self.league,
				self.num_stars,
				self.num_streams)


"""A team in a match.
"""
class Team(_Base):
	__tablename__  'Teams'

	id = sa.Column(sa.Integer, primary_key=True)
	name = sa.Column(sa.String, nullable=False)
	game = sa.Column(sa.String, nullable=False)
	league = sa.Column(sa.String, nullable=False)
	num_stars = sa.Column(sa.Integer, default=0, nullable=False)

	def __repr__(self):
		print 'Team(id=%r, name=%r, game=%r, league=%r, num_stars=%r)' % (
				self.id,
				self.name,
				self.game,
				self.league,
				self.num_stars)


"""The association from users to their starred matches.
"""
class StarredMatch(_Base):
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
class StarredTeam(_Base):
	__tablename__ = 'StarredTeam'

	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'), primary_key=True)
	team_id = sa.Column(sa.Integer, sa.ForeignKey('Teams.id'), primary_key=True)
	added = sa.Column(sa.DateTime, nullable=False)

	def __repr__(self):
		return 'StarredTeam(user_id=%r, team_id=%r, added=%r)' % (
				self.user_id,
				self.team_id,
				self.added)


"""The association from users to their streamed matches.
"""
class StreamedMatch(_Base):
	__tablename__ = 'StreamedMatches'

	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'), primary_key=True)
	match_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'), primary_key=True)
	added = sa.Column(sa.DateTime, 

	def __repr__(self):
		return 'StreamedMatch(user_id=%r, match_id=%r, added=%r)' % (
				self.user_id,
				self.match_id,
				self.added)


def create_all():
	global Users
	global SteamUsers
	global TwitchUsers
	global Teams
	global Matches
	global StarredMatch
	global StarredTeam
	global StreamedMatch

	_Base.metadata.create_all(_engine)

	# Create aliases for each table.
	Users = User.__table__
	SteamUsers = SteamUser.__table__
	TwitchUsers = TwitchUser.__table__
	Teams = Team.__table__
	Matches = Match.__table__
	StarredMatches = StarredMatch.__table__
	StarredTeams = StarredTeam.__table__
	StreamedMatches = StreamedMatch.__table__

def drop_all():
	global Users
	global SteamUsers
	global TwitchUsers
	global Teams
	global Matches
	global StarredMatches
	global StarredTeams
	global StreamedMatches

	# Clear aliases for each table.
	Users = None
	SteamUsers = None
	TwitchUsers = None
	Teams = None
	Matches = None
	StarredMatches = None
	StarredTeams = None
	StreamedMatches = None

	_Base.metadata.drop_all(_engine)


def _get_now(now):
	if now is None:
		return datetime.utcnow()
	return now


"""Adds a star by the client for the match with the given identifier.
"""
def add_star_match(client_id, match_id, now=None):
	now = _get_now(now)
	# Add the star for the match.
	star = StarredMatch(user_id=client_id, match_id=match_id, added=now)
	session.add(star)
	# Increment the count of stars for the match.
	session.execute(Matches.update()
			.where(Match.id == match_id)
			.values({Match.num_stars: Match.num_stars + 1}))
	session.commit()

"""Removes a star by the client for the match with the given identifier.
"""
def remove_star_match(client_id, match_id, now=None):
	# Remove the client's star for the match.
	result = session.execute(StarredMatch.delete().where(sa.and_(
			StarredMatch.user_id == client_id,
			StarredMatch.match_id == match_id)))
	if result.rowcount:
		# Decrement the count of stars for the match.
		session.execute(Matches.update()
				.where(Match.id == match_id)
				.values({Match.num_stars: Match.num_stars - 1}))
		session.commit()
	else:
		session.rollback()


"""Adds a star by the client for the team with the given identifier.
"""
def add_star_team(client_id, team_id, now=None):
	now = _get_now(now)
	# Add the star for the team.
	star = StarredTeam(user_id=client_id, team_id=team_id, added=now)
	session.add(star)
	# Increment the count of stars for the team.
	session.execute(Teams.update()
			.where(Team.id == team_id)
			.values({Team.num_stars: Team.num_stars + 1}))
	session.commit()

"""Removes a star by the client for the team with the given identifier.
"""
def remove_star_team(client_id, team_id, now=None):
	# Remove the client's star for the team.
	result = session.execute(StarredTeam.delete().where(sa.and_(
			StarredTeam.user_id == client_id,
			StarredTeam.team_id == team_id)))
	if result.rowcount:
		# Decrement the count of stars for the team.
		session.execute(Teams.update()
				.where(Team.id == team_id)
				.values({Team.num_stars: Team.num_stars - 1}))
		session.commit()
	else:
		session.rollback()

"""Adds a stream by the client for the match with the given identifier.
"""
def add_stream_match(client_id, match_id, now=None):
	pass

"""Removes a stream by the client for the match with the given identifier.
"""
def remove_stream_match(client_id, match_id, now=None):
	pass

