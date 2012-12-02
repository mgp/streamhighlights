from datetime import datetime
import re
import sqlalchemy as sa
import sqlalchemy.engine as sa_engine
import sqlalchemy.ext.declarative as sa_ext_declarative
import sqlalchemy.orm as sa_orm
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
class UserMixin(object):
	id = sa.Column(sa.Integer, primary_key=True)
	name = sa.Column(sa.String, nullable=False)
	image_url_small = sa.Column(sa.String)
	image_url_large = sa.Column(sa.String)
	created = sa.Column(sa.DateTime, nullable=False)
	last_seen = sa.Column(sa.DateTime)

	url_by_id = sa.Column(sa.String, nullable=False)
	url_by_name = sa.Column(sa.String)

	@sa_ext_declarative.declared_attr
	def steam_user(cls):
		return sa_orm.relationship('SteamUser', uselist=False, backref='user')
	@sa_ext_declarative.declared_attr
	def twitch_user(cls):
		return sa_orm.relationship('TwitchUser', uselist=False, backref='user')


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


def _get_now(now):
	if now is None:
		return datetime.utcnow()
	return now

_USER_URL_SEPARATOR = ':'
_USER_URL_STEAM_PREFIX = 's'
_USER_URL_TWITCH_PREFIX = 't'

"""Returns the url_by_id value for a User from Steam.
"""
def _get_steam_url_by_id(steam_id):
	return _USER_URL_SEPARATOR.join((_USER_URL_STEAM_PREFIX, str(steam_id)))

"""Returns the url_by_id value for a User from Twitch.
"""
def _get_twitch_url_by_id(twitch_id):
	return _USER_URL_SEPARATOR.join((_USER_URL_TWITCH_PREFIX, str(twitch_id)))

_GET_COMMUNITY_ID_REGEX = re.compile('steamcommunity\.com/id/(?P<community_id>\w+)$')

def _get_steam_url_by_name_from_community_id(community_id):
	return _USER_URL_SEPARATOR.join((_USER_URL_STEAM_PREFIX, community_id))

"""Returns the url_by_name value for a User from Steam, or None if one cannot
be created from the profile URL.
"""
def _get_steam_url_by_name_from_profile_url(profile_url):
	if profile_url is None:
		return None
	community_id_match = _GET_COMMUNITY_ID_REGEX.search(profile_url)
	if not community_id_match:
		return None
	community_id = community_id_match.group('community_id')
	return _get_steam_url_by_name_from_community_id(community_id)

"""Returns the url_by_name value for a User from Twitch.
"""
def _get_twitch_url_by_name(name):
	return _USER_URL_SEPARATOR.join((_USER_URL_TWITCH_PREFIX, name))

"""Returns the best URL for a given User.
"""
def _get_user_url(url_by_id, url_by_name):
	if url_by_name is not None:
		prefix, remainder = url_by_name.split(_USER_URL_SEPARATOR, 1)
		if prefix == _USER_URL_STEAM_PREFIX:
			# The remainder is the Steam community identifier.
			return '/user/steam/%s' % remainder
		elif prefix == _USER_URL_TWITCH_PREFIX:
			# The remainder is the Twitch user name.
			return '/user/twitch/%s' % remainder
		else:
			raise ValueError('Invalid url_by_name=%s' % url_by_name)

	prefix, remainder = url_by_id.split(_USER_URL_SEPARATOR, 1)
	if prefix == _USER_URL_STEAM_PREFIX:
		# The remainder is the Steam identifier.
		return '/user/steam_id/%s' % remainder
	elif prefix == _USER_URL_TWITCH_PREFIX:
		# The remainder is the Twitch identifier.
		return '/user/twitch_id/%s' % remainder
	else:
		raise ValueError('Invalid url_by_id=%s' % url_by_id)

def _get_twitch_url(user):
	if user.url_by_name is not None:
		return '/user/twitch/%s' % name
	prefix, twitch_id = user.url_by_id.split(_USER_URL_SEPARATOR, 1)
	return '/user/twitch_id/%s' % twitch_id

def _remove_equal_url_by_name(user_class, users_table, url_by_name, user_id):
	if url_by_name is not None:
		# The url_by_name must be unique.
		update_statement = users_table.update().where(user_class.url_by_name == url_by_name)
		if user_id is not None:
			update_statement = update_statement.where(user_class.id != user_id)
		session.execute(update_statement.values({user_class.url_by_name: None}))

"""Called whenever a Twitch user has been authenticated and logged in.
"""
def twitch_user_logged_in(user_class, users_table,
		twitch_id, name, display_name, logo, access_token,
		configure_user=None, now=None):
	now = _get_now(now)
	url_by_name = _get_twitch_url_by_name(name)
	try:
		twitch_user = session.query(TwitchUser)\
				.options(sa_orm.joinedload(TwitchUser.user))\
				.filter(TwitchUser.twitch_id == twitch_id).one()
		_remove_equal_url_by_name(user_class, users_table, url_by_name, twitch_user.user.id)
	except sa_orm.exc.NoResultFound:
		_remove_equal_url_by_name(user_class, users_table, url_by_name, None)
		twitch_user = TwitchUser(twitch_id=twitch_id)
		user = user_class(created=now, url_by_id=_get_twitch_url_by_id(twitch_id))
		if configure_user is not None:
			configure_user(user)
		twitch_user.user = user
		session.add(twitch_user)

	# Update the User.
	twitch_user.user.name = display_name
	twitch_user.user.image_url_large = logo
	twitch_user.user.last_seen = now
	twitch_user.user.url_by_name = url_by_name
	# Update the TwitchUser.
	twitch_user.name = name
	twitch_user.access_token = access_token

	session.commit()
	return twitch_user.user.id

"""Called whenever a Steam user has been authenticated and logged in.
"""
def steam_user_logged_in(user_class, users_table,
		steam_id, personaname, profile_url, avatar, avatar_full,
		configure_user=None, now=None):
	now = _get_now(now)
	url_by_name = _get_steam_url_by_name_from_profile_url(profile_url)
	try:
		steam_user = session.query(SteamUser)\
				.options(sa_orm.joinedload(SteamUser.user))\
				.filter(SteamUser.steam_id == steam_id).one()
		_remove_equal_url_by_name(user_class, users_table, url_by_name, steam_user.user.id)
	except sa_orm.exc.NoResultFound:
		_remove_equal_url_by_name(user_class, users_table, url_by_name, None)
		steam_user = SteamUser(steam_id=steam_id)
		user = user_class(created=now, url_by_id=_get_steam_url_by_id(steam_id))
		if configure_user is not None:
			configure_user(user)
		steam_user.user = user
		session.add(steam_user)
	
	# Update the User.
	steam_user.user.name = personaname
	steam_user.user.image_url_small = avatar
	steam_user.user.image_url_large = avatar_full
	steam_user.user.last_seen = now
	steam_user.user.url_by_name = url_by_name
	# Update the SteamUser.
	steam_user.profile_url = profile_url

	session.commit()
	return steam_user.user.id

"""Like calling one() on query, but returns None instead of raising NoResultFound.
"""
def optional_one(query):
	results = query.limit(1).all()
	if results:
		return results[0] 
	return None

def create_all():
	_Base.metadata.create_all(_engine)

	global SteamUsers
	global TwitchUsers

	# Create aliases for each table.
	SteamUsers = SteamUser.__table__
	TwitchUsers = TwitchUser.__table__

def drop_all():
	global SteamUsers
	global TwitchUsers
	
	# Clear aliases for each table.
	SteamUsers = None
	TwitchUsers = None

	_Base.metadata.drop_all(_engine)

