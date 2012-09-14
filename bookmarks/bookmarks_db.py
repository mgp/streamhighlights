from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.ext.declarative as sa_ext_declarative
import sqlalchemy.orm as sa_orm

def get_engine(testing=True):
	if testing:
		return sa.create_engine('sqlite:///:memory:', echo=True)
	else:
		# TODO
		return None

_engine = get_engine()
_Session = sa_orm.sessionmaker(bind=_engine)
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

	def __init__(self, name, now=None):
		if now is None:
			now = datetime.utcnow()
		self.name = name
		self.created = now
	
	def __repr__(self):
		return 'User(id=%r, name=%r, created=%r, last_seen=%r, steam_user=%r, twitch_user=%r, playlists=%r, bookmarks=%r)' % (
				self.id,
				self.name,
				self.created.isoformat(),
				self.last_seen.isoformat(),
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

	def __repr__(self):
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

	def __repr__(self):
		return 'TwitchUser(id=%r, user=%r)' % (
				self.id,
				self.user)


"""A playlist of videos by a user.
"""
class Playlist(_Base):
	__tablename__ = 'Playlists'

	id = sa.Column(sa.Integer, primary_key=True)
	created = sa.Column(sa.DateTime, nullable=False)
	visibility = sa.Column(sa.Enum('public', 'private'), nullable=False)
	name = sa.Column(sa.String, nullable=False)
	num_thumbs_up = sa.Column(sa.Integer, nullable=False)
	num_thumbs_down = sa.Column(sa.Integer, nullable=False)

	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'))
	votes = sa_orm.relationship('PlaylistVote', backref='playlist')

	def __init__(self, visibility, name, now=None):
		if now is None:
			now = datetime.utcnow()
		self.created = now
		self.visibility = visibility
		self.name = name
		self.num_thumbs_up = 0
		self.num_thumbs_down = 0
	
	def __repr__(self):
		return 'Playlist(id=%r, created=%r, visibility=%r, name=%r, num_thumbs_up=%r, num_thumbs_down=%r, user=%r, votes=%r)' % (
				self.id,
				self.created,
				self.visbility,
				self.name,
				self.num_thumbs_up,
				self.num_thumbs_down,
				self.user,
				self.votes)


"""A vote by a user for a playlist.
"""
class PlaylistVote(_Base):
	__tablename__ = 'PlaylistVotes'

	# TODO: make (user_id, playlist_id) primary key?
	id = sa.Column(sa.Integer, primary_key=True)
	created = sa.Column(sa.DateTime, nullable=False)
	vote = sa.Column(sa.Enum('thumb_up', 'thumb_down'), nullable=False)

	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'))
	playlist_id = sa.Column(sa.Integer, sa.ForeignKey('Playlists.id'))

	def __init__(self, vote, now=None):
		if now is None:
			now = datetime.utcnow()
		self.created = now
		self.vote = vote
	
	def __repr__(self):
		return 'PlaylistVote(created=%r, vote=%r, user=%r, playlist=%r)' % (
				self.created,
				self.vote,
				self.user,
				self.playlist)


"""A video on Twitch.
"""
class Video(_Base):
	__tablename__ = 'Videos'

	id = sa.Column(sa.Integer, primary_key=True)
	length = sa.Column(sa.Integer, nullable=False)
	bookmarks = sa_orm.relationship("Bookmark", backref='video')

	def __repr__(self):
		return 'Video(id=%r, length=%r, bookmarks=%r)' % (
				self.id,
				self.length,
				self.bookmarks)


"""A bookmark for a video.
"""
class Bookmark(_Base):
	__tablename__ = 'Bookmarks'

	id = sa.Column(sa.Integer, primary_key=True)
	comment = sa.Column(sa.String, nullable=False)
	time = sa.Column(sa.DateTime, nullable=False)
	created = sa.Column(sa.DateTime, nullable=False)
	num_thumbs_up = sa.Column(sa.Integer, nullable=False)
	num_thumbs_down = sa.Column(sa.Integer, nullable=False)

	video_id = sa.Column(sa.Integer, sa.ForeignKey('Videos.id'))
	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'))
	votes = sa_orm.relationship('BookmarkVote', backref='bookmark')

	def __init__(self, comment, time, now=None):
		self.comment = comment
		self.time = time
		self.created = now
		self.num_thumbs_up = 0
		self.num_thumbs_down = 0

	def __repr__(self):
		return 'Bookmark(id=%r, comment=%r, time=%r, created=%r, num_thumbs_up=%r, num_thumbs_down=%r, video=%r, user=%r, votes=%r)' % (
				self.id,
				self.comment,
				self.time,
				self.created.isoformat(),
				self.num_thumbs_up,
				self.num_thumbs_down,
				self.video,
				self.user,
				self.votes)


"""A vote by a user for a bookmark.
"""
class BookmarkVote(_Base):
	__tablename__ = 'BookmarkVotes'

	# TODO: make (user_id, bookmark_id) primary key?
	id = sa.Column(sa.Integer, primary_key=True)
	created = sa.Column(sa.DateTime, nullable=False)
	vote = sa.Column(sa.Enum('thumb_up', 'thumb_down'), nullable=False)

	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'))
	bookmark_id = sa.Column(sa.Integer, sa.ForeignKey('Bookmarks.id'))

	def __init__(self, vote, now=None):
		if now is None:
			now = datetime.utcnow()
		self.created = now
		self.vote = vote
	
	def __repr__(self):
		return 'PlaylistVote(created=%r, vote=%r, user=%r, bookmark=%r)' % (
				self.created,
				self.vote,
				self.user,
				self.bookmark)

def create_all():
	_Base.metadata.create_all(_engine)

def drop_all():
	_Base.metadata.drop_all(_engine)


"""Enums for thumbs up and thumbs down votes by the user."""
_THUMB_UP_VOTE = 'thumb_up'
_THUMB_DOWN_VOTE = 'thumb_down'


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
	def __init__(self, id, time_updated, num_thumbs_up, num_thumbs_down, user_vote, name, num_bookmarks):
		self.id = id
		self.time_created = time_updated
		self.num_thumbs_up = num_thumbs_up
		self.num_thumbs_down = num_thumbs_down
		self.user_vote = user_vote
		self.name = name
		self.num_bookmarks = num_bookmarks
	
	def __repr__(self):
		return 'DisplayedUserPlaylist(id=%r, time_updated=%r, num_thumbs_up=%r, num_thumbs_down=%r, user_vote=%r, name=%r, num_bookmarks=%r)' % (
				self.id,
				self.time_updated,
				self.num_thumbs_up,
				self.num_thumbs_down,
				self.user_vote,
				self.name,
				self.num_bookmarks)


def get_displayed_user(user_id):
	# TODO
	pass

def create_playlist(user_id, name, now=None):
	if now is None:
		now = datetime.utcnow()
	# TODO: return playlist_id
	pass

def delete_playlist(user_id, playlist_id):
	# TODO
	pass


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


def get_displayed_playlist(playlist_id):
	# TODO
	pass

def add_playlist_bookmark(user_id, playlist_id, bookmark_id, now=None):
	if now is None:
		now = datetime.utcnow()
	# TODO
	pass

def remove_playlist_bookmark(user_id, playlist_id, bookmark_id):
	# TODO
	pass

def vote_playlist_thumb_up(user_id, playlist_id):
	# TODO
	pass

def vote_playlist_thumb_down(user_id, playlist_id):
	# TODO
	pass

def remove_playlist_vote(user_id, playlist_id):
	# TODO
	pass


"""Data for displaying a video.
"""
class DisplayedVideo:
	def __init__(self, name, length, playlist_map, bookmarks):
		self.name = name
		self.length = length
		# A mapping from playlist identifiers to their names.
		self.playlist_map = playlist_map
		# The DisplayedBookmark objects for each bookmark.
		self.bookmarks = bookmarks
	
	def __repr__(self):
		return 'DisplayedVideo(name=%r, length=%r, playlist_map=%r, bookmarks=%r)' % (
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


def get_displayed_video(video_id):
	# TODO
	pass

def add_video_bookmark(user_id, video_id, comment, time, now=None):
	if now is None:
		now = datetime.utcnow()
	# TODO: return bookmark_id
	pass

def remove_video_bookmark(user_id, bookmark_id):
	# TODO
	pass

def vote_bookmark_thumb_up(user_id, bookmark_id):
	# TODO
	pass

def vote_bookmark_thumb_down(user_id, bookmark_id):
	# TODO
	pass

def remove_bookmark_vote(user_id, bookmark_id):
	# TODO
	pass

