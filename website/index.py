#!/usr/bin/env python
from wsgiref.handlers import CGIHandler
from wsgiref.util import request_uri

output_folder = "comicsgrab/output"

try:
	exception = BaseException
except NameError: # python <2.5
	exception = Exception

def comicsapp(environ, start_response):
	import traceback
	from cStringIO import StringIO
	ret = StringIO()
	try:
		from cgi import parse_qs
		from comicsgrab.date_manip import DateManip
		from time import localtime,strftime
		from os.path import join
		from glob import glob

		from comicsgrab.database import MySQL
		from comicsgrab import settings
		try:
			from PIL import Image
		except ImportError,e : # no PIL!
			Image = None
		db = MySQL(user=settings.user, password=settings.password, database=settings.database, prefix=settings.prefix)
		
		try:
			uri = request_uri(environ)
			if uri.find("?")!=-1:
				uri = uri[uri.find("?")+1:]

			query = parse_qs(uri)
		except KeyError:
			query = {}

		if 'user' not in query:
			print >> ret,  "Users:<br />"
			for user in db.list_users():
				print >> ret, "<a href=\"?user=%s\">%s</a><br />"%(user,user)
		else:
			user = query['user'][0]
			if 'date' not in query:
				now = today = DateManip().today()
			else:
				now = DateManip.strptime("%Y-%m-%d", query['date'][0])
				today = DateManip().today()
			folder = now.strftime("%Y-%m-%d")
			print >> ret, "Strips for <b>%s<b/>, %s<br />"%(user,folder)
			print >> ret, "<a href=\"?user=%s&date=%s\">Previous day</a><br />"%(user,now.mod_days(-1).strftime("%Y-%m-%d"))
			if now != today:
				print >> ret, "<a href=\"?user=%s&date=%s\">Next day</a><br />"%(user,now.mod_days(+1).strftime("%Y-%m-%d"))
			todaypath = join(output_folder,folder)
			user = db.get_user(user)
			for strip in sorted(db.list_user_strips(user)):
				st = db.get_strip(strip)
				items = glob(join(todaypath,"%s-*"%strip))
				if items != []:
					print >> ret, "<h3>"
					if st.homepage != "":
						print >> ret, "<a href=\"%s\">%s</a>"%(st.homepage,st.desc)
					else:
						print >> ret, st.desc
					print >> ret, "</h3>"

					onlyerror = len([x for x in items if not x.endswith("error")]) == 0
					for s in sorted(items):
						if s.endswith("error"):
							if onlyerror:
								print >> ret, open(s).read()
							continue
						if Image and st.zoom != 1.0:
							dimensions = [x*st.zoom for x in Image.open(s).size]
							print >> ret,"<img src=\"%s\" width=\"%d\" height=\"%d\"/><br />\n"%(s,dimensions[0],dimensions[1])
						else:
							print >> ret,"<img src=\"%s\" /><br />"%s
		status = '200 OK'
		response_headers = [('Content-type','text/html')]
		start_response(status, response_headers)
		return [ret.getvalue()]

	except exception, e:
		status = '500 Exception'
		response_headers = [('Content-type','text/html')]
		start_response(status, response_headers)
		tr = traceback.format_exc()
		return ["%s<br />\n<pre>%s</pre>"%(ret.getvalue(),tr)]

if __name__ == "__main__":
	CGIHandler().run(comicsapp)
