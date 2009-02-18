#!/usr/bin/python
# Comics Grabber by Tom Parker <palfrey@tevp.net>
# http://tevp.net/projects/comicsgrab/
#
# Released under the GPL Version 2 (http://www.gnu.org/copyleft/gpl.html)

def usage():
	print "Usage: "+sys.argv[0]+" [-d <debug level>] [-f <strips define file> ] [-c <cache dir>] [-p <proxy url>] [-g <group to get>]* [-s <strip to get>]* (-h/<output dir>/listme)"
	print "Default values are:"
	print "\tstrips define: ./strips.def"
	print "\tcache dir:     ./cache"
	print "\tdebug level:	2 (prints messages at this level and above)\n"
	print "\t\t\t1 is random warnings (mostly old comic messages)"
	print "\t\t\t2 is for when a comic page was retrieved, but the"
	print "\t\t\t regexp couldn't be found"
	print "\t\t\t3 is HTTP errors"
	print "\t\t\t4 is *everything*"
	print "-h prints this help message"
	print "'listme' prints out an HTML formatted list of the comics specified"
	print ""
	print "Example: python "+sys.argv[0]+" -g palfrey d:\www\comics"
 
from deffile import ComicsDef
from date_manip import DateManip
import getopt,sys

strips = "strips.def"
cache = "./cache"
groups = []
comics = []
debug = 2
proxy = None

try:
	opts, args = getopt.getopt(sys.argv[1:], "d:f:c:g:hs:p:")
except getopt.GetoptError:
	# print help information and exit:
	usage()
	sys.exit(2)

for o, a in opts:
	if o in ("-h",):
		usage()
		sys.exit()
	if o in ("-f",):
		strips = a
	if o in ("-c",):
		cache = a
	if o in ("-g",):
		groups.append(a)
	if o in ("-s",):
		comics.append(a)
	if o in ("-d",):
		debug = int(a)
	if o in ("-p",):
		proxy = a

if len(args)!=1:
	usage()
	sys.exit(2)

now = DateManip()
#now.mod_days(-1)
df = ComicsDef(strips,cache,debug=debug,proxy=proxy)
if args[0] == "listme":
	print "<ul>"
	for x in df.get_strips(comics,groups,now=now):
		print "<li><a href=\""+x.entries["homepage"]+"\">"+x.entries["name"]+"</a></li>"
	print "</ul>"
else:
	df.update(args[0],group=groups,strips=comics,now=now)
