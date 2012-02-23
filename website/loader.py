#!/usr/bin/env python
from wsgiref.handlers import CGIHandler
from wsgiref.util import request_uri

try:
	exception = BaseException
except NameError: # python <2.5
	exception = Exception

def comicsapp(environ, start_response):
	import traceback
	from cStringIO import StringIO
	ret = StringIO()
	try:
		from comicsgrab.database import MySQL
		from comicsgrab.loader import load_data
		from comicsgrab import settings
		db = MySQL(user=settings.user, password=settings.password, database=settings.database, prefix=settings.prefix)

		print >> ret, load_data(db, False, "comicsgrab/strips.def")
		print >> ret, load_data(db, True, "comicsgrab/users.def")

		status = '200 OK'
		response_headers = [('Content-type','text/html')]
		start_response(status, response_headers)
		return [ret.getvalue()]

	except exception, e:
		tr = traceback.format_exc()
		ret = "%s<br />\n<pre>%s</pre>"%(ret.getvalue(),tr)
		status = '500 Exception'
		response_headers = [('Content-type','text/html')]
		start_response(status, response_headers)
		return [ret]

if __name__ == "__main__":
	CGIHandler().run(comicsapp)
