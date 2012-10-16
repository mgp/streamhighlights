from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.engine as sa_engine
import sqlalchemy.ext.declarative as sa_ext_declarative
import sqlalchemy.orm as sa_orm
import sqlalchemy.schema as sa_schema


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
	created = sa.Column(sa.DateTime, nullable=False)
	last_seen = sa.Column(sa.DateTime)

	steam_user = sa_orm.relationship('SteamUser', uselist=False, backref='user')
	twitch_user = sa_orm.relationship('TwitchUser', uselist=False, backref='user')
	playlists = sa_orm.relationship('Playlist', backref='user')
	bookmarks = sa_orm.relationship('Bookmark', backref='user')

	def __init__(self, name, now):
		self.name = name
		self.created = now
	
	def __repr__(self):
		return 'User(id=%r, name=%r, created=%r, last_seen=%r, steam_user=%r, twitch_user=%r, playlists=%r, bookmarks=%r)' % (
				self.id,
				self.name,
				self.created.isoformat(),
				self.last_seen.isoformat() if self.last_seen else None,
				self.steam_user,
				self.twitch_user,
				self.playlists,
				self.bookmarks)


"""If the user logged in through Steam, the details of that user on Steam.
"""
class SteamUser(_Base):
	__tablename__ = 'SteamUsers'

	# TODO: make (id, user_id) primary key? or user_id primary key and foreign key?
	id = sa.Column(sa.Integer, primary_key=True)
	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'))

	def __init__(self, user_id):
		self.user_id = user_id

	def __repr__(self):
		# Has backref: user.
		return 'SteamUser(id=%r, user=%r)' % (
				self.id,
				self.user)


"""If the user logged in through Twitch, the details of that user on Twitch.
"""
class TwitchUser(_Base):
	__tablename__ = 'TwitchUsers'

	# TODO: make (id, user_id) primary key? or user_id primary key and foreign key?
	id = sa.Column(sa.Integer, primary_key=True)
	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'))

	def __init__(self):
		self.user_id = user_id

	def __repr__(self):
		# Has backref: user.
		return 'TwitchUser(id=%r, user=%r)' % (
				self.id,
				self.user)


"""The association from playlists to their contained bookmarks.
"""
class PlaylistBookmark(_Base):
	__tablename__ = 'PlaylistBookmarks'

	playlist_id = sa.Column(sa.Integer, sa.ForeignKey('Playlists.id'), primary_key=True)
	bookmark_id = sa.Column(sa.Integer, sa.ForeignKey('Bookmarks.id'), primary_key=True)
	added = sa.Column(sa.DateTime, nullable=False)

	bookmark = sa_orm.relationship('Bookmark')

	def __init__(self, playlist_id, bookmark_id, now):
		self.playlist_id = playlist_id
		self.bookmark_id = bookmark_id
		self.added = now

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
	num_thumbs_up = sa.Column(sa.Integer, nullable=False)
	num_thumbs_down = sa.Column(sa.Integer, nullable=False)
	created = sa.Column(sa.DateTime, nullable=False)
	updated = sa.Column(sa.DateTime, nullable=False)
	num_bookmarks = sa.Column(sa.Integer, nullable=False)

	votes = sa_orm.relationship('PlaylistVote', backref='playlist')
	bookmarks = sa_orm.relationship('PlaylistBookmark', backref='Playlist')

	def __init__(self, visibility, title, now, user_id=None):
		if user_id:
			self.user_id = user_id
		self.visibility = visibility
		self.title = title
		self.num_thumbs_up = 0
		self.num_thumbs_down = 0
		self.created = now
		self.updated = now
		self.num_bookmarks = 0
	
	def __repr__(self):
		# Has backref: user.
		return 'Playlist(id=%r, visibility=%r, title=%r, num_thumbs_up=%r, num_thumbs_down=%r, created=%r, updated=%r, num_bookmarks=%r, votes=%r, bookmarks=%r, user=%r)' % (
				self.id,
				self.visibility,
				self.title,
				self.num_thumbs_up,
				self.num_thumbs_down,
				self.created,
				self.updated,
				self.num_bookmarks,
				self.votes,
				self.bookmarks,
				self.user)


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

	def __init__(self, vote, now, user_id=None, playlist_id=None):
		if user_id:
			self.user_id = user_id
		if playlist_id:
			self.playlist_id = playlist_id
		self.vote = vote
		self.created = now
	
	def __repr__(self):
		# Has backref: playlist.
		return 'PlaylistVote(id=%r, vote=%r, created=%r, user=%r, playlist=%r)' % (
				self.id,
				self.vote,
				self.created,
				self.user,
				self.playlist)


