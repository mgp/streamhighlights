from datetime import datetime
import re
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
	playlists = sa_orm.relationship('Playlist', backref='user')
	bookmarks = sa_orm.relationship('Bookmark', backref='user')

	def __repr__(self):
		return 'User(id=%r, name=%r, image_url_small=%r, image_url_large=%r, created=%r, last_seen=%r, url_by_id=%r, url_by_name=%r, steam_user=%r, twitch_user=%r, playlists=%r, bookmarks=%r)' % (
				self.id,
				self.name,
				self.image_url_small,
				self.image_url_large,
				self.created.isoformat(),
				self.last_seen.isoformat() if self.last_seen else None,
				self.url_by_id,
				self.url_by_name,
				self.steam_user,
				self.twitch_user,
				self.playlists,
				self.bookmarks)


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


"""The association from playlists to their contained bookmarks.
"""
class PlaylistBookmark(_Base):
	__tablename__ = 'PlaylistBookmarks'

	playlist_id = sa.Column(sa.Integer, sa.ForeignKey('Playlists.id'), primary_key=True)
	bookmark_id = sa.Column(sa.Integer, sa.ForeignKey('Bookmarks.id'), primary_key=True)
	added = sa.Column(sa.DateTime, nullable=False)

	bookmark = sa_orm.relationship('Bookmark')

	def __repr__(self):
		return 'PlaylistBookmark(playlist_id=%r, bookmark_id=%r, added=%r)' % (
				self.playlist_id,
				self.bookmark_id,
				self.added)


"""A playlist of videos by a user.
"""
class Playlist(_Base):
	__tablename__ = 'Playlists'

	id = sa.Column(sa.Integer, primary_key=True)
	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'))
	visibility = sa.Column(sa.Enum('public', 'private'), nullable=False)
	title = sa.Column(sa.String, nullable=False)
	num_thumbs_up = sa.Column(sa.Integer, default=0, nullable=False)
	num_thumbs_down = sa.Column(sa.Integer, default=0, nullable=False)
	created = sa.Column(sa.DateTime, nullable=False)
	updated = sa.Column(sa.DateTime, nullable=False)
	num_bookmarks = sa.Column(sa.Integer, default=0, nullable=False)

	votes = sa_orm.relationship('PlaylistVote', backref='playlist')
	bookmarks = sa_orm.relationship('PlaylistBookmark', backref='Playlist')

	def __repr__(self):
		# Has backref: user.
		return 'Playlist(id=%r, visibility=%r, title=%r, num_thumbs_up=%r, num_thumbs_down=%r, created=%r, updated=%r, num_bookmarks=%r, votes=%r, bookmarks=%r)' % (
				self.id,
				self.visibility,
				self.title,
				self.num_thumbs_up,
				self.num_thumbs_down,
				self.created,
				self.updated,
				self.num_bookmarks,
				self.votes,
				self.bookmarks)


"""Enums for thumbs up and thumbs down votes by the user."""
_THUMB_UP_VOTE = 'thumb_up'
_THUMB_DOWN_VOTE = 'thumb_down'

"""A vote by a user for a playlist.
"""
class PlaylistVote(_Base):
	__tablename__ = 'PlaylistVotes'

	# TODO: make (user_id, playlist_id) primary key?
	id = sa.Column(sa.Integer, primary_key=True)
	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'))
	playlist_id = sa.Column(sa.Integer, sa.ForeignKey('Playlists.id'))
	vote = sa.Column(sa.Enum(_THUMB_UP_VOTE, _THUMB_DOWN_VOTE), nullable=False)
	created = sa.Column(sa.DateTime, nullable=False)

	user = sa_orm.relationship('User')

	def __repr__(self):
		# Has backref: playlist.
		return 'PlaylistVote(id=%r, vote=%r, created=%r, user=%r)' % (
				self.id,
				self.vote,
				self.created,
				self.user)


"""A video.
"""
class Video(_Base):
	__tablename__ = 'Videos'

	id = sa.Column(sa.Integer, primary_key=True)
	title = sa.Column(sa.String, nullable=False)
	length = sa.Column(sa.Integer, nullable=False)
	bookmarks = sa_orm.relationship("Bookmark", backref='video')

	twitch_video = sa_orm.relationship('TwitchVideo', uselist=False, backref='video')

	def __repr__(self):
		return 'Video(id=%r, title=%r, length=%r, bookmarks=%r, twitch_video=%r)' % (
				self.id,
				self.title,
				self.length,
				self.bookmarks,
				self.twitch_video)


"""A video on Twitch.
"""
class TwitchVideo(_Base):
	__tablename__ = 'TwitchVideos'

	id = sa.Column(sa.Integer, primary_key=True)
	video_id = sa.Column(sa.Integer, sa.ForeignKey('Videos.id'))
	archive_id = sa.Column(sa.Integer, nullable=False)
	video_file_url = sa.Column(sa.String, nullable=False)
	link_url = sa.Column(sa.String, nullable=False)

	def __repr__(self):
		# Has backref: video.
		return 'TwitchVideo(id=%r, video_id=%r, archive_id=%r, video_file_url=%r, link_url=%r)' % (
				self.id,
				self.video_id,
				self.archive_id,
				self.video_file_url,
				self.link_url)


