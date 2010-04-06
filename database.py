import sqlite3 as sqlite
from strips_pb2 import Class,Strip,Subsection,User

class NoSuchStrip(Exception):
	pass

class NoSuchUser(Exception):
	pass

class NoSuchClass(Exception):
	pass

class Database:
	pass

class Sqlite(Database):
	def __init__(self,db="comics.db"):
		self._con = sqlite.connect(db)
		self._cur = self._con.cursor()
		self._cur.execute("select name from sqlite_master where type='table' and name='strips'")
		if len(self._cur.fetchall())==0:
			self._setup(("users","strips","classes"))
	
	def _setup(self, tables):
		for t in tables:
			if t == "users":
				self._cur.execute("create table users (name text primary key, pb blob)")
			elif t == "strips":
				self._cur.execute("create table strips (name text primary key, desc text,homepage text, pb blob)")
			elif t == "classes":
				self._cur.execute("create table classes (name text primary key, desc text,pb blob)")
			else:
				raise Exception, t
		self._con.commit()

	def add_section(self, s):
		if isinstance(s,Strip):
			self._cur.execute("insert into strips values (?,?,?,?)",(s.name,s.desc,s.homepage,sqlite.Binary(s.SerializeToString())))
			self._con.commit()
		elif isinstance(s,User):
			data = (s.name,sqlite.Binary(s.SerializeToString()))
			self._cur.execute("insert into users values (?,?)",data)
			self._con.commit()
		
		elif isinstance(s,Class):
			self._cur.execute("insert into classes values (?,?,?)",(s.name,s.desc,sqlite.Binary(s.SerializeToString())))
			self._con.commit()
		else:
			raise Exception,(s,type(s))
	
	def _clear_table(self,table):
		try:
			self._cur.execute("drop table %s"%table)
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

	def clear_strips(self):
		self._clear_tables(("strips","classes"))
		
	def clear_users(self):
		self._clear_tables(("users",))
	
	def _list(self, table):
		self._cur.execute("select name from %s order by name"%table)
		return [x[0] for x in self._cur.fetchall()]

	def list_users(self):
		return self._list("users")

	def list_classes(self):
		return self._list("classes")

	def list_strips(self):
		return self._list("strips")

	def list_user_strips(self, user):
		return list(user.include)

	def get_strip(self, strip):
		self._cur.execute("select pb from strips where name='%s'"%strip)
		f = self._cur.fetchall()
		if len(f)!=1:
			raise NoSuchStrip
		s = Strip()
		s.ParseFromString(f[0][0])
		return s

	def get_class(self, cl):
		self._cur.execute("select pb from classes where name='%s'"%cl)
		f = self._cur.fetchall()
		if len(f)!=1:
			raise NoSuchClass
		c = Class()
		c.ParseFromString(f[0][0])
		return c

	def get_user(self, user):
		self._cur.execute("select pb from users where name=?",(user,))
		f = self._cur.fetchall()
		if len(f)!=1:
			print f
			raise NoSuchUser
		u = User()
		u.ParseFromString(f[0][0])
		return u
