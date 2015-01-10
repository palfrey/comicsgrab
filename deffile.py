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
import settings
from time import sleep
from glob import glob
import urlgrab
from codecs import open

class ComicsDef:
	def __init__(self,deffile,cachedir,debug=0,proxy=None, db=None, module="Sqlite", archive = False):
		if module == "Sqlite":
			self.db = database.Sqlite(db)
		else:
			self.db = database.MySQL(user=settings.user, password=settings.password, database=settings.database, prefix=settings.prefix)
		self.debug = debug
		self.maxdays = 14
		self.proxy = proxy
		self.cache = urlcache.URLCache(cachedir,self.proxy, archive)

	def get_strips(self,strips=None,user=None,now=DateManip(),all_users=False):
		ret = []
		if strips!=None:
			for d in strips:
				try:
					s = self.db.get_strip(d)
					search = gen_search(s,self.db,now,self.cache)
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
		if level > 1:
			if not os.path.exists(self.directory):
				os.makedirs(self.directory)
			error_path = os.path.join(self.directory, "%s-error"%strip)
			with open(error_path, "a") as error_file:
				error_file.write("%d: %s"%(level, msg))
		msg = strip+" : "+str(msg)
		self.errors.append((level,msg))

	def get_url(self,strip,url,ref=None):
		try:
			return self.cache.get_mult(url,ref,count=2)
		except urlcache.CacheError,err:
			self.store_err(strip,3,err)
			return None
		except urlgrab.URLTimeoutError, err:
			self.store_err(strip,3,err)
			return None

	def makeext(self, u, g):
		if g.HasField("ext"):
			ext = g.ext
		else:
			if u.mime[0]!="image" and u.mime[0] !="application":
				self.store_err(g.name,2,"Getting for <a href=\""+g.homepage+"\">"+g.homepage+"</a> found us a %s/%s (non-image) while retrieving %s"%(u.mime[0],u.mime[1],u.url))
				raise Exception, (u.mime, u.url)
			if u.mime[1] in ('jpeg', 'jpg'):
				ext = 'jpg'
			elif u.mime[1]=='gif':
				ext = 'gif'
			elif u.mime[1]=='png':
				ext = 'png'
			elif u.mime[1]=='webp':
				ext = 'webp'
			elif u.mime[1]=='octet-stream':
				# FIXME: somewhat lame
				ext = 'gif'
			else:
				raise Exception, "Don't know extension " + str(u.mime)
		return ext

	def archive(self, directory, strips, now=DateManip()):
		assert len(strips) == 1
		self.errors = []
		g = self.db.get_strip(strips[0])
		search = gen_search(g,self.db,now,self.cache)
		if not os.path.exists(directory):
			os.makedirs(directory)
		self.directory = directory

		current = g.firstpage

		for s in get_searches(g, search):
			(type,data) = s.retr(now, archive=True)
			print "type",type
			if type=="generate":
				print "Getting (image)",data
				self.cache.set_varying(data,ref=current)
				get = [self.get_url(g.name,data,ref=current)]
			else: # type == "search"
				if self.debug>=4:
					print "data",data
				searchpage = data["searchpage"]
				assert len(searchpage)>0
				while True:
					print "Getting (searchpage) '%s'"% searchpage
					page = self.get_url(g.name,searchpage,ref=searchpage)
					if page==None:# and page.status != urlcache.URLCache.STAT_UNCHANGED:
						print "Got no page at all!"
						self.cache.remove(searchpage, searchpage)
						sleep(5)
					else:
						content = page.content
						if data["initialpattern"] != "":
							print "Initially searching for",data["initialpattern"]
							iretr = re.findall("(?i)"+data["initialpattern"],content)
							assert len(iretr) == 1 # other patterns not supported yet
							content = iretr[0]
							
						print "Searching for", data["searchpattern"]
						assert data["searchpattern"]!=""
						retr = re.findall("(?i)"+data["searchpattern"],content)
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
						
						if data["namepage"] != "":
							np = list(set(re.findall(data["namepage"], searchpage, re.IGNORECASE | re.DOTALL | re.MULTILINE)))
						elif data["namepattern"] != "":
							np = list(set(re.findall(data["namepattern"], content, re.IGNORECASE | re.DOTALL | re.MULTILINE)))
						else:
							raise Exception, ("No namepage or namepattern", data)
						open("dump","wb", "utf-8").write(content)
					
						assert len(np) >=1, (data["namepattern"], np)
						names = np

						for idx, name in enumerate(names):
							try:
								val = int(name)
								names[idx] = "%05d" % val
							except ValueError: # not a number
								pass

						print "names", names

						shortpaths = [os.path.join(directory, x) for x in names]
						missing = False
						for shortpath in shortpaths:
							if len(glob(shortpath + "*")) == 0:
								missing = True
								break
						if missing:
							while True:
								get = []

								for x in range(len(retr)):
									if not s.look.HasField("index") or s.look.index == x+1:
										r = retr[x]
										img = urlparse.urljoin(data["baseurl"],r)
										self.cache.remove(img, searchpage)
										print "Getting (image from search)", img
										get.append(self.get_url(g.name,img,ref=searchpage))

								get = [u for u in get if u != None]
								assert len(get) == len(names), (get, names)
								if len(get) > 0:
									break
								sleep(5)

							exts = [self.makeext(u,g) for u in get]
							comicpaths = ["%s.%s"%(x,y) for (x,y) in zip(shortpaths, exts)]
							for (comicpath, u) in zip(comicpaths, get):
								print comicpath
								if not os.path.exists(comicpath):
									file(comicpath, "wb").write(u.content)

						assert len(data["nextpattern"]) >0
						nextpage = list(set(re.findall(data["nextpattern"], content, re.IGNORECASE | re.DOTALL | re.MULTILINE)))
						assert len(nextpage) == 1, (nextpage, data["nextpattern"])
						searchpage = urlparse.urljoin(data["baseurl"], nextpage[0])

						#tried += 1

	def update(self,directory,strips=None,user=None,now=DateManip(), all_users=False):
		self.now = now
		self.directory = os.path.join(directory,self.now.strftime("%Y-%m-%d"+os.sep))
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
							
			if len([x for x in found if not x.endswith("-error")]) == 0:
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
						searchpage = data["searchpage"]
						assert searchpage != ""
						print "Getting (searchpage)",searchpage
						page = self.get_url(g.name,searchpage,ref=searchpage)
						if page!=None:# and page.status != urlcache.URLCache.STAT_UNCHANGED:
							content = page.content
							if data["initialpattern"] != "":
								print "Initially searching for",data["initialpattern"]
								iretr = re.findall("(?i)"+data["initialpattern"],content)
								assert len(iretr) == 1 # other patterns not supported yet
								content = iretr[0]
								
							print "Searching for",data["searchpattern"]
							assert data["searchpattern"]!=""
							retr = re.findall("(?i)"+data["searchpattern"],content)
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
									
									print "Getting (image from search)",urlparse.urljoin(data["baseurl"],r)
									get.append(self.get_url(g.name,urlparse.urljoin(data["baseurl"],r),ref=searchpage))
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
						ext = self.makeext(u, g)
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
					onlyerror = len([x for x in found if not x.endswith("error")]) == 0
					for f in found:
						if f.endswith("error"):
							if onlyerror:
								htmlout.write(open(os.path.join(directory,f)).read())
							continue
						if Image:
							try:
								dimensions = [x*g.zoom for x in Image.open(os.path.join(directory,f)).size]
								htmlout.write("<img src=\"%s\" width=\"%d\" height=\"%d\"/><br />\n"%(f.replace(os.sep,"/"),dimensions[0],dimensions[1]))
								continue
							except:
								pass # assume something PIL can't cope with
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
