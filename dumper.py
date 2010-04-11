from sys import argv
import types
from google.protobuf.internal.containers import *

from database import Sqlite as Database
from optparse import OptionParser

def print_pb_indent(pb,indent="\t"):
	if opts.user:
		fields = pb.DESCRIPTOR.fields
	else:
		fields = [x[0] for x in pb.ListFields()]

	for fd in fields:
		if fd.name == "name":
			continue
		val = getattr(pb,fd.name)
		if isinstance(val,RepeatedScalarFieldContainer):
			val = " ".join(val)
		elif isinstance(val,RepeatedCompositeFieldContainer):
			use = fd.name
			end = "end"
			if use == "subs":
				use = "subbeg"
				end = "subend"
			for v in val:
				print "%s%s"%(indent,use)
				print_pb_indent(v,indent+"\t")
				print "%s%s"%(indent,end)
			continue
		elif fd.enum_type!=None:
			val = fd.enum_type.values_by_number[val].name
		elif isinstance(val,unicode) or isinstance(val,long) or isinstance(val,str) or isinstance(val,float):
			pass
		elif isinstance(val,bool):
			pass
		elif isinstance(val,int):
			val = int(val)
		else:
			print dir(fd)
			print dir(fd.enum_type)
			raise Exception,(fd.name,type(val),fd,getattr(pb,fd.name))
		if fd.name.find("_var_")==0:
			name = "$%s"%fd.name[len("_var_"):]
		else:
			name = fd.name
		print "%s%s %s"%(indent,name,str(val))

def print_pb(kind,pb):
	print "%s %s"%(kind,pb.name)
	print_pb_indent(pb)
	print "end\n"

print """# Comics Grabber by Tom Parker <palfrey@tevp.net>
# http://tevp.net
#
# Comics definition file (partially derived from the strips.def at
# http://dailystrips.sf.net)
#
# Released under the GPL Version 2 (http://www.gnu.org/copyleft/gpl.html)
"""

parser = OptionParser()
parser.add_option("-u","--user",dest="user",default=False,action="store_true",help="Dump user database")
parser.add_option("-d","--db",dest="db",default="comics.db",help="Set database to use")
parser.add_option("-m","--module",dest="db_module",default="Sqlite",help="Specify database module")
(opts,args) = parser.parse_args()

if len(args) != 0:
	parser.error("dumper doesn't take any non-option arguments!")

globals()['Database'] = getattr(__import__('database',globals(),locals(),[opts.db_module],-1),opts.db_module)

if opts.db_module == "Sqlite":
	db = Database(opts.db)
else:
	db = Database()
if opts.user:
	for user in db.list_users():
		print_pb("user",db.get_user(user))
else:
	for cl in db.list_classes():
		print_pb("class",db.get_class(cl))
	for s in db.list_strips():
		print_pb("strip",db.get_strip(s))

