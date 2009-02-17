#!/usr/bin/python
# Comics Grabber by Tom Parker <palfrey@bits.bris.ac.uk>
# http://www.bits.bris.ac.uk/palfrey/
#
# URLTimeoutAsync class
# Grabs URLs, but with a timeout to avoid locking on crapped-up sites.	
#	
# Released under the GPL Version 2 (http://www.gnu.org/copyleft/gpl.html)

import urlparse,urllib2,asynchttp,asyncore,socket
from alarms import AsyncAlarmMixin
from URLTimeoutCommon import *

debug = False

class asyncgrab(AsyncAlarmMixin,asynchttp.AsyncHTTPConnection):
	def __init__(self, url,referer=None):
		origurl = url
		bits = urlparse.urlsplit(url)
		#print "bits",bits
		if bits[1].find(':')==-1:
			asynchttp.AsyncHTTPConnection.__init__(self, bits[1], 80)
		else:
			asynchttp.AsyncHTTPConnection.__init__(self, bits[1][:bits[1].find(':')], int(bits[1][bits[1].find(':'):]))
		AsyncAlarmMixin.__init__(self)
		self.set_relative_alarm(12)
		url = bits[2]
		if len(bits[3])>0:
			url += "?"+bits[3]
		if len(url)==0:
			url="/"
		self._url = url
		self._referer = referer
		self._closed = False
		
	def handle_response(self):
		if not self._closed:
			self.close()
			self._closed = True
			self.die_now = True
		else:
			print "we already killed this (response)"		

	def handle_connect(self):
		asynchttp.AsyncHTTPConnection.handle_connect(self)
		self.putrequest("GET", self._url)
		if self._referer!=None:
			self.putheader("Referer",self._referer)
		self.endheaders()
		self.getresponse()
	
	def handle_alarm(self, data):
		if not self._closed:
			self.close()
			self._closed = True
			self.die_now = True
		else:
			print "we already killed this (alarm)"		


class URLTimeoutAsync(URLGetter):
	def get_url(self,url,ref,proxy):
		if proxy!="":
			raise Exception, "URLTimeoutAsync can't handle proxies right now!"
		origurl = url
		grab = asyncgrab(url,ref)
		#grab.set_debuglevel(1)
		try:
			grab.connect()
		except socket.error,err:
			raise URLTimeoutError,err[1]

		grab.loop(timeout=self.getTimeout())

		if not hasattr(grab, "response") or grab.response.body==None:
			#print grab.__dict__
			raise URLTimeoutError, "Timed out!"
		
		info = {}
		for hdr in grab.response.msg.headers:
			(type,data) = hdr.split(':',1)
			info[type] = data[1:]
			while len(info[type])>0 and (info[type][-1]=='\r' or info[type][-1]=='\n'):
				info[type] = info[type][:-1]

		if grab.response.status == 301: # moved permenantly
			return self.get_url(info["Location"],ref,proxy)
		
		if grab.response.status !=200:
			raise URLTimeoutError,str(grab.response.status)+" "+grab.response.reason
		
		return URLObject(origurl,grab.response.body,info)

#if __name__ == '__main__':
	#print urllib2.urlopen("http://eris")
#	ret = URLTimeout().get_url("http://eris",None)
#	print ret.info().getmime()
