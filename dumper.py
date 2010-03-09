from sys import argv
import types
from google.protobuf.internal.containers import *

from database import Sqlite as Database

def print_pb_indent(pb,indent="\t"):
	for (fd,val) in pb.ListFields():
		if fd.name == "name":
			continue
		if isinstance(val,RepeatedScalarFieldContainer):
			val = " ".join(val)
		elif isinstance(val,RepeatedCompositeFieldContainer):
			for v in val:
				print "%s%s"%(indent,fd.name)
				print_pb_indent(v,indent+"\t")
				print "%send"%indent
			continue
		elif fd.enum_type!=None:
			val = fd.enum_type.values_by_number[val].name
		elif isinstance(val,unicode) or isinstance(val,long) or isinstance(val,str) or isinstance(val,float):
			pass
		elif isinstance(val,bool):
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

db = Database()
for user in db.list_users():
	print_pb("group",db.get_user(user))
for cl in db.list_classes():
	print_pb("class",db.get_class(cl))
for s in db.list_strips():
	print_pb("strip",db.get_strip(s))