"""A bookmark for a video.
"""
class Bookmark(_Base):
	__tablename__ = 'Bookmarks'

	id = sa.Column(sa.Integer, primary_key=True)
	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'))
	video_id = sa.Column(sa.Integer, sa.ForeignKey('Videos.id'))
	comment = sa.Column(sa.String, nullable=False)
	time = sa.Column(sa.Integer, nullable=False)
	created = sa.Column(sa.DateTime, nullable=False)
	num_thumbs_up = sa.Column(sa.Integer, default=0, nullable=False)
	num_thumbs_down = sa.Column(sa.Integer, default=0, nullable=False)

	votes = sa_orm.relationship('BookmarkVote', backref='bookmark')

	def __repr__(self):
		# Has backrefs: user, video.
		return 'Bookmark(id=%r, comment=%r, time=%r, created=%r, num_thumbs_up=%r, num_thumbs_down=%r, votes=%r)' % (
				self.id,
				self.comment,
				self.time,
				self.created.isoformat(),
				self.num_thumbs_up,
				self.num_thumbs_down,
				self.votes)


"""A vote by a user for a bookmark.
"""
class BookmarkVote(_Base):
	__tablename__ = 'BookmarkVotes'

	# TODO: make (user_id, bookmark_id) primary key?
	id = sa.Column(sa.Integer, primary_key=True)
	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'))
	bookmark_id = sa.Column(sa.Integer, sa.ForeignKey('Bookmarks.id'))
	created = sa.Column(sa.DateTime, nullable=False)
	vote = sa.Column(sa.Enum(_THUMB_UP_VOTE, _THUMB_DOWN_VOTE), nullable=False)

	user = sa_orm.relationship('User')

	def __repr__(self):
		# Has backref: bookmark.
		return 'PlaylistVote(id=%r, vote=%r, created=%r, user=%r)' % (
				self.id,
				self.vote,
				self.created,
				self.user)


def create_all():
	global Users
	global SteamUsers
	global TwitchUsers
	global Playlists
	global PlaylistVotes
	global PlaylistBookmarks
	global Videos
	global TwitchVideos
	global Bookmarks
	global BookmarkVotes

	_Base.metadata.create_all(_engine)

	# Create aliases for each table.
	Users = User.__table__
	SteamUsers = SteamUser.__table__
	TwitchUsers = TwitchUser.__table__
	Playlists = Playlist.__table__
	PlaylistVotes = PlaylistVote.__table__
	PlaylistBookmarks = PlaylistBookmark.__table__
	Videos = Video.__table__
	TwitchVideos = TwitchVideo.__table__
	Bookmarks = Bookmark.__table__
	BookmarkVotes = BookmarkVote.__table__

def drop_all():
	global Users
	global SteamUsers
	global TwitchUsers
	global Playlists
	global PlaylistVotes
	global PlaylistBookmarks
	global Videos
	global TwitchVideos
	global Bookmarks
	global BookmarkVotes

	# Clear aliases for each table.
	Users = None
	SteamUsers = None
	TwitchUsers = None
	Playlists = None
	PlaylistVotes = None
	PlaylistBookmarks = None
	Videos = None
	TwitchVideos = None
	Bookmarks = None
	BookmarkVotes = None

	_Base.metadata.drop_all(_engine)

def _get_now(now):
	if now is None:
		return datetime.utcnow()
	return now

"""Adds the given video on Twitch.
"""
def add_twitch_video(title, length, archive_id, video_file_url, link_url):
	video = Video(title=title, length=length)
	twitch_video = TwitchVideo(
			archive_id=archive_id, video_file_url=video_file_url, link_url=link_url)
	twitch_video.video = video
	session.add(twitch_video)
	session.commit()
	# Return the video identifier for referencing by playlists and bookmarks.
	return video.id


"""Data for displaying a user.
"""
class DisplayedUser:
	# TODO: Add in site_url?
	def __init__(self, id, name, image_url_small, image_url_large, playlists):
		self.id = id
		self.name = name
		self.image_url_small = image_url_small
		self.image_url_large = image_url_large
		# The DisplayedUserPlaylist objects for each playlist.
		self.playlists = playlists
	
	def __repr__(self):
		return 'DisplayedUser(id=%r, name=%r, image_url_small=%r, image_url_large=%r, playlists=%r)' % (
				self.id,
				self.name,
				self.image_url_small,
				self.image_url_large,
				self.playlists)


"""Data for displaying a user on Twitch.
"""
class DisplayedTwitchUser(DisplayedUser):
	def __init__(self, id, name, image_url_small, image_url_large, playlists, twitch_id, link_url):
		DisplayedUser.__init__(self, id, name, image_url_small, image_url_large, playlists)
		self.twitch_id = twitch_id
		# The URL to this user on Twitch.
		self.link_url = link_url
	
	def __repr__(self):
		return 'DisplayedTwitchUser(id=%r, name=%r, image_url_small=%r, image_url_large=%r, playlists=%r, twitch_id=%r, link_url=%r)' % (
				self.id,
				self.name,
				self.image_url_small,
				self.image_url_large,
				self.playlists,
				self.twitch_id,
				self.link_url)


"""Data for displaying a user on Steam.
"""
class DisplayedSteamUser(DisplayedUser):
	def __init__(self, id, name, image_url_large, image_url_small, playlists, steam_id, link_url):
		DisplayedUser.__init__(self, id, name, image_url_large, image_url_small, playlists)
		# The 64-bit Steam identifier for this user.
		self.steam_id = steam_id
		# The URL to this user on Steam Community, either with a Steam ID or persona name.
		self.link_url = link_url
	
	def __repr__(self):
		return 'DisplayedSteamUser(id=%r, name=%r, image_url_small=%r, image_url_large=%r, playlists=%r, steam_id=%r, link_url=%r)' % (
				self.id,
				self.name,
				self.image_url_small,
				self.image_url_large,
				self.playlists,
				self.steam_id,
				self.link_url)


