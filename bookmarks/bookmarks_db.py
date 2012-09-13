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

	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id')

	def __init__(self, visibility, name, now=None):
		if now is None:
			now = datetime.utcnow()
		self.created = now
		self.visibility = visibility
		self.name = name
		self.num_thumbs_up = 0
		self.num_thumbs_down = 0
	
	def __repr__(self):
		return 'Playlist(id=%r, created=%r, visibility=%r, name=%r, num_thumbs_up=%r, num_thumbs_down=%r, user=%r)' % (
				self.id,
				self.created,
				self.visbility,
				self.name,
				self.num_thumbs_up,
				self.num_thumbs_down,
				self.user)


"""A video on Twitch.
"""
class Video(_Base):
	__tablename__ = 'Videos'

	id = sa.Column(sa.Integer, primary_key=True)
	bookmarks = sa.orm.relationship("Bookmark", backref='video')

	def __repr__(self):
		return 'Video(id=%r, bookmarks=%r)' % (
				self.id,
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
	user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id')

	def __init__(self, comment, time, now=None):
		self.comment = comment
		self.time = time
		self.created = now
		self.num_thumbs_up = 0
		self.num_thumbs_down = 0

	def __repr__(self):
		return 'Bookmark(id=%r, comment=%r, time=%r, created=%r, num_thumbs_up=%r, num_thumbs_down=%r, video=%r, user=%r)' % (
				self.id,
				self.comment,
				self.time,
				self.created.isoformat(),
				self.num_thumbs_up,
				self.num_thumbs_down,
				self.video,
				self.user)

