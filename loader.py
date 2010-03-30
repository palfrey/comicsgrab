from google.protobuf.internal.containers import BaseContainer
from strips_pb2 import Class,User,Strip,Subsection,_TYPE
from re import split
from database import Sqlite as Database

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-d","--db",dest="database",default="comics.db",help="Set database to use")
parser.add_option("-u","--user",dest="user",default=False,action="store_true",help="Load user database")
(opts,args) = parser.parse_args()

if len(args)!=1:
	parser.error("Need a definitions file!")

db = Database(opts.database)
if opts.user:
	db.clear_users()
else:
	db.clear_strips()

deffile = args[0]
infile = open(deffile)
storage = []
for lineno,line in enumerate(infile):
	while line.find("#")<>-1:
		line = line[:line.find("#")-1]
	line = line.strip()
	if line == "":
		continue

	try:
		data = split('[ \t]',line,1)
		#print data 
		if storage == []:
			if data[0] == "user":
				storage.append(User())
			elif data[0] == "class":
				storage.append(Class())
			elif data[0] == "strip":
				storage.append(Strip())
			else:
				raise Exception,"Unknown block type '%s'"%data[0]
			storage[-1].name = data[1]
		elif data[0] == 'end':
			assert len(storage) == 1,storage
			db.add_section(storage[0])
			storage = []
		else:
			if data[0] == "subbeg":
				storage.append(storage[-1].subs.add())
			elif data[0] == "name":
				storage[-1].desc = data[1]
			elif data[0] == "subend":
				assert len(storage)>1
				storage = storage[:-1]
			elif data[0] == "include":
				storage[-1].include.extend(data[1].split(" "))
			else:
				if data[0][0] == "$":
					data[0] = "_var_"+data[0][1:]
				attr = getattr(storage[-1],data[0])
				if isinstance(attr,BaseContainer): # composite type, use append
					attr.append(data[1])
				else:
					if len(data)==1:
						data.append("")
					if data[0] in ("index","noperl"):
						data[1] = int(data[1])
					elif data[0] in ("zoom",):
						data[1] = float(data[1])
					elif data[0] == "type":
						data[1] = _TYPE.values_by_name[data[1]].number
					else:
						pass
					setattr(storage[-1],data[0],data[1])
	except:
		print "error at line number %d in file %s"%(lineno+1,deffile)
		raise
infile.close()
