#!/usr/bin/python
# Comics Grabber by Tom Parker <palfrey@tevp.net>
# http://tevp.net
#
# Released under the GPL Version 2 (http://www.gnu.org/copyleft/gpl.html)

import re,os,sys
from sections import *
from date_manip import CalcWeek,DateManip
import urlcache
import urlparse
try:
	from PIL import Image
except ImportError: # no PIL!
	Image = None

import database

class ComicsDef:
	def __init__(self,deffile,cachedir,debug=0,proxy=None, db=None, module="Sqlite"):
		if db != None:
			self.db = getattr(database,module)(db)
		else:
			self.db = getattr(database,module)(user="palfrey_palfrey",database="palfrey_palfrey",password="epsilon", prefix="comics_")
		self.debug = debug
		self.maxdays = 14
		self.proxy = proxy
		self.cache = urlcache.URLCache(cachedir,self.proxy)

	def get_strips(self,strips=None,user=None,now=DateManip(),all_users=False):
		ret = []
		if strips!=None:
			for d in strips:
				try:
					s = self.db.get_strip(d)
					search = gen_search(s,self.db,self.now,self.cache)
					ret.append((s,search))
				except database.NoSuchStrip:
					raise Exception("No strip found "+d)
		if all_users:
			user = []
			for u in self.db.list_users():
				print "u",u
				u = self.db.get_user(u)
				if u.enabled:
					user.append(u.name)
		if user != None:
			for d in user:
				try:
					ret.extend(user_strips(self.db.get_user(d),self.db,now,self.cache))
				except database.NoSuchUser:
					raise Exception("No user found "+d)
			
		if strips==None and user==None:
			raise Exception, "No strips or users!"
		return ret

	def store_err(self,strip,level,msg):
		print msg
		msg = strip+" : "+str(msg)
		self.errors.append((level,msg))

	def get_url(self,strip,url,ref=None):
		try:
			return self.cache.get_mult(url,ref,count=2)
		except urlcache.CacheError,err:
			self.store_err(strip,3,err)
			return None

	def update(self,directory,strips=None,user=None,now=DateManip(), all_users=False):
		self.now = now
		self.errors = []
		c = CalcWeek(self.now)
		print self.now.strftime("%Y/%m/%d")

		if not os.path.exists(directory):
			os.makedirs(directory)
		htmlout = file(os.path.join(directory,"index.html"),'w')
		newindex = self.now.strftime("%Y-%m-%d.html")
		files = os.listdir(directory)
		files.sort()
		files.reverse()
		prev=""
		for l in files:
			if l=="index.html" or l==newindex:
				continue
		
			p = os.path.join(directory,l)
			if os.path.isfile(p):
				prev = l
				addfwd = file(p,'r')
				content = addfwd.read()
				content = content.replace("<!-- FWD LINK --><br />","<a href=\""+newindex+"\">Next day</a><br />")
				content = content.replace("<!-- FWD LINK -->","<a href=\""+newindex+"\">Next day</a><br />")
				addfwd.close()
				addfwd = file(p,'w+')
				addfwd.write(content)
				addfwd.close()
				break
		
		htmlout.write(self.now.strftime("<title>Comics page for %d/%m/%Y</title>\n"))
		htmlout.write(self.now.strftime("<h3>Comics page for %d/%m/%Y</h3>\n"))
		if prev!="":
			htmlout.write("<a href=\""+prev+"\">Previous day</a>")
		htmlout.write(" <!-- FWD LINK -->")
		if prev!="":
			htmlout.write("<br />\n")
		
		dirs = [x for x in os.listdir(directory) if os.path.isdir(os.path.join(directory,x))]
		dirs.sort()
		
		last = self.now.mod_days(-self.maxdays)

		l = last.strftime("%Y-%m-%d")
		lastdir = None
		for d in dirs:
			if d<l:
				lastdir = d
			else:
				break
			
		dirs.reverse()
		print "dirs",dirs,lastdir

		for (g,search) in self.get_strips(strips,user, all_users=all_users):
			print "Running",g.name, "("+g.days+")"
			last = DateManip(c.get_last_day(g.days))
			curr = self.now.copy()
			found = []
			oldstuff = False
			while curr>=last:
				folder = os.path.join(directory,curr.strftime("%Y-%m-%d"))
				if os.path.exists(folder):
					files = os.listdir(folder)
					print "Checking",folder
					for f in files:
						if f[:len(g.name)] == g.name:
							found.append(os.path.join(curr.strftime("%Y-%m-%d"),f))
							if self.now != curr:
								oldstuff = True
							
					if len(found)!=0:
						break
				else:
					print "no such folder",folder
				curr = curr.mod_days(-1)
			if lastdir!=None:
				removes = []
				found_last = False
				print "cleanup",dirs
				for d in dirs:
					folder = os.path.join(directory,d)
					files = os.listdir(folder)
					#print "Checking for deletable",folder
					for f in files:
						if f[:len(g.name)] == g.name:
							if found_last and d<lastdir:
								print "removing",os.path.join(folder,f)
								os.unlink(os.path.join(folder,f))
							if not found_last:
								print "found",folder
							found_last = True
							
			if len(found)==0:
				get = []
				tried = 0
				for s in get_searches(g,search):
					(type,data) = s.retr(now)
					print "type",type
					if type=="generate":
						print "Getting (image)",data
						self.cache.set_varying(data,ref=g.homepage)
						get = [self.get_url(g.name,data,ref=g.homepage)]
					else: # type == "search"
						if self.debug>=4:
							print "data",data
						(pattern,baseurl,searchpage) = data
						print "Getting (searchpage)",searchpage
						page = self.get_url(g.name,searchpage,ref=searchpage)
						if page!=None:# and page.status != urlcache.URLCache.STAT_UNCHANGED:
							print "Searching for",pattern
							assert pattern!=""
							retr = re.findall("(?i)"+pattern,page.content)
							if self.debug>=4:
								print page.content

              # remove duplicate images/paths
							dups = set([])
							keep = []
							for item in retr:
								if item not in dups:
										dups.add(item)
										keep.append(item)
							retr = keep

							for x in range(len(retr)):
								if not s.look.HasField("index") or s.look.index == x+1:
									r = retr[x]
									
									print "Getting (image from search)",urlparse.urljoin(baseurl,r)
									get.append(self.get_url(g.name,urlparse.urljoin(baseurl,r),ref=searchpage))
							tried += 1
						else:
							print "Got no page at all!"

					get = filter(lambda x:x!=None,get)
					if get!=[]:
						break
				
				if get!=[]:
					old = []
					files = os.listdir(directory)
					files.sort()
					files.reverse()
					nowfolder = self.now.strftime("%Y-%m-%d")
					for l in files:
						if l==nowfolder:
							continue
						folder = os.path.join(directory,l)
						if os.path.isdir(folder):
							files = os.listdir(folder)
							print "Looking for old in",folder
							for f in files:
								if f[:len(g.name)] == g.name:
									old.append(os.path.join(folder,f))
							if old!=[]:
								break

					if old != [] and len(old)==len(get):
						for o in range(len(old)):
							print "Comparing",old[o],"and",get[o].url

							if len(get[o].content) != os.stat(old[o]).st_size:
								break
						else:
							self.store_err(g.name,1,"Got the old stuff in "+ folder)
							print ""
							continue
				
					index = 0
					folder = os.path.join(directory,self.now.strftime("%Y-%m-%d"+os.sep))

					for u in get:
						if g.HasField("ext"):
							ext = g.ext
						else:
							if u.mime[0]!="image" and u.mime[0] !="application":
								self.store_err(g.name,2,"Getting for <a href=\""+g.homepage+"\">"+g.homepage+"</a> found us a %s/%s (non-image) while retrieving %s"%(u.mime[0],u.mime[1],u.url))
								continue
							if u.mime[1]=='jpeg':
								ext = 'jpg'
							elif u.mime[1]=='gif':
								ext = 'gif'
							elif u.mime[1]=='png':
								ext = 'png'
							elif u.mime[1]=='octet-stream':
								# FIXME: somewhat lame
								ext = 'gif'
							else:
								raise Exception, "Don't know extension " + str(u.mime)
						index +=1
						if not os.path.exists(folder):
							os.mkdir(folder)
						fname = folder+g.name+"-"+str(index)+"."+ext
						outfile = file(fname,'wb')
						outfile.write(u.content)
						outfile.close()
						found.append(self.now.strftime("%Y-%m-%d"+os.sep+g.name+"-"+str(index)+"."+ext))
				elif tried>0: # if get == []
					self.store_err(g.name,2,"Failed to get anything for <a href=\""+g.homepage+"\">"+g.homepage+"</a>")

			if len(found)>0:
				print "We found",found
				if not oldstuff:
					htmlout.write("<h3><a href=\""+g.homepage+"\">"+g.desc+"</a></h3>\n")
					for f in found:
						if Image:
							dimensions = [x*g.zoom for x in Image.open(os.path.join(directory,f)).size]
							htmlout.write("<img src=\"%s\" width=\"%d\" height=\"%d\"/><br />\n"%(f.replace(os.sep,"/"),dimensions[0],dimensions[1]))
						else:
							htmlout.write("<img src=\"%s\" /><br />\n"%f.replace(os.sep,"/"))
					htmlout.write("<br />\n")
				else:
					self.store_err(g.name,1,"Got the old stuff in "+ folder)
			print ""
		self.errors.sort()
		for (l,e) in self.errors:
			if l>=self.debug:
				htmlout.write(str(l)+": "+e+"<br />\n")
			
		htmlout.close()
		for d in dirs:
			di = os.path.join(directory,d)
			if os.listdir(di)==[]:
				os.removedirs(di)
				if os.path.exists(os.path.join(directory,d+".html")):
					os.unlink(os.path.join(directory,d+".html"))
		htmlout = file(os.path.join(directory,"index.html"),'r')
		dated = file(os.path.join(directory,newindex),'w')
		dated.write(htmlout.read())
		dated.close()
		htmlout.close()
		self.cache.cleanup()
