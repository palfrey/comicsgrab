from sys import argv
import types
from google.protobuf.internal.containers import *

from database import Sqlite as Database
from optparse import OptionParser

from os.path import join, dirname, exists
from os import mkdir

def print_pb_indent(fp, pb,indent="\t"):
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
				print >> fp, "%s%s"%(indent,use)
				print_pb_indent(fp, v,indent+"\t")
				print >> fp, "%s%s"%(indent,end)
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
		print >>fp, "%s%s %s"%(indent,name,str(val))

def print_pb(folder, pb):
	path = join(folder, pb.name)
	if not exists(folder):
		mkdir(folder)
	with open(path, "wb") as fp:
		print >> fp, "%s %s"%(pb.__class__.__name__.lower(),pb.name)
		print_pb_indent(fp, pb)
		print >> fp, "end"

parser = OptionParser()
parser.add_option("-u","--user",dest="user",default=False,action="store_true",help="Dump user database")
parser.add_option("-d","--db",dest="db",default="comics.db",help="Set database to use")
parser.add_option("-m","--module",dest="db_module",default="Sqlite",help="Specify database module")
(opts,args) = parser.parse_args()

if len(args) != 1:
	parser.error("Need folder")

folder = args[0]

globals()['Database'] = getattr(__import__('database',globals(),locals(),[opts.db_module],-1),opts.db_module)

if opts.db_module == "Sqlite":
	db = Database(opts.db)
else:
	db = Database()

if opts.user:
	for user in db.list_users():
		print_pb("user",db.get_user(user))
else:
	if not exists(folder):
		mkdir(folder)
	for cl in db.list_classes():
		print_pb(join(folder, "class"),db.get_class(cl))
	for s in db.list_strips():
		print_pb(join(folder, "strip"),db.get_strip(s))

