from datetime import datetime
import db

def _recreate_tables():
	db.drop_all()
	db.create_all()

game = 'tf2'
league = 'Season 13 Invite'

def _add_teams():

	team1_name = 'Xensity'
	team1_fingerprint = 'esea:51134'
	team_id1 = db.add_team(team1_name, game, league, team1_fingerprint)

	team2_name = 'Classic Mixup'
	team2_fingerprint = 'esea:51672'
	team_id2 = db.add_team(team2_name, game, league, team2_fingerprint)

	team3_name = 'LASER BEAMS'
	team3_fingerprint = 'esea:69988'
	team_id3 = db.add_team(team3_name, game, league, team3_fingerprint)

	return team_id1, team_id2, team_id3

def _add_matches(team1_id, team2_id, team3_id):
	match1_time = datetime(2012, 5, 5, 20, 0, 0, 0)
	match1_fingerprint = 'esea:222'
	match_id1 = db.add_match(
			team1_id, team2_id, match1_time, game, league, match1_fingerprint)
	
	match2_time = datetime(2012, 5, 6, 20, 30, 0, 0)
	match2_fingerprint = 'esea:333'
	match_id2 = db.add_match(
			team1_id, team3_id, match2_time, game, league, match2_fingerprint)

	match3_time = datetime(2012, 5, 6, 21, 0, 0, 0)
	match3_fingerprint = 'esea:444'
	match_id3 = db.add_match(
			team2_id, team3_id, match3_time, game, league, match3_fingerprint)

	return match_id1, match_id2, match_id3

def _add_streamers(match_id1, match_id2, match_id3):
	streamer1_twitch_id = 21605834
	streamer1_name = 'seanbud'
	streamer1_display_name = 'Seanbud'
	streamer1_logo = 'http://static-cdn.jtvnw.net/jtv_user_pictures/seanbud-profile_image-8feca52a40c892ad-300x300.jpeg'
	user_id1 = db.twitch_user_logged_in(
			streamer1_twitch_id, streamer1_name, streamer1_display_name, streamer1_logo, None)
	db.add_stream_match(user_id1, match_id1)
	db.add_stream_match(user_id1, match_id2)

	streamer2_twitch_id = 25367903
	streamer2_name = 'thatguytagg'
	streamer2_display_name = 'Thatguytagg'
	streamer2_logo = 'http://static-cdn.jtvnw.net/jtv_user_pictures/thatguytagg-profile_image-c6841baa66e80f1e-300x300.jpeg'
	user_id2 = db.twitch_user_logged_in(
			streamer2_twitch_id, streamer2_name, streamer2_display_name, streamer2_logo, None)
	db.add_stream_match(user_id2, match_id2)

	streamer3_twitch_id = 27541787
	streamer3_name = 'stabbystabby'
	streamer3_display_name = 'stabbystabby'
	streamer3_logo = 'http://static-cdn.jtvnw.net/jtv_user_pictures/stabbystabby-profile_image-1c2ef7de2c68e389-300x300.png'
	user_id3 = db.twitch_user_logged_in(
			streamer3_twitch_id, streamer3_name, streamer3_display_name, streamer3_logo, None)

	return user_id1, user_id2, user_id3

if __name__ == '__main__':
	_recreate_tables()

	team_id1, team_id2, team_id3 = _add_teams()
	print 'Team IDs: %s, %s, %s' % (team_id1, team_id2, team_id3)

	match_id1, match_id2, match_id3 = _add_matches(team_id1, team_id2, team_id3)
	print 'Match IDs: %s, %s, %s' % (match_id1, match_id2, match_id3)

	user_id1, user_id2, user_id3 = _add_streamers(match_id1, match_id2, match_id3)
	print 'User IDs: %s, %s, %s' % (user_id1, user_id2, user_id3)

