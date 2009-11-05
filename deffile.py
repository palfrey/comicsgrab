#!/usr/bin/python
# Comics Grabber by Tom Parker <palfrey@tevp.net>
# http://tevp.net
#
# Released under the GPL Version 2 (http://www.gnu.org/copyleft/gpl.html)

import re,os,sys
from sections import *
from stat import ST_MTIME
from cPickle import load,dump
from date_manip import CalcWeek,DateManip
import urlcache
import urlparse

class ComicsDef:
	def __init__(self,deffile,cachedir,debug=0,proxy=None):
		pickle = deffile+".pickle"		
		
		self.debug = debug
		self.maxdays = 14
		self.proxy = proxy
		input = open(deffile)
		storage = None
		self.cache = urlcache.URLCache(cachedir,self.proxy)
		if os.path.exists(pickle) and os.stat(deffile)[ST_MTIME]<os.stat(pickle)[ST_MTIME]:
			out = load(file(pickle))
			self.classes = out.classes
			self.groups = out.groups
			self.strips = out.strips
			self.config = out.config
			return
		else:
			self.strips = []
			self.groups = []
			self.classes = []
			self.config = comic_config()

		line = input.readline()
		lineno = 1
		while line!="":
			if storage!=None:
				storage.lines.append(line)
			
			while line.find("#")<>-1:
				line = line[:line.find("#")-1]
			line = line.strip()
			if line == "":
				line = input.readline()
				lineno += 1
				continue

			try:
				data = re.split('[ \t]',line,1)
				#print data 
				if storage == None:
					if data[0] == "group":
						storage = comic_group(data[1])
						self.groups.append(storage)
					elif data[0] == "class":
						storage = comic_class(data[1])
						self.classes.append(storage)
					elif data[0] == "strip":
						storage = comic_strip(data[1])
						self.strips.append(storage)
					elif data[0] == "config":
						storage = self.config
					else:
						raise Exception,"Unknown block type '%s'"%data[0]
					if len(data)==2:
						storage.new_entry(data[0],data[1])
				elif data[0] == 'end':
					storage = None
				else:
					if len(data)==1:
						storage.new_entry(data[0],"")
					else:
						storage.new_entry(data[0],data[1])
			except:
				print "error at line number %d in file %s"%(lineno,deffile)
				raise
			line = input.readline()
			lineno+=1
		input.close()
		dump(self,file(pickle,'w'))

	def get_strips(self,strips=None,group=None,now=DateManip()):
		ret = []
		if strips!=None:
			for d in strips:
				for s in self.strips:
					if d == s.name:
						ret.append(s)
						s.gen_search(self.classes,self.now,self.cache)
						break
				else:
					raise Exception("No strip found "+d)
		if group!=None:
			for d in group:
				for g in self.groups:
					if d == g.name:
						ret.extend(g.get_strips(self.strips,self.classes,now,self.cache))
						break
				else:
					raise Exception("No group found "+d)
			
		if strips==None and group==None:
			raise Exception, "No strips or groups!"
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

	def update(self,directory,strips=None,group=None,now=DateManip()):
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
		
		last = self.now.copy()
		last.mod_days(-self.maxdays)

		l =last.strftime("%Y-%m-%d")
		lastdir = None
		for d in dirs:
			if d<l:
				lastdir = d
			else:
				break
			
		dirs.reverse()
		print "dirs",dirs,lastdir

		for g in self.get_strips(strips,group):
			print "Running",g.entries["name"], "("+g.entries["days"]+")"
			last = DateManip(c.get_last_day(g.entries["days"]))
			curr = self.now.copy()
			found = []
			oldstuff = False
			while curr.compare(last)!=-1:
				folder = os.path.join(directory,curr.strftime("%Y-%m-%d"))
				if os.path.exists(folder):
					files = os.listdir(folder)
					print "Checking",folder
					for f in files:
						if f[:len(g.entries["strip"])] == g.entries["strip"]:
							found.append(os.path.join(curr.strftime("%Y-%m-%d"),f))
							if self.now.compare(curr)!=0:
								oldstuff = True
							
					if len(found)!=0:
						break
				else:
					print "no such folder",folder
				curr.mod_days(-1)
			if lastdir!=None:
				removes = []
				found_last = False
				print "cleanup",dirs
				for d in dirs:
					folder = os.path.join(directory,d)
					files = os.listdir(folder)
					#print "Checking for deletable",folder
					for f in files:
						if f[:len(g.entries["strip"])] == g.entries["strip"]:
							if found_last and d<lastdir:
								print "removing",os.path.join(folder,f)
								os.unlink(os.path.join(folder,f))
							if not found_last:
								print "found",folder
							found_last = True
							
			if len(found)==0:
				get = []
				tried = 0
				#print g.get_searches()
				for s in g.get_searches(self.now):
					(type,data) = s.retr(now)
					if type=="generate":
						print "Getting (image)",data
						self.cache.set_varying(data,ref=g.entries["homepage"])
						get = [self.get_url(g.entries["strip"],data,ref=g.entries["homepage"])]
					else: # type == "search"
						if self.debug>=4:
							print "data",data
						(pattern,baseurl,searchpage) = data
						print "Getting (searchpage)",searchpage
						page = self.get_url(g.entries["strip"],searchpage,ref=searchpage)
						if page!=None:# and page.status != urlcache.URLCache.STAT_UNCHANGED:
							print "Searching for",pattern
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
								if not s.look.has_key("index") or int(s.look["index"]) == x+1:
									r = retr[x]
									
									print "Getting (image from search)",urlparse.urljoin(baseurl,r)
									get.append(self.get_url(g.entries["strip"],urlparse.urljoin(baseurl,r),ref=searchpage))
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
								if f[:len(g.entries["strip"])] == g.entries["strip"]:
									old.append(os.path.join(folder,f))
							if old!=[]:
								break

					if old != [] and len(old)==len(get):
						for o in range(len(old)):
							print "Comparing",old[o],"and",get[o].url

							if len(get[o].content) != os.stat(old[o]).st_size:
								break
						else:
							self.store_err(g.entries["strip"],1,"Got the old stuff in "+ folder)
							print ""
							continue
				
					index = 0
					folder = os.path.join(directory,self.now.strftime("%Y-%m-%d"+os.sep))

					for u in get:
						if g.entries.has_key("ext"):
							ext = g.entries["ext"]
						else:
							if u.mime[0]!="image":
								self.store_err(g.entries["strip"],2,"Getting for <a href=\""+g.entries["homepage"]+"\">"+g.entries["homepage"]+"</a> found us a %s/%s (non-image) while retrieving %s"%(u.mime[0],u.mime[1],u.url))
								continue
								raise Exception, str(u.mime) + " isn't an image"
							if u.mime[1]=='jpeg':
								ext = 'jpg'
							elif u.mime[1]=='gif':
								ext = 'gif'
							elif u.mime[1]=='png':
								ext = 'png'
							else:
								raise Exception, "Don't know extension " + str(u.mime)
						index +=1
						if not os.path.exists(folder):
							os.mkdir(folder)
						fname = folder+g.entries["strip"]+"-"+str(index)+"."+ext
						outfile = file(fname,'wb')
						outfile.write(u.content)
						outfile.close()
						found.append(self.now.strftime("%Y-%m-%d"+os.sep+g.entries["strip"]+"-"+str(index)+"."+ext))
				elif tried>0: # if get == []
					self.store_err(g.entries["strip"],2,"Failed to get anything for <a href=\""+g.entries["homepage"]+"\">"+g.entries["homepage"]+"</a>")

			if len(found)>0:
				print "We found",found
				if not oldstuff:
					htmlout.write("<h3><a href=\""+g.entries["homepage"]+"\">"+g.entries["name"]+"</a></h3>\n")
					for f in found:
						htmlout.write("<img src=\""+f.replace(os.sep,"/")+"\" /><br />\n")
					htmlout.write("<br />\n")
				else:
					self.store_err(g.entries["strip"],1,"Got the old stuff in "+ folder)
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
