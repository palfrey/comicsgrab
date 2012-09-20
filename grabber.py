#!/usr/bin/python
# Comics Grabber by Tom Parker <palfrey@tevp.net>
# http://tevp.net/projects/comicsgrab/
#
# Released under the GPL Version 2 (http://www.gnu.org/copyleft/gpl.html)

 
from deffile import ComicsDef
from date_manip import DateManip
from optparse import OptionParser

proxy = None

parser = OptionParser(usage="%prog [options] (<output directory>)")
parser.add_option("-d","--debug",help="Debug level (default is 2).\n1 is random warnings (mostly old comic messages)\n2 is for when a comic page was retrieved, but the regexp couldn't be found\n3 is HTTP errors\n4 is *everything*", dest="debug", default=2, type="int")
parser.add_option("-f", dest="strips", default="strips.def", help="Strips definition file (default is strips.def)")
parser.add_option("-c","--cache",default="./cache", dest="cache",help="Cache directory (default is './cache')")
parser.add_option("-s","--comic",default =[],dest="comics", action="append", help="Add a strip to get")
parser.add_option("-u","--user",default =[],dest="users", action="append", help="Add a user to get")
parser.add_option("-p","--proxy",default=None, dest="proxy", help="Set proxy URL")
parser.add_option("--db", dest="db", default="comics.db")
parser.add_option("--listme", dest="listme", default=False, action="store_true", help="Prints out an HTML formatted list of the comics specified")
parser.add_option("--all-users", dest="all_users", default=False, action="store_true", help="Get comics for all enabled users")
parser.add_option("-m","--module",dest="db_module",default="Sqlite",help="Specify database module")
parser.add_option("--archive", dest="archive", default=False, action="store_true")

(opts, args) = parser.parse_args()

if not opts.listme and len(args)!=1:
	parser.error("Need an output directory!")

now = DateManip()
df = ComicsDef(opts.strips,opts.cache,debug=opts.debug,proxy=opts.proxy, db=opts.db, module=opts.db_module, archive = opts.archive)
if opts.listme:
	print "<ul>"
	for (x, search) in df.get_strips(opts.comics,opts.users,now=now):
		print "<li><a href=\""+x.homepage+"\">"+x.name+"</a></li>"
	print "</ul>"
elif opts.archive:
	df.archive(args[0],opts.comics)
else:
	df.update(args[0],user=opts.users,strips=opts.comics,now=now, all_users=opts.all_users)
