from fabric.api import *
import os

env.hosts = ['msg']
env.port = 941

_DIST_DIR = 'matchstreamguide/'
_DIST_PARENT_DIR = 'dist/'
_DIST_FULL_DIR = os.path.join(_DIST_PARENT_DIR, _DIST_DIR)
_ARCHIVE_FILE = 'msg.tar.gz'

def prepare():
	# Create the empty directory.
	local('rm -rf %s' % _DIST_FULL_DIR)
	local('mkdir -p %s' % _DIST_FULL_DIR)
	# Copy all files into it.
	local('cp run_msg_server.py %s' % _DIST_FULL_DIR)
	local('cp -r matchstreamguide %s' % _DIST_FULL_DIR)
	with lcd(_DIST_FULL_DIR):
		# Remove unnecessary files.
		local('find . -name "*.pyc" | xargs -n1 rm')
		local('find . -name ".DS_Store" | xargs -n1 rm')
		with lcd('matchstreamguide'):
			local('rm db_test_case.py *_tests.py')
			with lcd('static'):
				local('rm select2.js')
				local('rm -rf gen')
				local('rm -rf .webassets-cache')
	with lcd(_DIST_PARENT_DIR):
		# Create the archive file.
		local('tar czf %s %s' % (_ARCHIVE_FILE, _DIST_DIR))

def deploy():
	with lcd(_DIST_PARENT_DIR):
		# Copy the archive file to the server.
		put(_ARCHIVE_FILE, '/home/mgp')

def all():
	prepare()
	deploy()

