import sqlite3 as sqlite
from strips_pb2 import Class,Group,Strip,Subsection,Config,User

class NoSuchStrip(Exception):
	pass

class NoSuchUser(Exception):
	pass

class NoSuchClass(Exception):
	pass

class Database:
	pass

class Sqlite(Database):
	def __init__(self):
		self._con = sqlite.connect("comics.db")
		self._cur = self._con.cursor()
		self._cur.execute("select name from sqlite_master where type='table' and name='strips'")
		if len(self._cur.fetchall())==0:
			self._setup()
	
	def _setup(self):
		self._cur.execute("create table strips (name text primary key, desc text,homepage text, pb blob)")
		self._cur.execute("create table users (name text primary key, pb blob)")
		self._cur.execute("create table classes (name text primary key, desc text,pb blob)")
		self._con.commit()

	def add_section(self, s):
		if isinstance(s,Strip):
			self._cur.execute("insert into strips values (?,?,?,?)",(s.name,s.desc,s.homepage,sqlite.Binary(s.SerializeToString())))
			self._con.commit()
		elif isinstance(s,Config):
			pass # ignore for now
		elif isinstance(s,Group):
			u = User()
			u.name = s.name
			u.include.extend(list(s.include))
			data = (u.name,sqlite.Binary(u.SerializeToString()))
			self._cur.execute("insert into users values (?,?)",data)
			self._con.commit()
		
		elif isinstance(s,Class):
			self._cur.execute("insert into classes values (?,?,?)",(s.name,s.desc,sqlite.Binary(s.SerializeToString())))
			self._con.commit()
		else:
			raise Exception,(s,type(s))
	
	def clear(self):
		for table in ("strips","groups","classes"):
			try:
				self._cur.execute("drop table %s"%table)
			except sqlite.OperationalError,e:
				if e.message == "no such table: %s"%table:
					pass
				else:
					raise
		
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