"""Data for displaying a playlist on a user page.
"""
class DisplayedUserPlaylist:
	def __init__(self, id, time_created, time_updated, num_thumbs_up, num_thumbs_down, user_vote, title, num_bookmarks):
		self.id = id
		self.time_created = time_created
		self.time_updated = time_updated
		self.num_thumbs_up = num_thumbs_up
		self.num_thumbs_down = num_thumbs_down
		self.user_vote = user_vote
		self.title = title
		self.num_bookmarks = num_bookmarks
	
	def __repr__(self):
		return 'DisplayedUserPlaylist(id=%r, time_created=%r, time_updated=%r, num_thumbs_up=%r, num_thumbs_down=%r, user_vote=%r, title=%r, num_bookmarks=%r)' % (
				self.id,
				self.time_created,
				self.time_updated,
				self.num_thumbs_up,
				self.num_thumbs_down,
				self.user_vote,
				self.title,
				self.num_bookmarks)

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

def _remove_equal_url_by_name(url_by_name, user_id):
	if url_by_name is not None:
		# The url_by_name must be unique.
		update_statement = Users.update().where(User.url_by_name == url_by_name)
		if user_id is not None:
			update_statement = update_statement.where(User.id != user_id)
		session.execute(update_statement.values({User.url_by_name: None}))

"""Called whenever a Twitch user has been authenticated and logged in.
"""
def twitch_user_logged_in(twitch_id, name, display_name, logo, access_token, now=None):
	now = _get_now(now)
	url_by_name = _get_twitch_url_by_name(name)
	try:
		twitch_user = session.query(TwitchUser)\
				.options(sa_orm.joinedload(TwitchUser.user))\
				.filter(TwitchUser.twitch_id == twitch_id).one()
		_remove_equal_url_by_name(url_by_name, twitch_user.user.id)
	except sa_orm.exc.NoResultFound:
		_remove_equal_url_by_name(url_by_name, None)
		twitch_user = TwitchUser(twitch_id=twitch_id)
		twitch_user.user = User(created=now, url_by_id=_get_twitch_url_by_id(twitch_id))
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
def steam_user_logged_in(steam_id, personaname, profile_url, avatar, avatar_full, now=None):
	now = _get_now(now)
	url_by_name = _get_steam_url_by_name_from_profile_url(profile_url)
	try:
		steam_user = session.query(SteamUser)\
				.options(sa_orm.joinedload(SteamUser.user))\
				.filter(SteamUser.steam_id == steam_id).one()
		_remove_equal_url_by_name(url_by_name, steam_user.user.id)
	except sa_orm.exc.NoResultFound:
		_remove_equal_url_by_name(url_by_name, None)
		steam_user = SteamUser(steam_id=steam_id)
		steam_user.user = User(created=now, url_by_id=_get_steam_url_by_id(steam_id))
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


def _get_displayed_user_playlists(client_id, user_id):
	if client_id is None:
		# Get the playlists.
		playlists_cursor = session.query(Playlist)\
				.filter(Playlist.user_id == user_id)
		session.close()

		# Create the displayed playlist and number of bookmarks.
		displayed_user_playlists = [
				DisplayedUserPlaylist(
					id=playlist.id,
					time_created=playlist.created,
					time_updated=playlist.updated,
					num_thumbs_up=playlist.num_thumbs_up,
					num_thumbs_down=playlist.num_thumbs_down,
					user_vote=None,
					title=playlist.title,
					num_bookmarks=playlist.num_bookmarks)
				for playlist in playlists_cursor]
	else:
		# Get the playlists with the client's vote for each one.
		playlists_cursor = session.query(Playlist, PlaylistVote.vote)\
				.outerjoin(PlaylistVote, sa.and_(
					PlaylistVote.user_id == client_id,
					PlaylistVote.playlist_id == Playlist.id))\
				.filter(Playlist.user_id == user_id)
		session.close()

		# Create the displayed playlist and number of bookmarks.
		displayed_user_playlists = [
				DisplayedUserPlaylist(
					id=playlist.id,
					time_created=playlist.created,
					time_updated=playlist.updated,
					num_thumbs_up=playlist.num_thumbs_up,
					num_thumbs_down=playlist.num_thumbs_down,
					user_vote=playlist_vote,
					title=playlist.title,
					num_bookmarks=playlist.num_bookmarks)
				for playlist, playlist_vote in playlists_cursor]

	return displayed_user_playlists


def _get_displayed_twitch_user(client_id, filter_expression):
	try:
		# Get the Twitch user.
		twitch_user, user = session.query(TwitchUser, User)\
				.join(User, TwitchUser.user_id == User.id)\
				.filter(filter_expression).one()
	except sa_orm.exc.NoResultFound:
		session.close()
		raise DbException._chain()

	displayed_user_playlists = _get_displayed_user_playlists(client_id, user.id)
	link_url = 'http://www.twitch.tv/%s' % twitch_user.name
	displayed_twitch_user = DisplayedTwitchUser(
			user.id,
			user.name,
			user.image_url_small,
			user.image_url_large,
			displayed_user_playlists,
			twitch_user.twitch_id,
			link_url)
	return displayed_twitch_user

