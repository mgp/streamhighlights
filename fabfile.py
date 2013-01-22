from fabric.api import *

env.hosts = ['msg']
env.port = 941

def prepare_dist():
	# Create the empty directory.
	local('rm -rf dist/')
	local('mkdir dist')
	# Copy all files into it.
	local('cp run_msg_server.py dist')
	local('cp -r matchstreamguide dist')
	with lcd('dist'):
		# Remove unnecessary files.
		local('find . -name "*.pyc" | xargs -n1 rm')
		local('find . -name ".DS_Store" | xargs -n1 rm')
		with lcd('matchstreamguide'):
			local('rm db_test_case.py *_tests.py')
			with lcd('static'):
				local('rm select2.js')
				local('rm -rf gen')
				local('rm -rf .webassets-cache')
		# Create the zipped tarball.
		local('tar czf msg.tar.gz *')

