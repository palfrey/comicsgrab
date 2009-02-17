#!/usr/bin/python
# Comics Grabber by Tom Parker <palfrey@bits.bris.ac.uk>
# http://www.bits.bris.ac.uk/palfrey/
#
# URLTimeoutCurl class
# Grabs URLs, but with a timeout to avoid locking on crapped-up sites.	
#	
# Released under the GPL Version 2 (http://www.gnu.org/copyleft/gpl.html)

import pycurl,re
from URLTimeoutCommon import *

class URLTimeoutCurl(URLGetter):
	def body_callback(self, buf):
		self.contents = self.contents + buf
	
	def head_callback(self, buf):
		self.header = self.header + buf

	def get_url(self,url,ref,proxy=""):
		self.contents = ""
		self.header = ""
		origurl = url
		c = pycurl.Curl()
		c.setopt(c.URL, url)
		c.setopt(c.WRITEFUNCTION, self.body_callback)
		c.setopt(c.HEADERFUNCTION, self.head_callback)
		c.setopt(c.USERAGENT, "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.3) Gecko/20070310 Iceweasel/2.0.0.3 (Debian-2.0.0.3-2)")
		c.setopt(c.LOW_SPEED_LIMIT, 15) # 15 bytes/sec = dead. Random value.
		c.setopt(c.LOW_SPEED_TIME, self.getTimeout()) # i.e. dead (< 15 bytes/sec) for x seconds
		if proxy!="":
			c.setopt(c.PROXY,proxy)
		
		if ref!=None:
			c.setopt(c.REFERER, ref)

		try:
			c.perform()
		except pycurl.error, msg:
			raise URLTimeoutError,msg[1]
			
		c.close()
		
		if self.contents=="" and self.header == "":
			raise URLTimeoutError, "Timed out!"
		
		info = {}
		status = 0
		hdrs = self.header.splitlines()

		status = [0,0]
		if len(self.header.strip())>0:
			ret = re.search("HTTP/1.[01] (\d+)(.*?)",hdrs[0]).group(1,2)
			status[0] = int(ret[0])
			status[1] = ret[1].strip()
			hdrs = hdrs[1:]

			for hdr in hdrs:
				if hdr == "":
					continue
				(type,data) = hdr.split(':',1)
				info[type] = data[1:]
				while (info[type][-1]=='\r' or info[type][-1]=='\n'):
					info[type] = info[type][:-1]
		else:
			status[0] = 200

		if status[0] == 301 or status[0]==302: # moved
			try:
				if info.has_key("location"):
					return self.get_url(info["location"],ref)
				else:
					return self.get_url(info["Location"],ref)
			except KeyError:
				print info
				raise
		
		if status[0] !=200:
			raise URLTimeoutError,str(status[0])+" "+status[1]
		
		return URLObject(origurl,self.contents,info)