"""Returns the DisplayedTwitchUser with the given name.
"""
def get_displayed_twitch_user_by_name(client_id, name):
	url_by_name = _get_twitch_url_by_name(name)
	filter_expression = (User.url_by_name == url_by_name)
	return _get_displayed_twitch_user(client_id, filter_expression)

"""Returns the DisplayedTwitchUser with the given Twitch identifier.
"""
def get_displayed_twitch_user_by_id(client_id, twitch_id):
	filter_expression = (TwitchUser.twitch_id == twitch_id)
	return _get_displayed_twitch_user(client_id, filter_expression)


def _get_displayed_steam_user(client_id, filter_expression):
	try:
		# Get the Steam user.
		steam_user, user = session.query(SteamUser, User)\
			.join(User, SteamUser.user_id == User.id)\
			.filter(filter_expression).one()
	except sa_orm.exc.NoResultFound:
		session.close()
		raise DbException._chain()

	displayed_user_playlists = _get_displayed_user_playlists(client_id, user.id)
	if steam_user.profile_url:
		link_url = steam_user.profile_url
	else:
		link_url = 'http://steamcommunity.com/profiles/%s' % steam_user.steam_id
	displayed_steam_user = DisplayedSteamUser(
			user.id,
			user.name,
			user.image_url_small,
			user.image_url_large,
			displayed_user_playlists,
			steam_user.steam_id,
			link_url)
	return displayed_steam_user

"""Returns the DisplayedSteamUser with the given name.
"""
def get_displayed_steam_user_by_name(client_id, name):
	url_by_name = _get_steam_url_by_name_from_community_id(name)
	filter_expression = (User.url_by_name == url_by_name)
	return _get_displayed_steam_user(client_id, filter_expression)

"""Returns the DisplayedSteamUser with the given Steam identifier.
"""
def get_displayed_steam_user_by_id(client_id, steam_id):
	filter_expression = (SteamUser.steam_id == steam_id)
	return _get_displayed_steam_user(client_id, filter_expression)


"""Creates a playlist by the given user.
"""
def create_playlist(client_id, title, now=None):
	if session.query(User).filter(User.id == client_id).count() == 0:
		session.close()
		raise DbException('User not found: %s' % client_id)

	now = _get_now(now)
	playlist = Playlist(
			user_id=client_id, visibility='public', title=title, created=now, updated=now)
	session.add(playlist)
	session.commit()
	return playlist.id

"""Deletes the playlist with the given identifier.
"""
def remove_playlist(client_id, playlist_id, now=None):
	result = session.execute(
			Playlists.delete().where(
				sa.and_(Playlist.id == playlist_id, Playlist.user_id == client_id)))
	if result.rowcount:
		session.commit()
	else:
		session.rollback()
		raise DbException('Playlist not found: %s, User not found: %s' % (playlist_id, client_id))


"""Data for displaying a playlist.
"""
class DisplayedPlaylist:
	def __init__(self, author_name, author_image_url_large, author_url, time_created, time_updated, num_thumbs_up, num_thumbs_down, user_vote, title, bookmarks):
		self.author_name = author_name
		self.author_image_url_large = author_image_url_large
		self.author_url = author_url
		self.time_created = time_created
		self.time_updated = time_updated
		self.num_thumbs_up = num_thumbs_up
		self.num_thumbs_down = num_thumbs_down
		self.user_vote = user_vote
		self.title = title
		# The DisplayedPlaylistBookmark objects for each bookmark.
		self.bookmarks = bookmarks

	def __repr__(self):
		return 'DisplayedPlaylist(author_name=%r, author_image_url_large=%r, author_url=%r, time_created=%r, time_updated=%r, num_thumbs_up=%r, num_thumbs_down=%r, user_vote=%r, title=%r, bookmarks=%r)' % (
				self.author_name,
				self.author_image_url_large,
				slef.author_url,
				self.time_created,
				self.time_updated,
				self.num_thumbs_up,
				self.num_thumbs_down,
				self.user_vote,
				self.title,
				self.bookmarks)


"""Data for displaying a bookmark on a playlist page.
"""
class DisplayedPlaylistBookmark:
	def __init__(self, id, num_thumbs_up, num_thumbs_down, user_vote, video_title, comment, time_added, author_name, author_image_url_small, author_url):
		self.id = id
		self.num_thumbs_up = num_thumbs_up
		self.num_thumbs_down = num_thumbs_down
		self.user_vote = user_vote
		self.video_title = video_title
		self.comment = comment
		self.time_added = time_added
		# The author's info.
		self.author_name = author_name
		self.author_image_url_small = author_image_url_small
		self.author_url = author_url
	
	def __repr__(self):
		return 'DisplayedPlaylistBookmark(id=%r, num_thumbs_up=%r, num_thumbs_down=%r, user_vote=%r, video_title=%r, comment=%r, time_added=%r, author_name=%r, author_image_url_small=%r, author_url=%r)' % (
				self.id,
				self.num_thumbs_up,
				self.num_thumbs_down,
				self.user_vote,
				self.video_title,
				self.comment,
				self.time_added,
				self.author_name,
				self.author_image_url_small,
				self.author_url)


