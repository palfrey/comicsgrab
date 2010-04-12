#!/usr/bin/env python
from wsgiref.handlers import CGIHandler
from wsgiref.util import request_uri
output_folder = "output"

try:
	exception = BaseException
except NameError: # python <2.5
	exception = Exception

def comicsapp(environ, start_response):
	from cStringIO import StringIO
	ret = StringIO()
	try:
		from cgi import parse_qs
		from comicsgrab.date_manip import DateManip
		import traceback
		from time import localtime,strftime
		from os.path import join, abspath
		from glob import glob

		from comicsgrab.database import MySQL, Sqlite
		db = Sqlite("comicsgrab/comics.db")
		
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
				now = DateManip()
			else:
				now = DateManip.strptime("%Y-%m-%d", query['date'][0])
			folder = now.strftime("%Y-%m-%d")
			print >> ret, "Strips for <b>%s<b/>, %s<br />"%(user,folder)
			print >> ret, "<a href=\"?user=%s&date=%s\">Previous day</a><br />"%(user,now.mod_days(-1).strftime("%Y-%m-%d"))
			if now != DateManip().today():
				print >> ret, "<a href=\"?user=%s&date=%s\">Next day</a><br />"%(user,now.mod_days(+1).strftime("%Y-%m-%d"))
			today = join(output_folder,folder)
			user = db.get_user(query['user'][0])
			for strip in sorted(db.list_user_strips(user)):
				st = db.get_strip(strip)
				items = glob(join(today,"%s-*"%strip))
				if items != []:
					print >> ret, "<h3><a href=\"%s\">%s</a></h3>"%(st.homepage,st.name)
					for s in items:
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
