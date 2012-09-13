from datetime import datetime
import sqlalchemy as sa

def get_engine(testing=True):
	if testing:
		return sa.create_engine('sqlite:///:memory:', echo=True)
	else:
		# TODO
		return None


_Base = sa.declarative_base()


"""A user of the site.
"""
class User(_Base):
	__tablename__ = 'Users'

	id = sa.Column(sa.Integer, primary_key=True)
	created = sa.Column(sa.DateTime, nullable=False)
	last_seen = sa.Column(sa.DateTime)

	steam_user = sa.orm.relationship('SteamUser', uselist=False, backref='user')
	twitch_user = sa.orm.relationship('TwitchUser', uselist=False, backref='user')
	playlists = sa.orm.relationship('Playlist', backref='user')
	bookmarks = sa.orm.relationship('Bookmark', backref='user')

	def __init__(self, now=None):
		if now is None:
			now = datetime.utcnow()
		self.created = now
	
	def __repr__(self):
		return 'User(id=%r, created=%r, last_seen=%r, steam_user=%r, twitch_user=%r, playlists=%r, bookmarks=%r)' % (
				self.id,
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

	# TODO: pick primary key

	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'))

	def __repr__(self):
		return 'SteamUser(id=%r, user=%r') % (
				self.id,
				self.user)


"""If the user logged in through Twitch, the details of that user on Twitch.
"""
class TwitchUser(_Base):
	__tablename__ = 'TwitchUsers'

	# TODO: pick primary key

	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'))

	def __repr__(self):
		return 'TwitchUser(id=%r, user=%r') % (
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
	votes = sa.orm.relationship('PlaylistVote', backref='playlist')

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

	created = sa.Column(sa.DateTime, nullable=False)
	vote = sa.Column(sa.Enum('thumb_up', 'thumb_down'), nullable=False)

	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'))
	playlist_id = sa.Column(sa.Integer, sa.ForeignKey('Playlists.id'))

	# TODO: make user_id and playlist_id the primary key?

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
	bookmarks = sa.orm.relationship("Bookmark", backref='video')

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
	votes = sa.orm.relationship('BookmarkVote', backref='bookmark')

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

	created = sa.Column(sa.DateTime, nullable=False)
	vote = sa.Column(sa.Enum('thumb_up', 'thumb_down'), nullable=False)

	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'))
	bookmark_id = sa.Column(sa.Integer, sa.ForeignKey('Bookmarks.id'))

	# TODO: make user_id and bookmark_id the primary key?

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


"""Data for displaying a bookmark.
"""
class DisplayedBookmark:
	_THUMB_UP_VOTE = 'thumb_up'
	_THUMB_DOWN_VOTE = 'thumb_down'

	def __init__(self, num_thumbs_up, num_thumbs_down, user_vote, comment,
			author_name, author_id, playlist_ids):
		self.num_thumbs_up = num_thumbs_up
		self.num_thumbs_down = num_thumbs_down
		self.user_vote = user_vote
		self.comment = comment
		# The author's name, used for display.
		self.author_name = author_name
		# The author's unique identifier, used for linking.
		self.author_id = author_id
		# The identifiers of the user's playlists that this bookmark is part of.
		self.playlist_ids = playlist_ids

	def __repr__(self):
		return 'DisplayedBookmark(num_thumbs_up=%s, num_thumbs_down=%s, user_vote=%s, comment=%s, author_name=%s, author_id=%s, playlist_ids=%s)' % (
				self.num_thumbs_up,
				self.num_thumbs_down,
				self.user_vote,
				self.comment,
				self.author_name,
				self.author_id,
				self.playlist_ids)


"""Data for displaying a video.
"""
class DisplayedVideo:
	def __init__(self, length, playlist_map, bookmarks):
		self.length = length
		# A mapping from playlist identifiers to their names.
		self.playlist_map = playlist_map
		# The DisplayedBookmark objects for each bookmark.
		self.bookmarks = bookmarks
	
	def __repr__(self):
		return 'DisplayedVideo(length=%s, playlist_map=%s, bookmarks=%s)' % (
				self.length,
				self.playlist_map,
				self.bookmarks)

def get_displayed_video(user_id, video_id):
	# TODO
	pass

def vote_bookmark_thumb_up(user_id, bookmark_id):
	# TODO
	pass

def vote_bookmark_thumb_down(user_id, bookmark_id):
	# TODO
	pass

def remove_vote(user_id, bookmark_id):
	# TODO
	pass

# TODO: creating and deleting bookmarks

class DisplayedUser:
	# TODO
	pass

class DisplayedPlaylist:
	# TODO
	pass

