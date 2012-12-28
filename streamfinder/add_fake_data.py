from datetime import datetime
import db

def _recreate_tables():
	db.drop_all()
	db.create_all()

game = 'tf2'
division = 'esea-s13-invite'

def _add_teams():
	xensity_name = 'Xensity'
	xensity_fingerprint = 'esea:51134'
	xensity_id = db.add_team(
			xensity_name, game, division, xensity_fingerprint)

	classic_mixup_name = 'Classic Mixup'
	classic_mixup_fingerprint = 'esea:51672'
	classic_mixup_id = db.add_team(
			classic_mixup_name, game, division, classic_mixup_fingerprint)

	laser_beams_name = 'LASER BEAMS'
	laser_beams_fingerprint = 'esea:69988'
	laser_beams_id = db.add_team(
			laser_beams_name, game, division, laser_beams_fingerprint)

	apocalypse_gaming_name = 'Apocalypse Gaming'
	apocalypse_gaming_fingerprint = 'esea:56950'
	apocalypse_gaming_id = db.add_team(
			apocalypse_gaming_name, game, division, apocalypse_gaming_fingerprint)

	return (xensity_id, classic_mixup_id, laser_beams_id, apocalypse_gaming_id)

def _add_matches(
		xensity_id, classic_mixup_id, laser_beams_id, apocalypse_gaming_id):
	match1_time = datetime(2012, 12, 24, 20, 0, 0, 0)
	match1_fingerprint = 'esea:3085088'
	match_id1 = db.add_match(classic_mixup_id, apocalypse_gaming_id,
			match1_time, game, division, match1_fingerprint)
	
	match2_time = datetime(2012, 12, 27, 20, 30, 0, 0)
	match2_fingerprint = 'esea:3088406'
	match_id2 = db.add_match(xensity_id, classic_mixup_id,
			match2_time, game, division, match2_fingerprint)

	match3_time = datetime(2013, 1, 6, 21, 0, 0, 0)
	match3_fingerprint = 'esea:3085090'
	match_id3 = db.add_match(laser_beams_id, xensity_id,
			match3_time, game, division, match3_fingerprint)

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

	xensity_id, classic_mixup_id, laser_beams_id, apocalypse_gaming_id = _add_teams()
	print 'Team IDs: %s, %s, %s, %s' % (
			xensity_id, classic_mixup_id, laser_beams_id, apocalypse_gaming_id)

	match_id1, match_id2, match_id3 = _add_matches(
			xensity_id, classic_mixup_id, laser_beams_id, apocalypse_gaming_id)
	print 'Match IDs: %s, %s, %s' % (match_id1, match_id2, match_id3)

	user_id1, user_id2, user_id3 = _add_streamers(match_id1, match_id2, match_id3)
	print 'User IDs: %s, %s, %s' % (user_id1, user_id2, user_id3)