"""Returns the DisplayedPlaylist with the given identifier.
"""
def get_displayed_playlist(client_id, playlist_id):
	playlist_vote = None
	if client_id is None:
		try:
			# Get the playlist.
			playlist, creator_name, creator_url_by_id, creator_url_by_name = session.query(
						Playlist, User.name, User.url_by_id, User.url_by_name)\
					.join(User, Playlist.user_id == User.id)\
					.filter(Playlist.id == playlist_id)\
					.one()
		except sa_orm.exc.NoResultFound:
			session.close()
			raise DbException._chain()

		# Get the bookmarks.
		playlist_bookmarks_cursor = session.query(
					PlaylistBookmark.added, Bookmark,
					User.name, User.url_by_id, User.url_by_name, Video.title)\
				.join(Bookmark, PlaylistBookmark.bookmark_id == Bookmark.id)\
				.join(User, Bookmark.user_id == User.id)\
				.join(Video, Bookmark.video_id == Video.id)\
				.filter(PlaylistBookmark.playlist_id == playlist_id)
		session.close()

		# Create the displayed bookmarks.
		displayed_playlist_bookmarks = [
				DisplayedPlaylistBookmark(
					id=bookmark.id,
					num_thumbs_up=bookmark.num_thumbs_up,
					num_thumbs_down=bookmark.num_thumbs_down,
					user_vote=None,
					video_title=video_title,
					comment=bookmark.comment,
					time_added=added,
					author_name=author_name,
					author_image_url_small=None,
					author_url=_get_user_url(author_url_by_id, author_url_by_name))
				for added, bookmark, author_name, author_url_by_id, author_url_by_name, video_title
					in playlist_bookmarks_cursor]
	else:
		try:
			# Get the playlist with the client's vote.
			(playlist, creator_name,
					creator_url_by_id, creator_url_by_name, playlist_vote) = session.query(
						Playlist, User.name, User.url_by_id, User.url_by_name, PlaylistVote.vote)\
					.join(User, Playlist.user_id == User.id)\
					.outerjoin(PlaylistVote, sa.and_(
						PlaylistVote.user_id == client_id,
						PlaylistVote.playlist_id == Playlist.id))\
					.filter(Playlist.id == playlist_id)\
					.one()
		except sa_orm.exc.NoResultFound:
			session.close()
			raise DbException._chain()

		# Get the bookmarks with the client's vote for each one.
		playlist_bookmarks_cursor = session.query(
					PlaylistBookmark.added, Bookmark,
					User.name, User.url_by_id, User.url_by_name, Video.title, BookmarkVote.vote)\
				.join(Bookmark, PlaylistBookmark.bookmark_id == Bookmark.id)\
				.join(User, Bookmark.user_id == User.id)\
				.join(Video, Bookmark.video_id == Video.id)\
				.outerjoin(BookmarkVote, sa.and_(
					BookmarkVote.user_id == client_id,
					BookmarkVote.bookmark_id == Bookmark.id))\
				.filter(PlaylistBookmark.playlist_id == playlist_id)
		session.close()

		# Create the displayed bookmarks.
		displayed_playlist_bookmarks = [
				DisplayedPlaylistBookmark(
					id=bookmark.id,
					num_thumbs_up=bookmark.num_thumbs_up,
					num_thumbs_down=bookmark.num_thumbs_down,
					user_vote=bookmark_vote,
					video_title=video_title,
					comment=bookmark.comment,
					time_added=added,
					author_name=author_name,
					author_image_url_small=None,
					author_url=_get_user_url(author_url_by_id, author_url_by_name))
				for added, bookmark,
					author_name, author_url_by_id, author_url_by_name, video_title, bookmark_vote
						in playlist_bookmarks_cursor]

	# Create the displayed playlist.
	displayed_playlist = DisplayedPlaylist(
			author_name=creator_name,
			author_image_url_large=None,
			author_url=_get_user_url(creator_url_by_id, creator_url_by_name),
			time_created=playlist.created,
			time_updated=playlist.updated,
			num_thumbs_up=playlist.num_thumbs_up,
			num_thumbs_down=playlist.num_thumbs_down,
			user_vote=playlist_vote,
			title=playlist.title,
			bookmarks=displayed_playlist_bookmarks)
	return displayed_playlist

"""Adds the bookmark with the given identifier to the given playlist.
"""
def add_playlist_bookmark(client_id, playlist_id, bookmark_id, now=None):
	missing = session.query(Playlist, Bookmark)\
			.join(Bookmark, Bookmark.id == bookmark_id)\
			.filter(Playlist.id == playlist_id, Playlist.user_id == client_id)\
			.count() == 0
	if missing:
		session.close()
		raise DbException('Playlist not found: %s, User not found: %s' % (playlist_id, client_id))
	
	try:
		now = _get_now(now)
		# Add the bookmark to the playlist.
		playlist_bookmark = PlaylistBookmark(
				playlist_id=playlist_id, bookmark_id=bookmark_id, added=now)
		session.add(playlist_bookmark)
		# Increment the count of bookmarks for the playlist.
		session.execute(Playlists.update()
				.where(sa.and_(Playlist.id == playlist_id, Playlist.user_id == client_id))
				.values({
					Playlist.num_bookmarks: Playlist.num_bookmarks + 1,
					Playlist.updated: now}))
		session.commit()
	except sa.exc.IntegrityError:
		# The commit failed because this bookmark is already part of the playlist.
		session.rollback()

