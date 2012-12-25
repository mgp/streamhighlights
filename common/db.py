from datetime import datetime
import functools
import re
import sqlalchemy as sa
import sqlalchemy.engine as sa_engine
import sqlalchemy.ext.declarative as sa_ext_declarative
import sqlalchemy.orm as sa_orm
import sys


def close_session(f):
	"""A decorator that closes the session before returning a result."""
	@functools.wraps(f)
	def decorated_function(*pargs, **kwargs):
		result = f(*pargs, **kwargs)
		session.close()
		return result
	return decorated_function

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


def get_engine(testing=False):
	if testing:
		# http://docs.sqlalchemy.org/en/rel_0_7/dialects/sqlite.html#foreign-key-support
		@sa.event.listens_for(sa_engine.Engine, "connect")
		def set_sqlite_pragma(dbapi_connection, connection_record):
			cursor = dbapi_connection.cursor()
			cursor.execute("PRAGMA foreign_keys=ON")
			cursor.close()

		return sa.create_engine(
				'sqlite:///:memory:', convert_unicode=True, echo=False)
	else:
		return sa.create_engine(
				'postgresql+psycopg2://streamcalendar:streamcalendar@localhost/streamcalendar',
				echo=False)

_engine = get_engine()
# Use scoped_session with Flask: http://flask.pocoo.org/docs/patterns/sqlalchemy/
session = sa_orm.scoped_session(sa_orm.sessionmaker(
		autocommit=False, autoflush=False, bind=_engine))

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
		return 'SteamUser(steam_id=%r, user_id=%r, profile_url=%r)' % (
				self.steam_id,
				self.user_id,
				self.profile_url)


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


_USER_URL_SEPARATOR = ':'
_USER_URL_STEAM_PREFIX = 's'
_USER_URL_TWITCH_PREFIX = 't'

def _get_steam_url_by_id(steam_id):
	"""Returns the url_by_id value for a User from Steam."""
	return _USER_URL_SEPARATOR.join((_USER_URL_STEAM_PREFIX, str(steam_id)))

def _get_twitch_url_by_id(twitch_id):
	"""Returns the url_by_id value for a User from Twitch."""
	return _USER_URL_SEPARATOR.join((_USER_URL_TWITCH_PREFIX, str(twitch_id)))

_GET_COMMUNITY_ID_REGEX = re.compile('steamcommunity\.com/id/(?P<community_id>\w+)$')

def _get_steam_url_by_name_from_community_id(community_id):
	return _USER_URL_SEPARATOR.join((_USER_URL_STEAM_PREFIX, community_id))

def _get_steam_url_by_name_from_profile_url(profile_url):
	"""Returns the url_by_name value for a User from Steam, or None if one cannot
	be created from the profile URL.
	"""
	if profile_url is None:
		return None
	community_id_match = _GET_COMMUNITY_ID_REGEX.search(profile_url)
	if not community_id_match:
		return None
	community_id = community_id_match.group('community_id')
	return _get_steam_url_by_name_from_community_id(community_id)

def _get_twitch_url_by_name(name):
	"""Returns the url_by_name value for a User from Twitch."""
	return _USER_URL_SEPARATOR.join((_USER_URL_TWITCH_PREFIX, name))

def _get_user_url(url_by_id, url_by_name):
	"""Returns the best URL for a given User."""
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

def _get_external_url(url_by_id, url_by_name):
	"""Returns the best external URL for a given User."""
	if url_by_name is not None:
		prefix, remainder = url_by_name.split(_USER_URL_SEPARATOR, 1)
		if prefix == _USER_URL_STEAM_PREFIX:
			# The remainder is the Steam community identifier.
			return 'http://steamcommunity.com/id/%s' % remainder
		elif prefix == _USER_URL_TWITCH_PREFIX:
			# The remainder is the Twitch user name.
			return 'http://twitch.tv/%s' % remainder
		else:
			raise ValueError('Invalid url_by_name=%s' % url_by_name)

	prefix, remainder = url_by_id.split(_USER_URL_SEPARATOR, 1)
	if prefix == _USER_URL_STEAM_PREFIX:
		# The remainder is the Steam identifier.
		return 'http://steamcommunity.com/profiles/%s' % remainder
	else:
		raise ValueError('Invalid url_by_id=%s' % url_by_id)


