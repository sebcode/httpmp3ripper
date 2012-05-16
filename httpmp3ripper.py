"""
httpmp3ripper - mp3 ripping http proxy
by Sebastian Volland (based on Jonas Wagner's HTTPRipper)
---

Original license notice:

HTTPRipper a generic ripper for the web
Copyright (C) 2008-2009 Jonas Wagner

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import datetime
import logging
import os
from os import path
import shutil
import socket
import SocketServer
import sys
import tempfile
import threading
import time
from urlparse import urlparse
import prox as proxpy
import random
import pyid3lib

class Tee(object):
    """A filelike that writes it's data to two others"""
    def __init__(self, f1, f2):
        self.f1 = f1
        self.f2 = f2

    def write(self, data):
        self.f1.write(data)
        self.f2.write(data)

class HTTPProxyHandler(proxpy.HTTPProxyHandler):
	"""handles a single request to the proxy"""
	def forward_response_body(self, f1, f2, contentlength):
		"""forwardes the content to the client and (if record is true) logs it"""
		if self.server.record:
			fd, name = tempfile.mkstemp(dir=self.server.tempdir)
			f3 = os.fdopen(fd, "w+b", 0)
			f2 = Tee(f2, f3)
		self.forward(f1, f2, contentlength)
		if self.server.record:
			content_type = self.responseheaders.get("Content-Type")
			if content_type:
				content_type = content_type[0]
			self.server.on_new_file(self.url, name, content_type)

class HTTPProxyServer(proxpy.HTTPProxyServer, threading.Thread):
	"""accepts client connections, deletes all files on shutdown"""
	def __init__(self, mainwin):
		threading.Thread.__init__(self)
		proxpy.HTTPProxyServer.__init__(self, ("127.0.0.1", int(sys.argv[1])), HTTPProxyHandler)
		self.skip_headers.append("If-")
		self.tempdir = tempfile.mkdtemp(prefix="httpripper")
		self.record = True
		self.setDaemon(True)
		self.mainwin = mainwin
		self.counter = 0
		self.albumTrackCounter = {}
		self.targetPath = sys.argv[2]

	def run(self):
		self.serve_forever()

	def shutdown(self):
		shutil.rmtree(self.tempdir)
		self.socket.close()

	def on_new_file(self, url, filepath, content_type):
		if content_type != "audio/mpeg":
			os.unlink(filepath)
			return
		
		id3 = pyid3lib.tag(filepath)

		try:
			tracknum, total = id3.tracknum
		except:
			try:
				album = id3.album

				if album in self.albumTrackCounter:
					self.albumTrackCounter[album] += 1
				else:
					self.albumTrackCounter[album] = 1

				tracknum = self.albumTrackCounter[album]
			except:
				self.counter += 1
				tracknum = self.counter

		try:
			name = ("%02d-%s-%s" % (tracknum, id3.artist, id3.title)).replace(' ', '_')
		except:
			name = "unknown-%02d" % (self.counter)

		print "new file: %s" % (name)

		shutil.copy(filepath, '%s%s.mp3' % (self.targetPath, name))

if __name__ == "__main__":
	
	if len(sys.argv) < 3:
		print "syntax: %s <listen port> <target path>" % (sys.argv[0])
		print "example: %s 8080 /tmp/mp3z" % (sys.argv[0])
		sys.exit(1)

	#logging.basicConfig(level=logging.DEBUG)
	server = HTTPProxyServer(("127.0.0.1", int(sys.argv[1])))
	server.serve_forever()

