from google.protobuf.internal.containers import BaseContainer
from .strips_pb2 import Class,User,Strip,_TYPE
from re import split
from . import database

def loader(infile, deffile):
	storage = []
	for lineno,line in enumerate(infile):
		while line.find("#")!=-1:
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
					raise Exception("Unknown block type '%s'"%data[0])
				storage[-1].name = data[1]
			elif data[0] == 'end':
				assert len(storage) == 1,storage
				yield storage[0]
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
						if data[0] in ("index",):
							data[1] = int(data[1])
						elif data[0] in ("zoom",):
							data[1] = float(data[1])
						elif data[0] in ("enabled","noperl"):
							if data[1] in ("true","True"):
								data[1] = True
							else:
								data[1] = False
						elif data[0] == "type":
							data[1] = _TYPE.values_by_name[data[1]].number
						else:
							pass
						setattr(storage[-1],data[0],data[1])
		except StopIteration:
			return
		except Exception as e:
			print("error at line number %d in file %s"%(lineno+1,deffile))
			raise
	return

def load_data(db, user, deffile, clear = True):
	if clear:
		if user:
			db.clear_users()
		else:
			db.clear_strips()

	infile = open(deffile)

	for item in loader(infile, deffile):
		if db.has_section(item):
			db.delete_section(item)
		db.add_section(item)
	infile.close()

if __name__ == "__main__":
	from optparse import OptionParser

	parser = OptionParser()
	parser.add_option("-d","--db",dest="database",default="comics.db",help="Set database to use")
	parser.add_option("-u","--user",dest="user",default=False,action="store_true",help="Load user database")
	parser.add_option("-m","--module",dest="db_module",default="Sqlite",help="Specify database module")
	parser.add_option("--no-clear", dest="clear", default = True, action="store_false")
	(opts,args) = parser.parse_args()

	if len(args) == 0:
		parser.error("Need definitions file(s)!")

	db = database.get_db(opts.db_module,opts.database)
	
	clear = opts.clear
	for a in args:
		load_data(db, opts.user, a, clear = clear)
		clear = False