"""Removes the bookmark with the given identifier from the given playlist.
"""
def remove_playlist_bookmark(client_id, playlist_id, bookmark_id, now=None):
	missing = session.query(Playlist)\
			.filter(Playlist.id == playlist_id, Playlist.user_id == client_id)\
			.count() == 0
	if missing:
		session.close()
		raise DbException('Playlist not found: %s, User not found: %s' % (playlist_id, client_id))

	# Remove the bookmark from the playlist.
	result = session.execute(PlaylistBookmarks.delete().where(sa.and_(
			PlaylistBookmark.playlist_id == playlist_id,
			PlaylistBookmark.bookmark_id == bookmark_id)))
	if result.rowcount:
		# Decrement the count of bookmarks for the playlist.
		now = _get_now(now)
		session.execute(Playlists.update()
				.where(Playlist.id == playlist_id)
				.values({
					Playlist.num_bookmarks: Playlist.num_bookmarks - 1,
					Playlist.updated: now}))
		session.commit()
	else:
		session.rollback()

"""Votes up the playlist with the given identifier.
"""
def vote_playlist_thumb_up(client_id, playlist_id, now=None):
	try:
		playlist_user_id, vote = session.query(Playlist.user_id, PlaylistVote)\
				.outerjoin(PlaylistVote, sa.and_(
					PlaylistVote.user_id == client_id,
					PlaylistVote.playlist_id == Playlist.id))\
				.filter(Playlist.id == playlist_id)\
				.one()
	except sa_orm.exc.NoResultFound:
		session.close()
		raise DbException._chain()

	# Do not allow the creator to vote up his own playlist.
	if playlist_user_id == client_id:
		raise DbException('Client is playlist owner: %s' % client_id)

	now = _get_now(now)
	if vote is None:
		# Create the vote by the user.
		vote = PlaylistVote(
				user_id=client_id, playlist_id=playlist_id, vote=_THUMB_UP_VOTE, created=now)
		# Update the count of thumbs up for the playlist.
		session.execute(Playlists.update()
				.where(Playlist.id == playlist_id)
				.values({Playlist.num_thumbs_up: Playlist.num_thumbs_up + 1}))
	elif vote.vote == _THUMB_DOWN_VOTE:
		# Change the vote by the user.
		vote.vote = _THUMB_UP_VOTE
		vote.created = now
		# Update the counts of thumbs up and thumbs down for the playlist.
		session.execute(Playlists.update()
				.where(Playlist.id == playlist_id)
				.values({Playlist.num_thumbs_up: Playlist.num_thumbs_up + 1,
					Playlist.num_thumbs_down: Playlist.num_thumbs_down - 1}))
	else:
		session.close()
		return

	try:
		session.add(vote)
		session.commit()
	except sa.exc.IntegrityError:
		session.rollback()
		raise DbException._chain()

"""Votes down the playlist with the given identifier.
"""
def vote_playlist_thumb_down(client_id, playlist_id, now=None):
	try:
		playlist_user_id, vote = session.query(Playlist.user_id, PlaylistVote)\
				.outerjoin(PlaylistVote, sa.and_(
					PlaylistVote.user_id == client_id,
					PlaylistVote.playlist_id == Playlist.id))\
				.filter(Playlist.id == playlist_id)\
				.one()
	except sa_orm.exc.NoResultFound:
		session.close()
		raise DbException._chain()

	# Do not allow the creator to vote down his own playlist.
	if playlist_user_id == client_id:
		raise DbException('Client is playlist owner: %s' % client_id)

	now = _get_now(now)
	if vote is None:
		# Create the vote by the user.
		vote = PlaylistVote(
				user_id=client_id, playlist_id=playlist_id, vote=_THUMB_DOWN_VOTE, created=now)
		# Update the count of thumbs down for the playlist.
		session.execute(Playlists.update()
				.where(Playlist.id == playlist_id)
				.values({Playlist.num_thumbs_down: Playlist.num_thumbs_down + 1}))
	elif vote.vote == _THUMB_UP_VOTE:
		# Change the vote by the user.
		vote.vote = _THUMB_DOWN_VOTE
		vote.created = now
		# Update the counts of thumbs up and thumbs down for the playlist.
		session.execute(Playlists.update()
				.where(Playlist.id == playlist_id)
				.values({Playlist.num_thumbs_down: Playlist.num_thumbs_down + 1,
					Playlist.num_thumbs_up: Playlist.num_thumbs_up - 1}))
	else:
		session.close()
		return

	try:
		session.add(vote)
		session.commit()
	except sa.exc.IntegrityError:
		session.rollback()
		raise DbException._chain()

"""Removes the vote for the playlist with the given identifier.
"""
def remove_playlist_vote(client_id, playlist_id, now=None):
	try:
		vote = session.query(PlaylistVote)\
				.filter(PlaylistVote.user_id == client_id, PlaylistVote.playlist_id == playlist_id)\
				.one()
	except sa_orm.exc.NoResultFound:
		session.close()
		raise DbException._chain()

	if vote.vote == _THUMB_UP_VOTE:
		# Update the count of thumbs up for the playlist.
		session.execute(Playlists.update()
				.where(Playlist.id == playlist_id)
				.values({Playlist.num_thumbs_up: Playlist.num_thumbs_up - 1}))
	elif vote.vote == _THUMB_DOWN_VOTE:
		# Update the count of thumbs down for the playlist.
		session.execute(Playlists.update()
				.where(Playlist.id == playlist_id)
				.values({Playlist.num_thumbs_down: Playlist.num_thumbs_down - 1}))

	session.delete(vote)
	session.commit()


