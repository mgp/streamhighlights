from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.ext.declarative as sa_ext_declarative
import sqlalchemy.orm as sa_orm
import sqlalchemy.schema as sa_schema


def get_engine(testing=True):
	if testing:
		return sa.create_engine('sqlite:///:memory:')
	else:
		# TODO
		return None

_engine = get_engine()
_Session = sa_orm.sessionmaker(bind=_engine)
# TODO: Use a contextual session
# http://docs.sqlalchemy.org/en/rel_0_7/orm/session.html#unitofwork-contextual
session = _Session()


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


# TODO: add time_added data, or when the bookmark was added to the playlist
association_table = sa_schema.Table('PlaylistBookmarks', _Base.metadata,
	sa.Column('playlist_id', sa.Integer, sa.ForeignKey('Playlists.id')),
	sa.Column('bookmark_id', sa.Integer, sa.ForeignKey('Bookmarks.id'))
)

"""A playlist of videos by a user.
"""
class Playlist(_Base):
	__tablename__ = 'Playlists'

	id = sa.Column(sa.Integer, primary_key=True)
	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'))
	visibility = sa.Column(sa.Enum('public', 'private'), nullable=False)
	name = sa.Column(sa.String, nullable=False)
	num_thumbs_up = sa.Column(sa.Integer, nullable=False)
	num_thumbs_down = sa.Column(sa.Integer, nullable=False)
	created = sa.Column(sa.DateTime, nullable=False)
	updated = sa.Column(sa.DateTime, nullable=False)

	votes = sa_orm.relationship('PlaylistVote', backref='playlist')
	bookmarks = sa_orm.relationship('Bookmark',
			secondary=association_table)

	def __init__(self, visibility, name, now, user_id=None):
		if user_id:
			self.user_id = user_id
		self.visibility = visibility
		self.name = name
		self.num_thumbs_up = 0
		self.num_thumbs_down = 0
		self.created = now
		self.updated = now
	
	def __repr__(self):
		# Has backref: user.
		return 'Playlist(id=%r, visibility=%r, name=%r, num_thumbs_up=%r, num_thumbs_down=%r, created=%r, updated=%r, votes=%r, bookmarks=%r, user=%r)' % (
				self.id,
				self.visbility,
				self.name,
				self.num_thumbs_up,
				self.num_thumbs_down,
				self.created,
				self.updated,
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


"""A video on Twitch.
"""
class Video(_Base):
	__tablename__ = 'Videos'

	id = sa.Column(sa.Integer, primary_key=True)
	name = sa.Column(sa.String, nullable=False)
	length = sa.Column(sa.Integer, nullable=False)
	bookmarks = sa_orm.relationship("Bookmark", backref='video')

	def __init__(self, name, length):
		self.name = name
		self.length = length

	def __repr__(self):
		return 'Video(id=%r, name=%r, length=%r, bookmarks=%r)' % (
				self.id,
				self.name,
				self.length,
				self.bookmarks)


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
	global Videos
	global Bookmarks
	global BookmarkVotes

	_Base.metadata.create_all(_engine)

	# Create aliases for each table.
	Users = User.__table__
	SteamUsers = SteamUser.__table__
	TwitchUsers = TwitchUser.__table__
	Playlists = Playlist.__table__
	PlaylistVotes = PlaylistVote.__table__
	Videos = Video.__table__
	Bookmarks = Bookmark.__table__
	BookmarkVotes = BookmarkVote.__table__

def drop_all():
	global Users
	global SteamUsers
	global TwitchUsers
	global Playlists
	global PlaylistVotes
	global Videos
	global Bookmarks
	global BookmarkVotes

	# Clear aliases for each table.
	Users = None
	SteamUsers = None
	TwitchUsers = None
	Playlists = None
	PlaylistVotes = None
	Videos = None
	Bookmarks = None
	BookmarkVotes = None

	_Base.metadata.drop_all(_engine)

def _get_now(now):
	if now is None:
		return datetime.utcnow()
	return now


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
	def __init__(self, id, time_created, time_updated, num_thumbs_up, num_thumbs_down, user_vote, name, num_bookmarks):
		self.id = id
		self.time_created = time_created
		self.time_updated = time_updated
		self.num_thumbs_up = num_thumbs_up
		self.num_thumbs_down = num_thumbs_down
		self.user_vote = user_vote
		self.name = name
		self.num_bookmarks = num_bookmarks
	
	def __repr__(self):
		return 'DisplayedUserPlaylist(id=%r, time_created=%r, time_updated=%r, num_thumbs_up=%r, num_thumbs_down=%r, user_vote=%r, name=%r, num_bookmarks=%r)' % (
				self.id,
				self.time_created,
				self.time_updated,
				self.num_thumbs_up,
				self.num_thumbs_down,
				self.user_vote,
				self.name,
				self.num_bookmarks)


"""Returns the DisplayedUser with the given identifier.
"""
def get_displayed_user(user_id):
	try:
		# Get the user and his playlists.
		user = session.query(User).options(
				sa_orm.joinedload(User.playlists)).filter(User.id == user_id).one()
	except sa_orm.exc.NoResultFound:
		raise ValueError
	finally:
		# TODO: what should I do after a query?
		session.flush()

	displayed_user_playlists = [
			# TODO: set user_vote, num_bookmarks
			DisplayedUserPlaylist(
				id=playlist.id,
				time_created=playlist.created,
				time_updated=playlist.updated,
				num_thumbs_up=playlist.num_thumbs_up,
				num_thumbs_down=playlist.num_thumbs_down,
				user_vote=None,
				name=playlist.name,
				num_bookmarks=0) for playlist in user.playlists]
	displayed_user = DisplayedUser(user.id, user.name, displayed_user_playlists)
	return displayed_user
	

"""Creates a playlist by the given user.
"""
def create_playlist(user_id, name, now=None):
	now = _get_now(now)
	if session.query(User).filter(User.id == user_id).count() == 0:
		session.rollback()
		raise ValueError

	playlist = Playlist('public', name, now, user_id=user_id)
	session.add(playlist)
	session.commit()
	return playlist.id

"""Deletes the playlist with the given identifier.
"""
def delete_playlist(user_id, playlist_id, now=None):
	now = _get_now(now)
	result = session.execute(
			Playlists.delete().where(
				sa.and_(Playlist.id == playlist_id, Playlist.user_id == user_id)))
	session.commit()


"""Data for displaying a playlist.
"""
class DisplayedPlaylist:
	def __init__(self, author_id, author_name, time_created, time_updated, num_thumbs_up, num_thumbs_down, user_vote, name, playlist_map, bookmarks):
		self.author_id = author_id
		self.author_name = author_name
		self.time_created = time_created
		self.time_updated = time_updated
		self.num_thumbs_up = num_thumbs_up
		self.num_thumbs_down = num_thumbs_down
		self.user_vote = user_vote
		self.name = name
		# A mapping from playlist identifiers to their names.
		self.playlist_map = playlist_map
		# The DisplayedPlaylistBookmark objects for each bookmark.
		self.bookmarks = bookmarks

	def __repr__(self):
		return 'DisplayedPlaylist(author_id=%r, author_name=%r, time_created=%r, time_updated=%r, num_thumbs_up=%r, num_thumbs_down=%r, user_vote=%r, name=%r, bookmarks=%r, playlist_map=%r)' % (
				self.author_id,
				self.author_name,
				self.time_created,
				self.time_updated,
				self.num_thumbs_up,
				self.num_thumbs_down,
				self.user_vote,
				self.name,
				self.bookmarks,
				self.playlist_map)


"""Data for displaying a bookmark on a playlist page.
"""
class DisplayedPlaylistBookmark:
	def __init__(self, id, num_thumbs_up, num_thumbs_down, user_vote, video_name, comment, time_added, author_name, author_id, playlist_ids):
		self.id = id
		self.num_thumbs_up = num_thumbs_up
		self.num_thumbs_down = num_thumbs_down
		self.user_vote = user_vote
		self.video_name = video_name
		self.comment = comment
		self.time_added = time_added
		self.author_name = author_name
		self.author_id = author_id
		# The identifiers of the user's playlists that this bookmark is part of.
		self.playlist_ids = playlist_ids
	
	def __repr__(self):
		return 'DisplayedPlaylistBookmark(id=%r, num_thumbs_up=%r, num_thumbs_down=%r, user_vote=%r, video_name=%r, comment=%r, time_added=%r, author_name=%r, author_id=%r, playlist_ids=%r)' % (
				self.id,
				self.num_thumbs_up,
				self.num_thumbs_down,
				self.user_vote,
				self.video_name,
				self.comment,
				self.time_added,
				self.author_name,
				self.author_id,
				self.playlist_ids)


"""Returns the DisplayedPlaylist with the given identifier.
"""
def get_displayed_playlist(playlist_id):
	try:
		# Get the playlist and its bookmarks.
		playlist = session.query(Playlist).options(
				sa_orm.joinedload(Playlist.bookmarks)).filter(Playlist.id == playlist_id).one()
	except sa_orm.exc.NoResultFound:
		raise ValueError
	finally:
		# TODO: what should I do after a query?
		session.flush()

	displayed_playlist_bookmarks = [
			# TODO: set user_vote, video_name, time_added, author_name,
			DisplayedPlaylistBookmark(
				id=bookmark.id,
				num_thumbs_up=bookmark.num_thumbs_up,
				num_thumbs_down=bookmark.num_thumbs_down,
				user_vote=None,
				video_name=None,
				comment=bookmark.comment,
				time_added=None,
				author_name=None,
				author_id=playlist.user_id) for bookmark in playlist.bookmarks]
	# TODO: set user_name, author_name, playlist_map
	displayed_playlist = DisplayedPlaylist(
			author_id=playlist.user_id,
			author_name=None,
			time_created=playlist.created,
			time_updated=playlist.updated,
			num_thumbs_up=playlist.num_thumbs_up,
			num_thumbs_down=playlist.num_thumbs_down,
			user_vote=None,
			name=playlist.name,
			playlist_map={},
			bookmarks=displayed_playlist_bookmarks)
	return displayed_playlist

"""Adds the bookmark with the given identifier to the given playlist.
"""
def add_playlist_bookmark(user_id, playlist_id, bookmark_id, now=None):
	try:
		playlist = session.query(Playlist).filter(
				sa.and_(Playlist.id == playlist_id, Playlist.user_id == user_id)).one()
	except sa_orm.exc.NoResultFound:
		raise ValueError
	
	now = _get_now(now)
	# TODO
	pass

"""Removes the bookmark with the given identifier from the given playlist.
"""
def remove_playlist_bookmark(user_id, playlist_id, bookmark_id, now=None):
	try:
		playlist = session.query(Playlist).filter(
				sa.and_(Playlist.id == playlist_id, Playlist.user_id == user_id)).one()
	except sa_orm.exc.NoResultFound:
		raise ValueError

	now = _get_now(now)
	# TODO
	pass

"""Votes up the playlist with the given identifier.
"""
def vote_playlist_thumb_up(user_id, playlist_id, now=None):
	try:
		vote = session.query(PlaylistVote).filter(
				sa.and_(PlaylistVote.user_id == user_id, PlaylistVote.playlist_id == playlist_id)).one()
	except sa_orm.exc.NoResultFound:
		vote = None

	# TODO: foreign key constraint guarantees cannot add for unknown user or playlist?
	now = _get_now(now)
	if vote is None:
		# Create the vote by the user.
		vote = PlaylistVote(
				vote=_THUMB_UP_VOTE, now=now, user_id=user_id, playlist_id=playlist_id)
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
		session.rollback()
		return

	session.add(vote)
	session.commit()

"""Votes down the playlist with the given identifier.
"""
def vote_playlist_thumb_down(user_id, playlist_id, now=None):
	try:
		vote = session.query(PlaylistVote).filter(
				sa.and_(PlaylistVote.user_id == user_id, PlaylistVote.playlist_id == playlist_id)).one()
	except sa_orm.exc.NoResultFound:
		vote = None

	# TODO: foreign key constraint guarantees cannot add for unknown user or playlist?
	now = _get_now(now)
	if vote is None:
		# Create the vote by the user.
		vote = PlaylistVote(
				vote=_THUMB_DOWN_VOTE, now=now, user_id=user_id, playlist_id=playlist_id)
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
		session.rollback()
		return

	session.add(vote)
	session.commit()


"""Removes the vote for the playlist with the given identifier.
"""
def remove_playlist_vote(user_id, playlist_id, now=None):
	try:
		vote = session.query(PlaylistVote).filter(
				sa.and_(PlaylistVote.user_id == user_id, PlaylistVote.playlist_id == playlist_id)).one()
	except sa_orm.exc.NoResultFound:
		session.flush()
		return

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
	def __init__(self, id, name, length, playlist_map, bookmarks):
		self.id = id
		self.name = name
		self.length = length
		# A mapping from playlist identifiers to their names.
		self.playlist_map = playlist_map
		# The DisplayedBookmark objects for each bookmark.
		self.bookmarks = bookmarks
	
	def __repr__(self):
		return 'DisplayedVideo(id=%r, name=%r, length=%r, playlist_map=%r, bookmarks=%r)' % (
				self.id,
				self.name,
				self.length,
				self.playlist_map,
				self.bookmarks)


"""Data for displaying a bookmark on a video page.
"""
class DisplayedVideoBookmark:
	def __init__(self, id, num_thumbs_up, num_thumbs_down, user_vote, comment, time, time_created,
			author_name, author_id, playlist_ids):
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
		# The identifiers of the user's playlists that this bookmark is part of.
		self.playlist_ids = playlist_ids

	def __repr__(self):
		return 'DisplayedBookmark(id=%r, num_thumbs_up=%r, num_thumbs_down=%r, user_vote=%r, comment=%r, time=%r, time_created=%r, author_name=%r, author_id=%r, playlist_ids=%r)' % (
				self.id,
				self.num_thumbs_up,
				self.num_thumbs_down,
				self.user_vote,
				self.comment,
				self.time,
				self.time_created,
				self.author_name,
				self.author_id,
				self.playlist_ids)


"""Returns the DisplayedVideo with the given identifier.
"""
def get_displayed_video(video_id):
	try:
		# Get the video and its bookmarks.
		video = session.query(Video).options(
				sa_orm.joinedload(Video.bookmarks)).filter(Video.id == video_id).one()
	except sa_orm.exc.NoResultFound:
		raise ValueError
	finally:
		# TODO: what should I do after a query?
		session.flush()

	displayed_video_bookmarks = [
			# TODO: set user_vote, author_name, playlist_ids
			DisplayedVideoBookmark(
				id=bookmark.id,
				num_thumbs_up=bookmark.num_thumbs_up,
				num_thumbs_down=bookmark.num_thumbs_down,
				user_vote=None,
				comment=bookmark.comment,
				time=bookmark.time,
				time_created=bookmark.created,
				author_name=None,
				author_id=bookmark.user_id,
				playlist_ids=[]) for bookmark in video.bookmarks]
	# TODO: set playlist_map
	displayed_video = DisplayedVideo(
			video.id, video.name, video.length, {}, displayed_video_bookmarks)
	return displayed_video

"""Adds a bookmark by the given user for the given video.
"""
def add_video_bookmark(user_id, video_id, comment, time, now=None):
	now = _get_now(now)
	if session.query(Video).filter(Video.id == video_id).count() == 0:
		session.rollback()
		raise ValueError
	
	bookmark = Bookmark(comment, time, now, user_id=user_id, video_id=video_id)
	session.add(bookmark)
	session.commit()
	return bookmark.id

"""Removes the bookmark with the given identifier for the given video.
"""
def remove_video_bookmark(user_id, bookmark_id, now=None):
	now = _get_now(now)
	result = session.execute(
			Bookmarks.delete().where(
				sa.and_(Bookmark.id == bookmark_id, Bookmark.user_id == user_id)))
	session.commit()

"""Votes up the bookmark with the given identifier.
"""
def vote_bookmark_thumb_up(user_id, bookmark_id, now=None):
	try:
		vote = session.query(BookmarkVote).filter(
				sa.and_(BookmarkVote.user_id == user_id, BookmarkVote.bookmark_id == bookmark_id)).one()
	except sa_orm.exc.NoResultFound:
		vote = None

	# TODO: foreign key constraint guarantees cannot add for unknown user or bookmark?
	now = _get_now(now)
	if vote is None:
		# Create the vote by the user.
		vote = BookmarkVote(
				vote=_THUMB_UP_VOTE, now=now, user_id=user_id, bookmark_id=bookmark_id)
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
		session.rollback()
		return

	session.add(vote)
	session.commit()

"""Votes down the bookmark with the given identifier.
"""
def vote_bookmark_thumb_down(user_id, bookmark_id, now=None):
	try:
		vote = session.query(BookmarkVote).filter(
				sa.and_(BookmarkVote.user_id == user_id, BookmarkVote.bookmark_id == bookmark_id)).one()
	except sa_orm.exc.NoResultFound:
		vote = None

	# TODO: foreign key constraint guarantees cannot add for unknown user or bookmark?
	now = _get_now(now)
	if vote is None:
		# Create the vote by the user.
		vote = BookmarkVote(
				vote=_THUMB_DOWN_VOTE, now=now, user_id=user_id, bookmark_id=bookmark_id)
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
		session.rollback()
		return

	session.add(vote)
	session.commit()

"""Removes the vote for the bookmark with the given identifier.
"""
def remove_bookmark_vote(user_id, bookmark_id, now=None):
	try:
		vote = session.query(BookmarkVote).filter(
				sa.and_(BookmarkVote.user_id == user_id, BookmarkVote.bookmark_id == bookmark_id)).one()
	except sa_orm.exc.NoResultFound:
		session.flush()
		return

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

