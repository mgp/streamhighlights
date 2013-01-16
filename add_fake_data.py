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

_BP = _EseaTeam('bp', 'esea:69987')
_CLASSIC_MIXUP = _EseaTeam('Classic Mixup', 'esea:51672')
_FULLY_TORQUED = _EseaTeam('Fully Torqued-', 'esea:69988')
_CHESS_CLUB = _EseaTeam('The Chess Club', 'esea:65380')
_APOCALYPSE_GAMING = _EseaTeam('Apocalypse Gaming', 'esea:56950')
_DONT_TRIP = _EseaTeam('Dont Trip', 'esea:32376')
_XENSITY = _EseaTeam('Xensity', 'esea:51134')
_VECTOR_GAMING = _EseaTeam('Vector Gaming', 'esea:50903')

_ESEA_TF2_INVITE_TEAMS = [
	_BP,
	_CLASSIC_MIXUP,
	_FULLY_TORQUED,
	_CHESS_CLUB,
	_APOCALYPSE_GAMING,
	_DONT_TRIP,
	_XENSITY,
	_VECTOR_GAMING,
]

def _add_teams():
	team_ids = {}
	for invite_team in _ESEA_TF2_INVITE_TEAMS:
		name, fingerprint = invite_team
		indexed_name = views._get_indexed_name(name)
		team_id = db.add_team(
				name, indexed_name, _TF2_GAME, _TF2_INVITE_DIVISION, fingerprint)
		team_ids[fingerprint] = team_id
	return team_ids


_EseaMatch = collections.namedtuple(
		'EseaMatch', ['team1', 'team2', 'time', 'fingerprint'])

_ESEA_TF2_INVITE_MATCHES = [
	_EseaMatch(_FULLY_TORQUED, _CLASSIC_MIXUP, datetime(2013, 1, 17, 4, 0, 0), 'esea:3138477'),
	_EseaMatch(_CLASSIC_MIXUP, _DONT_TRIP, datetime(2013, 1, 18, 4, 0, 0), 'esea:3135189'),
]

def _add_matches(team_ids):
	match_ids = {}
	for team1, team2, time, fingerprint in _ESEA_TF2_INVITE_MATCHES:
		team1_id = team_ids[team1.fingerprint]
		team2_id = team_ids[team2.fingerprint]
		match_id = db.add_match(
				team1_id, team2_id, time, _TF2_GAME, _TF2_INVITE_DIVISION, fingerprint)
		match_ids[fingerprint] = match_id
	return match_ids


_TwitchStreamer = collections.namedtuple(
		'TwitchStreamer', ['twitch_id', 'name', 'display_name', 'logo'])

_TEAM_FORTRESS_TV = _TwitchStreamer(37846210, 'teamfortresstv', 'TeamFortressTV', None)
_BLANK = _TwitchStreamer(22097899, 'Bl4nk', 'blank', None)
_MR_SLIN = _TwitchStreamer(22129289, 'misterslin', 'MR SLIN', 
		'http://static-cdn.jtvnw.net/jtv_user_pictures/misterslin-profile_image-a33d9bf4cdc93d14-300x300.jpeg')

_TWITCH_TF2_STREAMERS = [
	_TEAM_FORTRESS_TV,
	_BLANK,
	_MR_SLIN,
]

_TwitchStreamedMatch = collections.namedtuple(
		'TwitchStreamedMatch', ['streamer', 'match_fingerprint'])

_TWITCH_TF2_STREAMED_MATCHES = [
	_TwitchStreamedMatch(_TEAM_FORTRESS_TV, _ESEA_TF2_INVITE_MATCHES[0].fingerprint),
	_TwitchStreamedMatch(_TEAM_FORTRESS_TV, _ESEA_TF2_INVITE_MATCHES[1].fingerprint),
]

def _add_streamers(match_ids):
	streamer_ids = {}
	for twitch_id, name, display_name, logo in _TWITCH_TF2_STREAMERS:
		indexed_name = views._get_indexed_name(display_name)
		streamer_id, new_user = db.twitch_user_logged_in(
				twitch_id, name, display_name, indexed_name, logo, None)
		db.toggle_can_stream_by_twitch_id(twitch_id, True)
		streamer_ids[twitch_id] = streamer_id
	for streamer, match_fingerprint in _TWITCH_TF2_STREAMED_MATCHES:
		streamer_id = streamer_ids[streamer.twitch_id]
		match_id = match_ids[match_fingerprint]
		db.add_stream_match(streamer_id, match_id)
	return streamer_ids

def run():
	_recreate_tables()

	team_ids = _add_teams()
	print 'Team IDs: %s' % team_ids

	match_ids = _add_matches(team_ids)
	print 'Match IDs: %s' % match_ids

	streamer_ids = _add_streamers(match_ids)
	print 'Streamer IDs: %s' % streamer_ids

if __name__ == '__main__':
	run()