"""A video.
"""
class Video(_Base):
	__tablename__ = 'Videos'

	id = sa.Column(sa.Integer, primary_key=True)
	title = sa.Column(sa.String, nullable=False)
	length = sa.Column(sa.Integer, nullable=False)
	bookmarks = sa_orm.relationship("Bookmark", backref='video')

	twitch_video = sa_orm.relationship('TwitchVideo', uselist=False, backref='video')

	def __init__(self, title, length):
		self.title = title
		self.length = length

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
	twitch_id = sa.Column(sa.Integer, sa.ForeignKey('Videos.id'))
	archive_id = sa.Column(sa.String, nullable=False)
	video_file_url = sa.Column(sa.String, nullable=False)
	link_url = sa.Column(sa.String, nullable=False)

	def __init__(self, archive_id, video_file_url, link_url, twitch_id=None):
		if twitch_id is not None:
			self.twitch_id = twitch_id
		self.archive_id = archive_id
		self.video_file_url = video_file_url
		self.link_url = link_url

	def __repr__(self):
		# Has backref: video.
		return 'TwitchVideo(id=%r, twitch_id=%r, archive_id=%r, video_file_url=%r, link_url=%r, video=%r)' % (
				self.id,
				self.twitch_id,
				self.archive_id,
				self.video_file_url,
				self.link_url,
				self.video)


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
	num_thumbs_up = sa.Column(sa.Integer, nullable=False)
	num_thumbs_down = sa.Column(sa.Integer, nullable=False)

	votes = sa_orm.relationship('BookmarkVote', backref='bookmark')

	def __init__(self, comment, time, now, user_id=None, video_id=None):
		if user_id:
			self.user_id = user_id
		if video_id:
			self.video_id = video_id
		self.comment = comment
		self.time = time
		self.created = now
		self.num_thumbs_up = 0
		self.num_thumbs_down = 0

	def __repr__(self):
		# Has backrefs: user, video.
		return 'Bookmark(id=%r, comment=%r, time=%r, created=%r, num_thumbs_up=%r, num_thumbs_down=%r, votes=%r, user=%r, video=%r)' % (
				self.id,
				self.comment,
				self.time,
				self.created.isoformat(),
				self.num_thumbs_up,
				self.num_thumbs_down,
				self.votes,
				self.user,
				self.video)


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

	def __init__(self, vote, now, user_id=None, bookmark_id=None):
		if user_id:
			self.user_id = user_id
		if bookmark_id:
			self.bookmark_id = bookmark_id
		self.vote = vote
		self.created = now
	
	def __repr__(self):
		# Has backref: bookmark.
		return 'PlaylistVote(id=%r, vote=%r, created=%r, user=%r, bookmark=%r)' % (
				self.id,
				self.vote,
				self.created,
				self.user,
				self.bookmark)


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
	twitch_video = TwitchVideo(archive_id, video_file_url, link_url)
	twitch_video.video = Video(title, length)
	session.add(twitch_video)
	session.commit()
	return twitch_video.id


"""Data for displaying a user.
"""
class DisplayedUser:
	def __init__(self, id, name, playlists):
		self.id = id
		self.name = name
		# The DisplayedUserPlaylist objects for each playlist.
		self.playlists = playlists
	
	def __repr__(self):
		return 'DisplayedUser(id=%r, name=%r, playlists=%r)' % (
				self.id,
				self.name,
				self.playlists)


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


"""Returns the DisplayedUser with the given identifier.
"""
def get_displayed_user(client_id, user_id):
	try:
		# Get the user.
		user = session.query(User).filter(User.id == user_id).one()
	except sa_orm.exc.NoResultFound:
		session.close()
		raise ValueError

	# Get the playlists.
	playlists_cursor = session.query(Playlist, PlaylistVote.vote)\
			.outerjoin(PlaylistVote, sa.and_(
				PlaylistVote.user_id == client_id,
				PlaylistVote.playlist_id == Playlist.id))\
			.filter(Playlist.user_id == user_id)
	session.close()

	# Create the displayed playlist and bookmarks.
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
	displayed_user = DisplayedUser(user.id, user.name, displayed_user_playlists)
	return displayed_user


