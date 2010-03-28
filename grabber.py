#!/usr/bin/python
# Comics Grabber by Tom Parker <palfrey@tevp.net>
# http://tevp.net/projects/comicsgrab/
#
# Released under the GPL Version 2 (http://www.gnu.org/copyleft/gpl.html)

 
from deffile import ComicsDef
from date_manip import DateManip
from optparse import OptionParser

proxy = None

parser = OptionParser(usage="%prog [options] (listme/<output directory>)\n'listme' prints out an HTML formatted list of the comics specified")
parser.add_option("-d","--debug",help="Debug level (default is 2).\n1 is random warnings (mostly old comic messages)\n2 is for when a comic page was retrieved, but the regexp couldn't be found\n3 is HTTP errors\n4 is *everything*", dest="debug", default=2, type="int")
parser.add_option("-f", dest="strips", default="strips.def", help="Strips definition file (default is strips.def)")
parser.add_option("-c","--cache",default="./cache", dest="cache",help="Cache directory (default is './cache')")
parser.add_option("-s","--comic",default =[],dest="comics", action="append", help="Add a strip to get")
parser.add_option("-g","--group",default =[],dest="groups", action="append", help="Add a group to get")
parser.add_option("-p","--proxy",default=None, dest="proxy", help="Set proxy URL")
parser.add_option("--db", dest="db", default="comics.db")

(opts, args) = parser.parse_args()

if len(args)!=1:
	parser.error("Need *one* arg")

now = DateManip()
#now.mod_days(-1)
df = ComicsDef(opts.strips,opts.cache,debug=opts.debug,proxy=opts.proxy, db=opts.db)
if args[0] == "listme":
	print "<ul>"
	for x in df.get_strips(opts.comics,opts.groups,now=now):
		print "<li><a href=\""+x.entries["homepage"]+"\">"+x.entries["name"]+"</a></li>"
	print "</ul>"
else:
	df.update(args[0],group=opts.groups,strips=opts.comics,now=now)
