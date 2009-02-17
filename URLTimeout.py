#!/usr/bin/python
# Comics Grabber by Tom Parker <palfrey@bits.bris.ac.uk>
# http://www.bits.bris.ac.uk/palfrey/
#
# URLTimeout class
# Grabs URLs, but with a timeout to avoid locking on crapped-up sites.	
#	
# Released under the GPL Version 2 (http://www.gnu.org/copyleft/gpl.html)

from URLTimeoutAsync import URLTimeoutAsync
from URLTimeoutCommon import *

debug = False

class URLTimeout:
	def __init__(self):
		try:
			from URLTimeoutCurl import URLTimeoutCurl
			self.ut = URLTimeoutCurl()
		except:
			try:
				self.ut = URLTimeoutAsync()
			except:
				raise Exception, "Install Python >=2.3 (for asyncchat) or PyCurl, 'cause neither work right now!"

	def get_url(self,url,ref,proxy=""):
		return self.ut.get_url(url,ref,proxy)

URLTimeout.URLTimeoutError = URLTimeoutError
