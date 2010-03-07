from google.protobuf.internal.containers import BaseContainer
from strips_pb2 import Class,Group,Strip,Subsection,Config,_TYPE
from re import split

from database import Sqlite as Database

db = Database()

deffile = "strips.def"
infile = open(deffile)
storage = []
strips = []
groups = []
classes = []
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
			if data[0] == "group":
				storage.append(Group())
				storage[-1].name = data[1]
				groups.append(storage[-1])
			elif data[0] == "class":
				storage.append(Class())
				storage[-1].name = data[1]
				classes.append(storage[-1])
			elif data[0] == "strip":
				storage.append(Strip())
				storage[-1].name = data[1]
				strips.append(storage[-1])
			elif data[0] == "config":
				storage.append(Config())
			else:
				raise Exception,"Unknown block type '%s'"%data[0]
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
						data[1] = data[1].decode("latin-1")
					setattr(storage[-1],data[0],data[1])
	except:
		print "error at line number %d in file %s"%(lineno+1,deffile)
		raise
infile.close()

#print db.list_user_strips(db.list_users()[-1])
print db.list_user_strips(db.get_user('palfrey'))
print db.get_strip('skinhorse')