def _remove_equal_url_by_name(user_class, users_table, url_by_name, user_id):
	"""If another user has the same url_by_name value, clear it; the user logging
	in has now "claimed ownership" of it.
	"""

	if url_by_name is not None:
		# The url_by_name must be unique.
		update_statement = users_table.update().where(user_class.url_by_name == url_by_name)
		if user_id is not None:
			update_statement = update_statement.where(user_class.id != user_id)
		session.execute(update_statement.values({user_class.url_by_name: None}))

@close_session
def twitch_user_logged_in(user_class, users_table,
		twitch_id, name, display_name, logo, access_token,
		user_class_extra_kwargs={}, now=None):
	"""Called whenever a Twitch user has been authenticated and logged in.

	The following parameters are provided by the Twitch API:
	* twitch_id: The user's unique numerical identifier by Twitch.
	* name: The user's unique username on Twitch.
	* display_name: A capitalized variant of the username.
	* logo: The profile picture of the user on Twitch.
	* access_token: The access token returned after authenticating the user on Twitch.
	"""
	now = _get_now(now)
	url_by_name = _get_twitch_url_by_name(name)
	try:
		twitch_user, user = session.query(TwitchUser, user_class)\
				.join(user_class, TwitchUser.user_id == user_class.id)\
				.filter(TwitchUser.twitch_id == twitch_id).one()
		_remove_equal_url_by_name(user_class, users_table, url_by_name, user.id)
		user.name = display_name
		user.image_url_large = logo
		user.last_seen = now
		user.url_by_name = url_by_name
		session.add(user)
		user_id = user.id

	except sa_orm.exc.NoResultFound:
		_remove_equal_url_by_name(user_class, users_table, url_by_name, None)
		twitch_user = TwitchUser(twitch_id=twitch_id)
		user = user_class(
				name=display_name,
				image_url_large=logo,
				last_seen=now,
				url_by_name=url_by_name,
				created=now,
				url_by_id=_get_twitch_url_by_id(twitch_id),
				**user_class_extra_kwargs)
		session.add(user)
		session.flush()
		user_id = user.id
		twitch_user.user_id = user_id

	# Update the TwitchUser.
	twitch_user.name = name
	twitch_user.access_token = access_token
	session.add(twitch_user)
	session.commit()
	return user_id

@close_session
def steam_user_logged_in(user_class, users_table,
		steam_id, personaname, profile_url, avatar, avatar_full,
		user_class_extra_kwargs={}, now=None):
	"""Called whenever a Steam user has been authenticated and logged in.

	The following parameters are provided by the Steam Web API:
	* steam_id: The user's unique 64-bit Steam identifier.
	* personaname: The user's optional, but unique, display name on Steam.
	* profile_url: The unique URL of the user's Steam Community profile.
	* avatar: The small picture on the user's Steam Community profile.
	* avatar_full: The large picture on the user's Steam Community profile.
	"""
	now = _get_now(now)
	url_by_name = _get_steam_url_by_name_from_profile_url(profile_url)
	try:
		steam_user, user = session.query(SteamUser, user_class)\
				.join(user_class, SteamUser.user_id == user_class.id)\
				.filter(SteamUser.steam_id == steam_id).one()
		_remove_equal_url_by_name(user_class, users_table, url_by_name, user.id)
		user.name = personaname
		user.image_url_small = avatar
		user.image_url_large = avatar_full
		user.last_seen = now
		user.url_by_name = url_by_name
		session.add(user)
		user_id = user.id
		
	except sa_orm.exc.NoResultFound:
		_remove_equal_url_by_name(user_class, users_table, url_by_name, None)
		steam_user = SteamUser(steam_id=steam_id)
		user = user_class(name=personaname,
				image_url_small=avatar,
				image_url_large=avatar_full,
				last_seen=now,
				url_by_name=url_by_name,
				created=now,
				url_by_id=_get_steam_url_by_id(steam_id),
				**user_class_extra_kwargs)
		session.add(user)
		session.flush()
		user_id = user.id
		steam_user.user_id = user_id
	
	# Update the SteamUser.
	steam_user.profile_url = profile_url
	session.add(steam_user)
	session.commit()
	return user_id


def _get_now(now):
	if now is None:
		return datetime.utcnow()
	return now

def optional_one(query):
	"""Like calling one() on query, but returns None instead of raising
	NoResultFound.
	"""
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

