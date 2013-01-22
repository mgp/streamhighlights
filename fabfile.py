from fabric.api import *

env.hosts = ['msg']
env.port = 941

def prepare_dist():
	local('rm -rf dist/')
	local('mkdir dist')
	local('cp run_msg_server.py dist')
	local('cp -r matchstreamguide dist')
	with lcd('dist'):
		local('find . -name "*.pyc" | xargs -n1 rm')
		local('find . -name ".DS_Store" | xargs -n1 rm')
		local('rm -rf matchstreamguide/static/gen')
		local('rm -rf matchstreamguide/static/.webassets-cache')
		local('tar czf msg.tar.gz *')