"""Data for displaying a video.
"""
class DisplayedVideo:
	def __init__(self, id, title, length, bookmarks):
		self.id = id
		self.title = title
		self.length = length
		# The DisplayedBookmark objects for each bookmark.
		self.bookmarks = bookmarks
	
	def __repr__(self):
		return 'DisplayedVideo(id=%r, title=%r, length=%r, bookmarks=%r)' % (
				self.id,
				self.title,
				self.length,
				self.bookmarks)


"""Data for displaying a video on Twitch.
"""
class DisplayedTwitchVideo(DisplayedVideo):
	def __init__(self, id, title, length, bookmarks, archive_id, video_file_url, link_url):
		DisplayedVideo.__init__(self, id, title, length, bookmarks)
		self.archive_id = archive_id
		self.video_file_url = video_file_url
		self.link_url = link_url
	
	def __repr__(self):
		return 'DisplayedTwitchVideo(id=%r, title=%r, length=%r, bookmarks=%r, archive_id=%r, video_file_url=%r, link_url=%r)' % (
				self.id,
				self.title,
				self.length,
				self.bookmarks,
				self.archive_id,
				self.video_file_url,
				self.link_url)


"""Data for displaying a bookmark on a video page.
"""
class DisplayedVideoBookmark:
	def __init__(self, id, num_thumbs_up, num_thumbs_down, user_vote, comment, time, time_created,
			author_name, author_image_url_small, author_url):
		self.id = id
		self.num_thumbs_up = num_thumbs_up
		self.num_thumbs_down = num_thumbs_down
		self.user_vote = user_vote
		self.comment = comment
		# The bookmarked time.
		self.time = time
		# The time to bookmark was created.
		self.time_created = time_created
		# The author's info.
		self.author_name = author_name
		self.author_image_url_small = author_image_url_small
		self.author_url = author_url

	def __repr__(self):
		return 'DisplayedBookmark(id=%r, num_thumbs_up=%r, num_thumbs_down=%r, user_vote=%r, comment=%r, time=%r, time_created=%r, author_name=%r, author_image_url_small=%r, author_url)' % (
				self.id,
				self.num_thumbs_up,
				self.num_thumbs_down,
				self.user_vote,
				self.comment,
				self.time,
				self.time_created,
				self.author_name,
				self.author_image_url_small,
				self.author_url)


"""Returns the DisplayedVideo with the given identifier.
"""
def get_displayed_twitch_video(client_id, archive_id):
	try:
		# Get the video.
		twitch_video, video = session.query(TwitchVideo, Video)\
				.join(Video, TwitchVideo.video_id == Video.id)\
				.filter(TwitchVideo.archive_id == archive_id).one()
	except sa_orm.exc.NoResultFound:
		session.close()
		raise DbException._chain()

	if client_id is None:
		# Get the bookmarks.
		video_bookmarks_cursor = session.query(
					Bookmark, User.name, User.url_by_id, User.url_by_name)\
				.join(User, Bookmark.user_id == User.id)\
				.filter(Bookmark.video_id == video.id)
		session.close()

		# Create the displayed bookmarks.
		displayed_video_bookmarks = [
				DisplayedVideoBookmark(
					id=bookmark.id,
					num_thumbs_up=bookmark.num_thumbs_up,
					num_thumbs_down=bookmark.num_thumbs_down,
					user_vote=None,
					comment=bookmark.comment,
					time=bookmark.time,
					time_created=bookmark.created,
					author_name=author_name,
					author_image_url_small=None,
					author_url=_get_user_url(author_url_by_id, author_url_by_name))
				for bookmark, author_name, author_url_by_id, author_url_by_name
					in video_bookmarks_cursor]
	else:
		# Get the bookmarks with the client's vote for each one.
		video_bookmarks_cursor = session.query(
					Bookmark, User.name, User.url_by_id, User.url_by_name, BookmarkVote.vote)\
				.join(User, Bookmark.user_id == User.id)\
				.outerjoin(BookmarkVote, sa.and_(
					BookmarkVote.user_id == client_id,
					BookmarkVote.bookmark_id == Bookmark.id))\
				.filter(Bookmark.video_id == video.id)
		session.close()

		# Create the displayed bookmarks.
		displayed_video_bookmarks = [
				DisplayedVideoBookmark(
					id=bookmark.id,
					num_thumbs_up=bookmark.num_thumbs_up,
					num_thumbs_down=bookmark.num_thumbs_down,
					user_vote=bookmark_vote,
					comment=bookmark.comment,
					time=bookmark.time,
					time_created=bookmark.created,
					author_name=author_name,
					author_image_url_small=None,
					author_url=_get_user_url(author_url_by_id, author_url_by_name))
				for bookmark, author_name, author_url_by_id, author_url_by_name, bookmark_vote
					in video_bookmarks_cursor]

	# Create the displayed video.
	displayed_video = DisplayedTwitchVideo(
			video.id, video.title, video.length, displayed_video_bookmarks,
			twitch_video.archive_id, twitch_video.video_file_url, twitch_video.link_url)
	return displayed_video

"""Adds a bookmark by the given user for the given video.
"""
def add_video_bookmark(client_id, video_id, comment, time, now=None):
	now = _get_now(now)
	try:
		bookmark = Bookmark(
				user_id=client_id, video_id=video_id, comment=comment, time=time, created=now)
		session.add(bookmark)
		session.commit()
		return bookmark.id
	except sa.exc.IntegrityError: 
		session.rollback()
		raise DbException._chain()

