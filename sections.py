#!/usr/bin/python
# Comics Grabber by Tom Parker <palfrey@tevp.net>
# http://tevp.net
#
# Released under the GPL Version 2 (http://www.gnu.org/copyleft/gpl.html)

import re
from PerlREEval import PerlREEval
import copy
from urlcache import CacheError
from database import NoSuchStrip
from strips_pb2 import Strip, _TYPE as Type, Subsection
from google.protobuf.internal.containers import RepeatedCompositeFieldContainer
try:
	from google.protobuf.pyext._message import *
except ImportError:
	class RepeatedCompositeContainer:
		pass

import types

def user_strips(user,db,now,cache):
	strips = db.list_user_strips(user)
	ret = []
	for s in strips:
		try:
			new_s = db.get_strip(s)
		except NoSuchStrip:
			raise Exception("No strip found '%s'"%s)
		search = gen_search(new_s,db,now,cache)
		ret.append((new_s, search))
	return ret

def get_searches(strip,other_searches):
	if not other_searches:
		if len(strip.subs) == 0:
			return [search(strip)]
		else:
			return [search((s,strip)) for s in strip.subs]
	#raise Exception, other_searches
	return other_searches
	
def update_entries(strip, cl):
	for (fd,val) in cl.ListFields():
		n = fd.name
		if hasattr(strip,n):
			if n == "name" and strip.name!="":
				continue
			old = getattr(strip,n)
			if isinstance(old,RepeatedCompositeFieldContainer) or isinstance(old,RepeatedCompositeContainer):
				old.MergeFrom(getattr(cl,n))
			else:
				setattr(strip,n,val)

def gen_search(strip,db,now,cache, search = None):
	if strip.HasField("useclass"):
		new_c = db.get_class(strip.useclass)
		update_entries(strip, new_c)
		if strip.homepage.find("$")!=-1:
			pre = PerlREEval(now)
			pre.look = new_c
			strip.homepage = pre.eval_perl(strip.homepage)
		ns = copy.copy(get_searches(strip, search))
		for n in ns:
			n.parent = strip
		return ns
	if strip.HasField("infopage"):
		page = strip.infopage
		val = strip.infoval
		#print page,val
		try:
			print "Getting (infopage)", page
			data = cache.get_mult(page,None,count=2).content
			find = re.search(val, data)
			if find == None:
				raise CacheError, "Can't find %s"%val
			check = find.groups()[0]
			strip.infoval = check
		except CacheError,e:
			print "error while getting infoval '%s'"%page, str(e)
			#raise
				
class search:
	def __init__(self,parent):
		self.parent = parent
		self.look = Strip()
		self.eval = None

		if type(self.parent) in (types.ListType,types.TupleType):
			for p in self.parent:
				update_entries(self.look,p)
		else:
			update_entries(self.look,self.parent)

	def eval_perl(self,exp):
		return self.eval.eval_perl(exp)

	def __repr__(self):
		ret = {}
		for (fd,val) in self.look.ListFields():
			ret[fd.name] = val
		return ret.__repr__()

	def retr(self,now, archive = False):
		if self.eval == None:
			self.eval = PerlREEval(now)
			self.eval.look = self.look

		data = ()

		method = Type.values_by_number[self.look.type].name
		if method == "search":
			data = {"searchpattern":self.look.searchpattern,"baseurl":self.look.baseurl,"searchpage":self.look.searchpage, "initialpattern": self.look.initialpattern}
			if archive:
				data["searchpage"] = self.look.firstpage
				data["namepattern"] = self.look.namepattern
				data["nextpattern"] = self.look.nextpage
				if hasattr(self.look, "namepage"):
					data["namepage"] = self.look.namepage
				else:
					data["namepage"] = ""
			if data["searchpage"] == "":
				data["searchpage"] = self.look.homepage
			if data["baseurl"] == "":
				data["baseurl"] = self.look.homepage
			if not self.look.noperl:
				for d in data.keys():
					data[d] = self.eval_perl(data[d])
					if data[d].find("$")!=-1:
						print self.look
						print data
						raise Exception("Unevaluated variable! - "+str(data[d]))
		elif method == "generate":
			if archive:
				raise Exception, self.look
			data = self.eval_perl(self.look.imageurl)
		else:
			print method
			print self.look
			raise Exception("dunno what to do!")
		return (method,data)