"""Creates a playlist by the given user.
"""
def create_playlist(client_id, title, now=None):
	if session.query(User).filter(User.id == client_id).count() == 0:
		session.close()
		raise ValueError

	now = _get_now(now)
	playlist = Playlist('public', title, now, user_id=client_id)
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
		raise ValueError


"""Data for displaying a playlist.
"""
class DisplayedPlaylist:
	def __init__(self, author_id, author_name, time_created, time_updated, num_thumbs_up, num_thumbs_down, user_vote, title, bookmarks):
		self.author_id = author_id
		self.author_name = author_name
		self.time_created = time_created
		self.time_updated = time_updated
		self.num_thumbs_up = num_thumbs_up
		self.num_thumbs_down = num_thumbs_down
		self.user_vote = user_vote
		self.title = title
		# The DisplayedPlaylistBookmark objects for each bookmark.
		self.bookmarks = bookmarks

	def __repr__(self):
		return 'DisplayedPlaylist(author_id=%r, author_name=%r, time_created=%r, time_updated=%r, num_thumbs_up=%r, num_thumbs_down=%r, user_vote=%r, title=%r, bookmarks=%r)' % (
				self.author_id,
				self.author_name,
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
	def __init__(self, id, num_thumbs_up, num_thumbs_down, user_vote, video_title, comment, time_added, author_name, author_id):
		self.id = id
		self.num_thumbs_up = num_thumbs_up
		self.num_thumbs_down = num_thumbs_down
		self.user_vote = user_vote
		self.video_title = video_title
		self.comment = comment
		self.time_added = time_added
		self.author_name = author_name
		self.author_id = author_id
	
	def __repr__(self):
		return 'DisplayedPlaylistBookmark(id=%r, num_thumbs_up=%r, num_thumbs_down=%r, user_vote=%r, video_title=%r, comment=%r, time_added=%r, author_name=%r, author_id=%r)' % (
				self.id,
				self.num_thumbs_up,
				self.num_thumbs_down,
				self.user_vote,
				self.video_title,
				self.comment,
				self.time_added,
				self.author_name,
				self.author_id)


"""Returns the DisplayedPlaylist with the given identifier.
"""
def get_displayed_playlist(client_id, playlist_id):
	try:
		# Get the playlist without its bookmarks.
		playlist, creator_name, playlist_vote = session.query(Playlist, User.name, PlaylistVote.vote)\
				.join(User, Playlist.user_id == User.id)\
				.outerjoin(PlaylistVote, sa.and_(
					PlaylistVote.user_id == client_id,
					PlaylistVote.playlist_id == Playlist.id))\
				.filter(Playlist.id == playlist_id)\
				.one()
	except sa_orm.exc.NoResultFound:
		session.close()
		raise ValueError

	# Get the bookmarks.
	playlist_bookmarks_cursor = session.query(
				PlaylistBookmark.added, Bookmark, User.name, Video.title, BookmarkVote.vote)\
			.join(Bookmark, PlaylistBookmark.bookmark_id == Bookmark.id)\
			.join(User, Bookmark.user_id == User.id)\
			.join(Video, Bookmark.video_id == Video.id)\
			.outerjoin(BookmarkVote, sa.and_(
				BookmarkVote.user_id == Bookmark.user_id,
				BookmarkVote.bookmark_id == Bookmark.id))\
			.filter(PlaylistBookmark.playlist_id == playlist_id)
	session.close()

	# Create the displayed bookmarks and playlist.
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
				author_id=bookmark.user_id)
			for added, bookmark, author_name, video_title, bookmark_vote in playlist_bookmarks_cursor]
	displayed_playlist = DisplayedPlaylist(
			author_id=playlist.user_id,
			author_name=creator_name,
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
		raise ValueError
	
	try:
		now = _get_now(now)
		# Add the bookmark to the playlist.
		playlist_bookmark = PlaylistBookmark(playlist_id, bookmark_id, now)
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
		raise ValueError

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
		raise ValueError

	# Do not allow the creator to vote up his own playlist.
	if playlist_user_id == client_id:
		raise ValueError

	now = _get_now(now)
	if vote is None:
		# Create the vote by the user.
		vote = PlaylistVote(
				vote=_THUMB_UP_VOTE, now=now, user_id=client_id, playlist_id=playlist_id)
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
		raise ValueError

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
		raise ValueError

	# Do not allow the creator to vote down his own playlist.
	if playlist_user_id == client_id:
		raise ValueError

	now = _get_now(now)
	if vote is None:
		# Create the vote by the user.
		vote = PlaylistVote(
				vote=_THUMB_DOWN_VOTE, now=now, user_id=client_id, playlist_id=playlist_id)
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
		raise ValueError

"""Removes the vote for the playlist with the given identifier.
"""
def remove_playlist_vote(client_id, playlist_id, now=None):
	try:
		vote = session.query(PlaylistVote)\
				.filter(PlaylistVote.user_id == client_id, PlaylistVote.playlist_id == playlist_id)\
				.one()
	except sa_orm.exc.NoResultFound:
		session.close()
		raise ValueError

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
			author_name, author_id):
		self.id = id
		self.num_thumbs_up = num_thumbs_up
		self.num_thumbs_down = num_thumbs_down
		self.user_vote = user_vote
		self.comment = comment
		# The bookmarked time.
		self.time = time
		# The time to bookmark was created.
		self.time_created = time_created
		# The author's name, used for display.
		self.author_name = author_name
		# The author's unique identifier, used for linking.
		self.author_id = author_id

	def __repr__(self):
		return 'DisplayedBookmark(id=%r, num_thumbs_up=%r, num_thumbs_down=%r, user_vote=%r, comment=%r, time=%r, time_created=%r, author_name=%r, author_id=%r)' % (
				self.id,
				self.num_thumbs_up,
				self.num_thumbs_down,
				self.user_vote,
				self.comment,
				self.time,
				self.time_created,
				self.author_name,
				self.author_id)