"""Removes the bookmark with the given identifier for the given video.
"""
def remove_video_bookmark(client_id, bookmark_id, now=None):
	result = session.execute(
			Bookmarks.delete().where(
				sa.and_(Bookmark.id == bookmark_id, Bookmark.user_id == client_id)))
	if result.rowcount:
		session.commit()
	else:
		session.rollback()
		raise DbException('Bookmark not found: %s, User not found: %s' % (bookmark_id, client_id))

"""Votes up the bookmark with the given identifier.
"""
def vote_bookmark_thumb_up(client_id, bookmark_id, now=None):
	try:
		bookmark_user_id, vote = session.query(Bookmark.user_id, BookmarkVote)\
				.outerjoin(BookmarkVote, sa.and_(
					BookmarkVote.user_id == client_id,
					BookmarkVote.bookmark_id == Bookmark.id))\
				.filter(Bookmark.id == bookmark_id)\
				.one()
	except sa_orm.exc.NoResultFound:
		session.close()
		raise DbException._chain()

	# Do not allow the creator to vote up his own bookmark.
	if bookmark_user_id == client_id:
		raise DbException('Client is bookmark owner: %s' % client_id)

	now = _get_now(now)
	if vote is None:
		# Create the vote by the user.
		vote = BookmarkVote(
				user_id=client_id, bookmark_id=bookmark_id, vote=_THUMB_UP_VOTE, created=now)
		# Update the count of thumbs up for the bookmark.
		session.execute(Bookmarks.update()
				.where(Bookmark.id == bookmark_id)
				.values({Bookmark.num_thumbs_up: Bookmark.num_thumbs_up + 1}))
	elif vote.vote == _THUMB_DOWN_VOTE:
		# Change the vote by the user.
		vote.vote = _THUMB_UP_VOTE
		vote.created = now
		# Update the counts of thumbs up and thumbs down for the bookmark.
		session.execute(Bookmarks.update()
				.where(Bookmark.id == bookmark_id)
				.values({Bookmark.num_thumbs_up: Bookmark.num_thumbs_up + 1,
					Bookmark.num_thumbs_down: Bookmark.num_thumbs_down - 1}))
	else:
		session.close()
		return

	try:
		session.add(vote)
		session.commit()
	except sa.exc.IntegrityError:
		session.rollback()
		raise DbException._chain()

"""Votes down the bookmark with the given identifier.
"""
def vote_bookmark_thumb_down(client_id, bookmark_id, now=None):
	try:
		bookmark_user_id, vote = session.query(Bookmark.user_id, BookmarkVote)\
				.outerjoin(BookmarkVote, sa.and_(
					BookmarkVote.user_id == client_id,
					BookmarkVote.bookmark_id == Bookmark.id))\
				.filter(Bookmark.id == bookmark_id)\
				.one()
	except sa_orm.exc.NoResultFound:
		session.close()
		raise DbException._chain()

	# Do not allow the creator to vote down his own bookmark.
	if bookmark_user_id == client_id:
		raise DbException('Client is bookmark owner: %s' % client_id)

	now = _get_now(now)
	if vote is None:
		# Create the vote by the user.
		vote = BookmarkVote(
				user_id=client_id, bookmark_id=bookmark_id, vote=_THUMB_DOWN_VOTE, created=now)
		# Update the count of thumbs down for the bookmark.
		session.execute(Bookmarks.update()
				.where(Bookmark.id == bookmark_id)
				.values({Bookmark.num_thumbs_down: Bookmark.num_thumbs_down + 1}))
	elif vote.vote == _THUMB_UP_VOTE:
		# Change the vote by the user.
		vote.vote = _THUMB_DOWN_VOTE
		vote.created = now
		# Update the counts of thumbs up and thumbs down for the bookmark.
		session.execute(Bookmarks.update()
				.where(Bookmark.id == bookmark_id)
				.values({Bookmark.num_thumbs_down: Bookmark.num_thumbs_down + 1,
					Bookmark.num_thumbs_up: Bookmark.num_thumbs_up - 1}))
	else:
		session.close()
		return

	try:
		session.add(vote)
		session.commit()
	except sa.exc.IntegrityError:
		session.rollback()
		raise DbException._chain()

"""Removes the vote for the bookmark with the given identifier.
"""
def remove_bookmark_vote(client_id, bookmark_id, now=None):
	try:
		vote = session.query(BookmarkVote)\
				.filter(BookmarkVote.user_id == client_id, BookmarkVote.bookmark_id == bookmark_id)\
				.one()
	except sa_orm.exc.NoResultFound:
		session.close()
		raise DbException._chain()

	if vote.vote == _THUMB_UP_VOTE:
		# Update the count of thumbs up for the bookmark.
		session.execute(Bookmarks.update()
				.where(Bookmark.id == bookmark_id)
				.values({Bookmark.num_thumbs_up: Bookmark.num_thumbs_up - 1}))
	elif vote.vote == _THUMB_DOWN_VOTE:
		# Update the count of thumbs down for the bookmark.
		session.execute(Bookmarks.update()
				.where(Bookmark.id == bookmark_id)
				.values({Bookmark.num_thumbs_down: Bookmark.num_thumbs_down - 1}))

	session.delete(vote)
	session.commit()

