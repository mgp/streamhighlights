import collections
from datetime import datetime, timedelta
from streamfinder import db, views
import pytz

def _recreate_tables():
	db.drop_all()
	db.create_all()

_TF2_GAME = 'tf2'
_TF2_INVITE_DIVISION = 'esea-s13-invite'

_EseaTeam = collections.namedtuple('EseaTeam', ['name', 'fingerprint'])

_ESEA_TF2_INVITE_TEAMS = [
	_EseaTeam('bp', 'esea:69987'),
	_EseaTeam('Classic Mixup', 'esea:51672'),
	_EseaTeam('Fully Torqued-', 'esea:69988'),
	_EseaTeam('The Chess Club', 'esea:65380'),
	_EseaTeam('Apocalypse Gaming', 'esea:56950'),
	_EseaTeam('Dont Trip', 'esea:32376'),
	_EseaTeam('Xensity', 'esea:51134'),
	_EseaTeam('Vector Gaming', 'esea:50903'),
]

def _add_teams():
	team_ids = []
	for name, fingerprint in _ESEA_TF2_INVITE_TEAMS:
		indexed_name = views._get_indexed_name(name)
		team_id = db.add_team(
				name, indexed_name, _TF2_GAME, _TF2_INVITE_DIVISION, fingerprint)
		team_ids.append(team_id)
	return team_ids

def _add_matches(
		xensity_id, classic_mixup_id, fully_torqued_id, apocalypse_gaming_id):
	eastern_tz = pytz.timezone('US/Eastern')
	now = eastern_tz.localize(datetime.utcnow())

	match1_time = now + timedelta(days=3)
	match1_time = match1_time.replace(hour=21, minute=0, second=0, microsecond=0)
	match1_fingerprint = 'esea:3085088'
	match_id1 = db.add_match(classic_mixup_id,
			apocalypse_gaming_id,
			match1_time.astimezone(pytz.utc).replace(tzinfo=None),
			game,
			division,
			match1_fingerprint)
	
	match2_time = now + timedelta(days=5)
	match2_time = match2_time.replace(hour=20, minute=0, second=0, microsecond=0)
	match2_fingerprint = 'esea:3088406'
	match_id2 = db.add_match(xensity_id,
			classic_mixup_id,
			match2_time.astimezone(pytz.utc).replace(tzinfo=None),
			game,
			division,
			match2_fingerprint)

	match3_time = now + timedelta(days=5)
	match3_time = match3_time.replace(hour=20, minute=30, second=0, microsecond=0)
	match3_fingerprint = 'esea:3085090'
	match_id3 = db.add_match(fully_torqued_id,
			xensity_id,
			match3_time.astimezone(pytz.utc).replace(tzinfo=None),
			game,
			division,
			match3_fingerprint)

	return match_id1, match_id2, match_id3

_TwitchStreamer = collections.namedtuple(
		'TwitchStreamer', ['id', 'name', 'display_name', 'logo'])

_TWITCH_TF2_STREAMERS = [
	_TwitchStreamer(37846210, 'teamfortresstv', 'TeamFortressTV', None),
	_TwitchStreamer(22097899, 'Bl4nk', 'blank', None),
	_TwitchStreamer(22129289, 'misterslin', 'MR SLIN', 
			'http://static-cdn.jtvnw.net/jtv_user_pictures/misterslin-profile_image-a33d9bf4cdc93d14-300x300.jpeg'),
]

def _add_streamers():
	streamer_ids = []
	for twitch_id, name, display_name, logo in _TWITCH_TF2_STREAMERS:
		indexed_name = views._get_indexed_name(display_name)
		streamer_id, new_user = db.twitch_user_logged_in(
				twitch_id, name, display_name, indexed_name, logo, None)
		db.toggle_can_stream_by_twitch_id(twitch_id, True)
		streamer_ids.append(streamer_id)
	return streamer_ids

def run():
	_recreate_tables()

	team_ids = _add_teams()
	print 'Team IDs: %s' % team_ids

	"""
	match_id1, match_id2, match_id3 = _add_matches(
			xensity_id, classic_mixup_id, fully_torqued_id, apocalypse_gaming_id)
	print 'Match IDs: %s, %s, %s' % (match_id1, match_id2, match_id3)
	"""

	streamer_ids = _add_streamers()
	print 'Streamer IDs: %s' % streamer_ids

if __name__ == '__main__':
	run()