"""Returns the DisplayedVideo with the given identifier.
"""
def get_displayed_video(client_id, video_id):
	try:
		# Get the video without its bookmarks.
		video = session.query(Video).filter(Video.id == video_id).one()
	except sa_orm.exc.NoResultFound:
		session.close()
		raise ValueError

	# Get the bookmarks.
	video_bookmarks_cursor = session.query(Bookmark, User.name, BookmarkVote.vote)\
			.join(User, Bookmark.user_id == User.id)\
			.outerjoin(BookmarkVote, sa.and_(
				BookmarkVote.user_id == client_id,
				BookmarkVote.bookmark_id == Bookmark.id))\
			.filter(Bookmark.video_id == video_id)
	session.close()

	# Create the displayed bookmarks and video.
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
				author_id=bookmark.user_id)
			for bookmark, author_name, bookmark_vote in video_bookmarks_cursor]
	displayed_video = DisplayedVideo(
			video.id, video.title, video.length, displayed_video_bookmarks)
	return displayed_video

"""Adds a bookmark by the given user for the given video.
"""
def add_video_bookmark(client_id, video_id, comment, time, now=None):
	now = _get_now(now)
	try:
		bookmark = Bookmark(comment, time, now, user_id=client_id, video_id=video_id)
		session.add(bookmark)
		session.commit()
		return bookmark.id
	except sa.exc.IntegrityError: 
		session.rollback()
		raise ValueError

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
		raise ValueError

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
		raise ValueError

	# Do not allow the creator to vote up his own bookmark.
	if bookmark_user_id == client_id:
		raise ValueError

	now = _get_now(now)
	if vote is None:
		# Create the vote by the user.
		vote = BookmarkVote(
				vote=_THUMB_UP_VOTE, now=now, user_id=client_id, bookmark_id=bookmark_id)
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
		raise ValueError

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
		raise ValueError

	# Do not allow the creator to vote down his own bookmark.
	if bookmark_user_id == client_id:
		raise ValueError

	now = _get_now(now)
	if vote is None:
		# Create the vote by the user.
		vote = BookmarkVote(
				vote=_THUMB_DOWN_VOTE, now=now, user_id=client_id, bookmark_id=bookmark_id)
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
		raise ValueError

"""Removes the vote for the bookmark with the given identifier.
"""
def remove_bookmark_vote(client_id, bookmark_id, now=None):
	try:
		vote = session.query(BookmarkVote)\
				.filter(BookmarkVote.user_id == client_id, BookmarkVote.bookmark_id == bookmark_id)\
				.one()
	except sa_orm.exc.NoResultFound:
		session.close()
		raise ValueError

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

