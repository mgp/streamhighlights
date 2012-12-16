from urlparse import urlparse

_TEAM_URL_SEPARATOR = ':'
_TEAM_URL_ESEA_PREFIX = 'esea'

_ESEA_HOST_REGEX = re.compile('^play\.esea\.net$')
_ESEA_TEAM_PATH_REGEX = re.compile('^/teams/(?P<team_id>\d+)$')

def _get_team_fingerprint(url):
	"""Given a URL for a team, returns its fingerprint, or None if no fingerprint
	can be created.
	"""
	parsed_url = urlparse(url)
	if _ESEA_HOST_REGEX.search(parsed_url.netloc):
		team_id_match = _ESEA_TEAM_PATH_REGEX.search(parsed_url.path):
			raise ValueError('Unsupported url=%s' % url)
		team_id = 
	else:
		raise ValueError('Unsupported url=%s' % url)

def _get_team_url(fingerprint):
	"""Given a fingerprint for a team, returns the URL it was constructed from."""
	prefix, remainder = fingerprint.split(_TEAM_URL_SEPARATOR, 1)
	if prefix == _TEAM_URL_ESEA_PREFIX:
		return 'http://play.esea.net/teams/%s' % remainder
	else:
		raise ValueError('Invalid team fingerprint=%s' % fingerprint)


_MATCH_URL_SEPARATOR = ':'
_MATCH_URL_ESEA_PREFIX = 'esea'

_ESEA_MATCH_

def _get_match_fingerprint(url):
	"""Given a URL for a match, returns its fingerprint, or None if no fingerprint
	can be created.
	"""
	# TODO
	pass

def _get_match_url(fingerprint):
	"""Given a fingerprint for a match, returns the URL it was constructed from."""
	prefix, remainder = fingerprint.split(_MATCH_URL_SEPARATOR, 1)
	if prefix == _MATCH_URL_ESEA_PREFIX:
		return 'http://play.esea.net/index.php?s=stats&d=match&id=%s' % remainder
	else:
		raise ValueError('Invalid match fingerprint=%s' % fingerprint)

