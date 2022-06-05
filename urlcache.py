#!/usr/bin/python
# Comics Grabber by Tom Parker <palfrey@tevp.net>
# http://tevp.net
#
# URL Caching class
# Caches retrieved URLs, with some comic-optimised sections
#
# Released under the GPL Version 2 (http://www.gnu.org/copyleft/gpl.html)

import os
from pickle import dump,load,UnpicklingError
try:
	from .urlgrab import URLTimeout, URLTimeoutError
except ImportError:
	print("Get urlgrab with 'git submodule init;git submodule update'")
	raise
import urllib.request, urllib.error, urllib.parse
from os.path import exists

import hashlib

def hexdigest_md5(data):
	if type(data) == str:
		data = data.encode('utf-8', errors='ignore')
	return hashlib.md5(data).hexdigest()

class CacheError(Exception):
	pass	

class URLCache:
	STAT_START = 1
	STAT_NEW = 2
	STAT_UNCHANGED = 3
	STAT_FAILED = 4

	def __init__(self,cache_dir,proxy=None,archive = False, debug = False):
		self.store = {}
		self.cache = cache_dir
		self.proxy = proxy
		self.archive = archive
		self.debug = debug
		if not os.path.exists(self.cache):
			os.makedirs(self.cache)

	def __load__(self,hash):
		if hash in self.store:
			return
		f = hash
		if f in os.listdir(self.cache):
			try:
				print("loading",os.path.join(self.cache,f))
				old = load(open(os.path.join(self.cache,f)))
				if old.mime[0] == "image" or self.archive:
					old.status = self.STAT_UNCHANGED
				else:
					old.status = self.STAT_START
				old.used = False
				self.store[self.md5(old.url,old.ref)] = old

			except (EOFError, ValueError, UnpicklingError): # ignore and discard
				os.unlink(os.path.join(self.cache,f))
	
	def remove(self, url, ref):
		url = url.replace("&amp;","&")
		h = self.md5(url,ref)
		if h in self.store:
			del self.store[h]
			print("removed", h)
			p = os.path.join(self.cache, h)
			if exists(p):
				print("deleted", p)
				os.unlink(p)
		else:
			print("no page in cache", url, ref, h)

	def cleanup(self):
		for h in self.store.keys():
			if self.store[h].status != self.STAT_FAILED and ("used" not in self.store[h].__dict__ or self.store[h].used == False):
				p = os.path.join(self.cache,h)
				if exists(p):
					os.unlink(p)
				
	def md5(self,url,ref):
		return hexdigest_md5(url+str(ref))
	
	def set_varying(self,url,ref=None):
		hash = self.md5(url,ref)
		if hash in self.store:
			self.store[hash].status = self.STAT_START

	def used(self,url,ref=None):
		hash = self.md5(url,ref)
		if hash in self.store:
			self.store[hash].used = True
	
	def get(self,url,ref=None):
		url = url.replace("&amp;","&").replace(" ","%20")
		hash = self.md5(url,ref)
		self.__load__(hash)
		if hash in self.store:
			old = self.store[hash]
		else:
			old = URLData(url,ref)
			self.store[hash] = old
		if old.status == self.STAT_FAILED:
			return None

		if old.status == self.STAT_START:
			try:
				ut = URLTimeout(debug = self.debug)
				ut.setTimeout(120)
				data = ut.get(url,ref=ref,proxy=self.proxy, headers = {"User-Agent":"Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.94 Safari/537.4"})
			except urllib.error.HTTPError as err:
				if err.code==404:
					return None
				else:
					if ref!=None:
						refpath = os.path.join(self.cache,self.md5(ref,None))
						if os.path.exists(refpath):
							os.unlink(refpath)
							print("Destroyed",refpath,"because of error!")
					self.gen_failed(old)
					raise CacheError(err.msg+" while getting <a href=\""+url+"\">"+url+"</a>")
			except urllib.error.URLError as err:
				self.gen_failed(old)
				raise CacheError(err.reason[1]+" while getting <a href=\""+url+"\">"+url+"</a>")
			except URLTimeoutError as err:
				self.gen_failed(old)
				raise CacheError(str(err)+" while getting <a href=\""+url+"\">"+url+"</a>")

			content = data.read()
			if old.content!=content:
				old.status = self.STAT_NEW
				old.content = content
				old.length = len(content)
				try:
					old.mime = (data.info().getmaintype(),data.info().getsubtype())
				except:
					return None
				f = open(os.path.join(self.cache,hash),'wb')
				dump(old,f,False)
			else:
				old.status = self.STAT_UNCHANGED
		old.used = True
		return old

	def gen_failed(self,old):
		old.status = self.STAT_FAILED
		old.content = ""
		old.length = 0
		old.mime = ("","")

	def get_mult(self,url,ref=None,count=1):
		retry = 0
		while retry<count:
			try:
				return self.get(url,ref)
			except CacheError as err:
				if str(err).find("Timed out")==-1:
					break
				retry += 1
				if retry!=count:
					print("retrying...")

		hash = self.md5(url,ref)
		self.store[hash] = URLData(url,ref)
		self.gen_failed(self.store[hash])
		raise

class URLData:
	def __init__(self,url,ref):
		self.url = url
		self.ref = ref
		self.content = ""
		self.status = URLCache.STAT_START
		self.mime = ("","")

