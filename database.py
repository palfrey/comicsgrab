try:
	import sqlite3 as sqlite
except ImportError:
	sqlite = None
try:
	import MySQLdb
except ImportError:
	MySQLdb = None

from strips_pb2 import Class,Strip,Subsection,User

class NoSuchStrip(Exception):
	pass

class NoSuchUser(Exception):
	pass

class NoSuchClass(Exception):
	pass

class Database:
	prefix = ""

	def list_users(self):
		return self._list("users")

	def list_classes(self):
		return self._list("classes")

	def list_strips(self):
		return self._list("strips")

	def list_user_strips(self, user):
		return list(user.include)
	
	def clear_strips(self):
		self._clear_tables(("strips","classes"))
		
	def clear_users(self):
		self._clear_tables(("users",))

	def add_section(self, s):
		if isinstance(s,Strip):
			self._cur.execute("insert into "+self.prefix+"strips values ("+self.replace_str+","+self.replace_str+","+self.replace_str+","+self.replace_str+")",(s.name,s.desc,s.homepage,self.binary(s.SerializeToString())))
			self._con.commit()
		elif isinstance(s,User):
			data = (s.name,self.binary(s.SerializeToString()))
			self._cur.execute("insert into "+self.prefix+"users values ("+self.replace_str+","+self.replace_str+")",data)
			self._con.commit()
		
		elif isinstance(s,Class):
			self._cur.execute("insert into "+self.prefix+"classes values ("+self.replace_str+","+self.replace_str+","+self.replace_str+")",(s.name,s.desc,self.binary(s.SerializeToString())))
			self._con.commit()
		else:
			raise Exception,(s,type(s))
	
	def _clear_table(self,table):
		try:
			self._cur.execute("drop table %s"%(self.prefix+table))
		except sqlite.OperationalError,e:
			if e.message == "no such table: %s"%table:
				pass
			else:
				raise

	def _clear_tables(self, tables):
		for table in (tables):
			self._clear_table(table)
		self._con.commit()
		self._setup(tables)
	
	def _list(self, table):
		self._cur.execute("select name from %s order by name"%(self.prefix+table))
		return [x[0] for x in self._cur.fetchall()]

	def get_strip(self, strip):
		self._cur.execute("select pb from %sstrips where name='%s'"%(self.prefix,strip))
		f = self._cur.fetchall()
		if len(f)!=1:
			raise NoSuchStrip
		s = Strip()
		s.ParseFromString(f[0][0])
		return s

	def get_class(self, cl):
		self._cur.execute("select pb from %sclasses where name='%s'"%(self.prefix,cl))
		f = self._cur.fetchall()
		if len(f)!=1:
			raise NoSuchClass
		c = Class()
		c.ParseFromString(f[0][0])
		return c

	def get_user(self, user):
		self._cur.execute("select pb from "+self.prefix+"users where name="+self.replace_str+"",(user,))
		f = self._cur.fetchall()
		if len(f)!=1:
			print f
			raise NoSuchUser
		u = User()
		u.ParseFromString(f[0][0])
		return u

class MySQL(Database):
	replace_str = "%s"

	def __init__(self,database="comics", prefix="", user="comics", password="comics"):
		self.prefix = prefix
		self._con = MySQLdb.connect(user=user,passwd=password,db=database)
		self._cur = self._con.cursor()
		for table in ("users","strips","classes"):
			self._cur.execute("show tables like '%s'"%(self.prefix+table))
			if len(self._cur.fetchall())==0:
				self._setup((table,))

	def _setup(self, tables):
		for t in tables:
			if t == "users":
				self._cur.execute("create table %susers (name varchar(100) primary key, pb blob)"%self.prefix)
			elif t == "strips":
				self._cur.execute("create table %sstrips (name varchar(100) primary key, description varchar(200), homepage varchar(200), pb blob)"%self.prefix)
			elif t == "classes":
				self._cur.execute("create table %sclasses (name varchar(100) primary key, description varchar(200), pb blob)"%self.prefix)
			else:
				raise Exception, t
		self._con.commit()
	
	def binary(self, data):
		return data

class Sqlite(Database):
	replace_str = "?"

	def __init__(self,db="comics.db", prefix=""):
		self._con = sqlite.connect(db)
		self._con.text_factory = str
		self._cur = self._con.cursor()
		self.prefix = prefix
		self._cur.execute("select name from sqlite_master where type='table' and name='%sstrips'"%prefix)
		if len(self._cur.fetchall())==0:
			self._setup(("users","strips","classes"))
	
	def _setup(self, tables):
		for t in tables:
			if t == "users":
				self._cur.execute("create table %susers (name text primary key, pb blob)"%self.prefix)
			elif t == "strips":
				self._cur.execute("create table %sstrips (name text primary key, desc text,homepage text, pb blob)"%self.prefix)
			elif t == "classes":
				self._cur.execute("create table %sclasses (name text primary key, desc text,pb blob)"%self.prefix)
			else:
				raise Exception, t
		self._con.commit()

	def binary(self, data):
		return sqlite.Binary(data)
