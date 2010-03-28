#!/usr/bin/python
# Comics Grabber by Tom Parker <palfrey@tevp.net>
# http://tevp.net
#
# Date manipulation class - could be used for more general uses, but CalcWeek
# is fairly specific for Comics Grabber
#
# Released under the GPL Version 2 (http://www.gnu.org/copyleft/gpl.html)

import time,calendar,re

class DateManip:
	hour_mod = ( (time.altzone/60) + (time.daylight*60) ) / -60 # allow for gmt offsets and daylight

	@staticmethod
	def strptime(format, date):
		return DateManip(init_date=time.mktime(time.strptime(date,format)))

	def __init__(self,init_date=time.time()):
		tup = time.localtime(init_date)
		self.year = tup[0]
		self.month = tup[1]
		self.day = tup[2]
	
	def mod_days(self,num):
		ret = self.copy()
		ret.day += num
		while ret.day<1:
			ret.month -= 1
			ret._check_mon()
			ret.day += calendar.monthrange(ret.year, ret.month)[1]
		while ret.day>calendar.monthrange(ret.year, ret.month)[1]:
			ret.day -= calendar.monthrange(ret.year, ret.month)[1]
			ret.month += 1
			ret._check_mon()
		#print ret.year,ret.month,ret.day,calendar.monthrange(ret.year,ret.month)
		if ret.day>31:
			raise Exception
		return ret
	
	def _check_mon(self):
		while self.month<1:
			self.year -= 1
			self.month += 12
		while self.month>12:
			self.year += 1
			self.month -= 12

	def __cmp__(self, other):
		s1 = self.secs()
		s2 = other.secs()
		if s1==s2:
			return 0
		elif s1>s2:
			return 1
		else:
			return -1

	def dow(self):
		return calendar.weekday(self.year, self.month, self.day)
		
	def gmtime(self):
		return time.localtime(time.mktime((self.year,self.month,self.day,self.hour_mod,0,0,0,1,0)))
		
	def secs(self):
		return time.mktime(self.gmtime())
	
	def strftime(self,format):
		return time.strftime(format,self.gmtime())

	def copy(self):
		return DateManip(self.secs())

class CalcWeek:
	dow = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
	def __init__(self,curr = DateManip()):
		curr_day = curr.copy()
		days = [0 for x in range(7)]
		
		while True:
			if days[curr_day.dow()]!=0:
				break
			days[curr_day.dow()] = curr_day.secs()
			curr_day = curr_day.mod_days(-1)
		self.days = days

	def map_filter(self,x,y):
		if x:
			return y
		else:
			return x

	def get_last_day(self,inp):
		used = self.conv_days_string(inp)
		return max(map(self.map_filter,used,self.days))
	
	def conv_days_string(self,inp):
		bits = re.findall("([A-Za-z]+)|(-)|( )",inp)
		ret = []
		last = seq = 0
		for x in range(0,7):
			ret[x:x] = [0]
		for b in bits:
			b = max(b).lower()
			if b == ' ':
				continue
			if b == '-':
				seq = 1
				continue
				
			for i in range(len(self.dow)):
				if self.dow[i].lower().startswith(b):
					ret[i]=1
					if seq == 1:
						for j in range(last,i):
							ret[j] = 1
						seq = 0
					last = i
					break
			else:
				raise Exception, "Can't find DoW "+b
		if seq != 0:
			raise Exception, "No end of sequence!!"
		return ret
