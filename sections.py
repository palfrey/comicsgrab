#!/usr/bin/python
# Comics Grabber by Tom Parker <palfrey@bits.bris.ac.uk>
# http://www.bits.bris.ac.uk/palfrey/
#
# Released under the GPL Version 2 (http://www.gnu.org/copyleft/gpl.html)

import re,string,time,math
from PerlREEval import PerlREEval
import copy
from urlcache import CacheError

class InvalidKey (Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return "Key \""+self.value+"\" is a bad key!"

class Section:
	def __init__(self,name):
		self.name = name
		self.entries = {}
		self.good_keys = []
		self.lines = []
	
	def new_entry(self,key,data):
		if key not in self.good_keys:
			raise InvalidKey(key)
		self.entries[key] = data

	def __repr__(self):
		return self.__str__()
	
	def __str__(self):
		return "\n".join(self.good_keys)

class comic_config(Section):
	def __init__(self):
		Section.__init__(self,"")
		self.good_keys = ("must","may")

class comic_group(Section):
	def __init__(self,name):
		Section.__init__(self,name)
		self.good_keys = ("group","desc","include")
		self.desc = ""
		self.strips = []

	def new_entry(self,key,data):
		Section.new_entry(self,key,data)
		if key == "desc":
			self.desc = data
		elif key == "include":
			new_strips = [x for x in re.split(' ',data) if x.strip()!=""]
			self.strips = self.strips + new_strips

	def get_strips(self,strips,classes,now,cache):
		for i in range(len(self.strips)):
			for s in strips:
				if s.name == self.strips[i]:
					self.strips[i] = s
					s.gen_search(classes,now,cache)
					break
			else:
				raise Exception("No strip found '%s'"%self.strips[i])
		return self.strips

class comic_class(Section):
	def __init__(self,name):
		Section.__init__(self,name)
		self.searches = []
		self.good_keys = ("class","homepage","type","searchpattern","baseurl","provides","imageurl","searchpage","prefetch","referer","days","subbeg","subend","ext","noperl","index","infopage","infoval")
		self.curr = None

	def new_entry(self,key,data):
		key = key.lower()
		if key not in self.good_keys:
			raise InvalidKey(key)
		if key == "subbeg":
			self.curr = search(self)
			self.searches.append(self.curr)
		elif key == "subend":
			self.curr = None
		elif self.curr == None:
			self.entries[key] = data
		else:
			self.curr.entries[key] = data

class comic_strip(comic_class):
	def __init__(self,name):
		comic_class.__init__(self,name)
		self.desc = ""
		self.entries["days"] = "Mo-Su"
		self.days = map(lambda x:1,range(7))
		self.good_keys = self.good_keys + ("strip","name","matchpart","useclass","artist")

	def new_entry(self,key,data):	
		if key[0]=='$':
			if self.curr == None:
				self.entries[key] = data
			else:
				self.curr.entries[key] = data
		else:
			comic_class.new_entry(self,key,data)
	
	def get_searches(self,now):
		if len(self.searches)==0:
			return [search(self)]
		for e in self.searches:
			if len(e.entries)==0:
				self.searches.remove(e)
			
		return self.searches
	
	def __repr__(self):
		return " - ".join([self.entries["name"],self.entries["homepage"]])
#		ret = []
#		for e in self.get_searches():
#			ret.append(str(e.retr()))
#			
#		return " - ".join(ret)
	
	def gen_search(self,classes,now,cache):
		if self.entries.has_key('useclass'):
			for j in range(len(classes)):
				if classes[j].name == self.entries['useclass']:
					self.entries.update(classes[j].entries)
					if self.entries["homepage"].find("$")!=-1:
						pre = PerlREEval(now)
						pre.look = self.entries
						self.entries["homepage"] = pre.eval_perl(self.entries["homepage"])
					ns = copy.deepcopy(classes[j].searches)
					for n in ns:
						n.parent = self
					self.searches.extend(ns)
					break
			else:
				raise Exception("Can't find class "+self.entries['useclass'])
		if self.entries.has_key("infopage"):
			page = self.entries["infopage"]
			val = self.entries["infoval"]
			#print page,val
			try:
				data = cache.get_mult(page,None,count=2).content
				check = re.search(val,data).groups()[0]
				self.entries["infoval"] = check
			except CacheError,e:
				print "error while getting infoval",str(e)
				
			#print data
			#print check
			#raise Exception

class search:
	def __init__(self,parent):
		self.parent = parent
		self.entries = {}
		self.look = {}
		self.eval = None

	def __repr__(self):
		return self.entries.__repr__()
	
	def eval_perl(self,exp):
		return self.eval.eval_perl(exp)
	
	def retr(self,now):
		if self.eval == None:
			self.eval = PerlREEval(now)
			self.eval.look = self.look

		if self.parent <> None:
			self.look.update(self.parent.entries)
			#print self.look
		self.look.update(self.entries)
		#print self.look
		#if self.look["homepage"].find("$")!=-1:
		#	self.look["homepage"] = self.eval_perl(self.look["homepage"])
		data = ()

		if "type" not in self.look:
			print self.look,self.parent.entries
			if self.parent <> None:
				print "parent", self.parent.entries
			raise Exception("No type!")
		try:
			if self.look["type"] == "search":
				data = [self.look["searchpattern"],self.look.get("baseurl",""),self.look.get("searchpage",self.look["homepage"])]
				if not self.look.has_key("noperl") or self.look["noperl"] == "0":
					for d in range(len(data)):
						data[d] = self.eval_perl(data[d])
						if data[d].find("$")!=-1:
							print self.look
							print data
							raise Exception("Unevaluated variable! - "+str(data[d]))
			elif self.look["type"] == "generate":
				data = self.eval_perl(self.look["imageurl"])
			else:
				print self.look
				raise Exception("dunno what to do!")
		except Exception:
			print self.look
			print self.entries
			raise
		return (self.look["type"],data)
	

		
