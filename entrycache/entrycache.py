# vim: tabstop=4 shiftwidth=4 expandtab
"""
entrycache.py
Caches entry timestamps of the original creation date

If you want to manually create the cachefile, place a file 
called .entrycache containing
{ }
in your datadir  directory. This file needs to be
writable by your webserver.

If you do not want to create this file, it will automatically
be created in your datadir. 

Questions, comments and fixes can be sent to joe@terrarum.net
"""

__author__ = 'Joe Topjian <joe@terrarum.net>'
__version__ = '$Id: entrycache.py, v 1 2005/08/07 19:00:00 joe Exp $'
__url__ = "http://joe.terrarum.net"

import os.path

def cb_start(args):
	t = { }
	request = args["request"]
	config = request.getConfiguration()
	data = request.getData()
	if os.path.isfile(os.path.join(config['datadir'],'.entrycache')):
		data['cachefile'] = os.path.join(config['datadir'],'.entrycache')
		f = file(os.path.join(config['datadir'],'.entrycache'))
		t = eval(f.read())
		f.close()
        data['cache'] = t
	request.addData(data)

	if not data.has_key('cachefile'):
		f = file(os.path.join(config['datadir'],'.entrycache'),'w')
		f.write("{ }")
		f.close()
		data['cachefile'] = os.path.join(config['datadir'],'.entrycache')
		request.addData(data)

def cb_filestat(args):
	request = args["request"]
	data = request.getData()
	cache = data["cache"]
	if cache.has_key(args['filename']):
		mtime = []
		for i in args['mtime']:
			mtime.append(i)
		mtime[8] = cache[args['filename']]
		args['mtime'] = tuple(mtime)
	else:
		cache[args['filename']] = args['mtime'][8]
		f = open(data['cachefile'],'w')
		f.write("{\n")
		f.write("\t'%s' : %i,\n" % (args['filename'], args['mtime'][8]))
		for i in cache:
			f.write("\t'%s' : %i,\n" % (i, cache[i]))
		f.write("}")
		f.close()
	return args
