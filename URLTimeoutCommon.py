#!/usr/bin/python
# Comics Grabber by Tom Parker <palfrey@bits.bris.ac.uk>
# http://www.bits.bris.ac.uk/palfrey/
#
# URLTimeoutCommon classes
# Common functionality used by URLTimeout* classes
#	
# Released under the GPL Version 2 (http://www.gnu.org/copyleft/gpl.html)

debug = False

class URLTimeoutError(Exception):
	pass

def strip(inp,remove):
	for x in remove:
		inp = inp.replace(x,"")

class URLHeaders:
	def __init__(self,headers):
		self.headers = headers
		if debug:
			print self.headers
	
	def getmime(self):
		ct = ""
		if self.headers.has_key("Content-Type"):
			ct = self.headers["Content-Type"]
		elif self.headers.has_key("Content-type"):
			ct = self.headers["Content-type"]
		else:
			raise Exception, "No content type header!"
		mime = ct.split("/",1)
		mime[1:] = mime[1].split(";",1)
		strip(mime[1],"\r\n")
		if mime[1][-1]=='\r' or mime[1][-1]=='\n':
			raise Exception
		
		mime = mime[:2]
		return mime
	
	
	def getmaintype(self):
		return self.getmime()[0]
		
	def getsubtype(self):
		return self.getmime()[1]

import codecs
#codec = {codecs.BOM_UTF16_LE:codecs.lookup('utf_16_le'),codecs.BOM_UTF16_BE:codecs.lookup('utf_16_be')}
codec = {}
ascii = codecs.lookup('ascii')[0]

class URLGetter:
	def __init__(self):
		self.timeout = 40
		
	def setTimeout(self, val):
		self.timeout = val
	
	def getTimeout(self):
		return self.timeout

	def get_url(self,url,ref):
		raise Exception, "Warning: subclass has not defined get_url"

class URLObject:
	def __init__(self,url,data,headers):
		self.url = url
		self.data = data
		for x in codec.keys():
			if self.data[0:len(x)] == x:
				self.data = ascii(codec[x][1](self.data[len(x):])[0])[0]
				break			

		self.headers = URLHeaders(headers)
	
	def geturl(self):
		return self.url
	
	def info(self):
		return self.headers
	
	def read(self):
		return self.data
