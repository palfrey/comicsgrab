#!/usr/bin/python
# Comics Grabber by Tom Parker <palfrey@tevp.net>
# http://tevp.net
#
# Perl RE evaluator for Python
# Handles <code: sections, but not very well
#
# Released under the GPL Version 2 (http://www.gnu.org/copyleft/gpl.html)

import time,string,re,math,sys

class PerlREEval:
	def __init__(self, now):
		self.now = now

	def eval_perl(self,expr):
		#now = self.now
		ret = expr

		found = True
		while found:
			found = False
			for (fd,v) in self.look.ListFields():
				k = fd.name
				if k.find("_var_") == 0:
					k = "$%s"%k[len("_var_"):]
				if ret.find("$"+k)!=-1:
					found = True
					ret = ret.replace("$"+k,getattr(self.look,k))
				if k[0] == '$' and ret.find(k)!=-1:
					found = True
					ret = ret.replace(k,getattr(self.look,"_var_%s"%k[1:]))

			k = self.look.DESCRIPTOR.name.lower()
			if ret.find("$"+k)!=-1:
				found = True
				assert self.look.name!="",[(fd.name,val) for (fd,val) in self.look.ListFields()]
				ret = ret.replace("$"+k,self.look.name)
	
		local_vars = {}
		funcs = {}
		while ret.find("<code:")!=-1:
			#print ret
			sec = re.search("(.*?)(?<!\\\\)<code:(.*?)(?<!\\\\)>(.*)",ret)
			if sec == None:
				break
			lines = re.split(";",sec.group(2))
			#print "lines"+str(lines)
			local_vars = {"time_today":now.secs(),"localtime_today":now.gmtime()}
			funcs = {"strftime":"time.strftime","localtime":"time.gmtime","floor":"math.floor"}
			i = -1
			z = 0
			while i<len(lines)-1:
				i += 1
				l = lines[i]
				l = l.strip()
				if z == 0:
					for k in funcs.keys():
						#print "lookfor","(?<!@)(?<!"+funcs[k]+")"+k,funcs[k]
						l = re.sub("(?<!@)(?<!"+funcs[k]+")"+k, funcs[k], l)
				else:
					z = 0

				if l.startswith("use "):
					continue
				if l.startswith("my "):
					l = l[3:]
				if l.startswith("my$"):
					l = l[2:]
				l = l.replace("\".\"","")
				l = l.replace("\\>",">")
				l = re.sub("\$(\w*)\+\+",r"$\1=$\1 + 1",l)
				ite = re.search("(.*?)(?<!g)if(.*)",l) # if-the-else - will prolly match other things, but we're not doing proper perl!
				if ite!=None:
					#print ite.groups()
					expr = ite.group(2).strip()
					ev = self.exp_perl(expr,local_vars,funcs)
					if int(ev)!=0:
						#print "ev:"+str(ev)
						r = self.expr_perl(ite.group(1).strip(),local_vars,funcs)
						if r!=None:
							l = r
					else:
						l = ""
					#raise Exception,"did ite, what now?"
					if i!=len(lines)-1:
						continue
				else:
					wloop = re.search("while([^{]*?){([^}]*?)}",l) # bad while loop regexp...
					if wloop!=None:
						#print wloop.groups()
						expr = wloop.group(1).strip()
						
						orig = expr
						ev = self.exp_perl(expr,local_vars,funcs)
						while int(ev)!=0:
							#print "ev:"+str(ev),expr
							r = self.expr_perl(wloop.group(2).strip(),local_vars,funcs)
							expr = orig
							ev = self.exp_perl(expr,local_vars,funcs)
						#print "matched",wloop.group()
						lines[i] = l[len(wloop.group()):]
						#print "awl",lines[i]
						i -= 1
						z = 1
						continue
				if i==len(lines)-1: # and l[0]=='\"' and l[len(l)-1]=='\"':
					ret = self.exp_perl(l,local_vars,funcs)
					break
				self.expr_perl(l,local_vars,funcs)
			else:
				raise Exception, "didn't break!"
			#print sec.groups()
			#print ret
			ret = sec.group(1)+ret+sec.group(3)
			#print ret
			#raise Exception, "haven't finished code section"
		ret = self.expr_perl(ret,local_vars,funcs)
		return ret
			
				
	def expr_perl(self,l,local_vars,funcs):
		expr = re.search("\$([^ =]*?) *= *(.*)",l)
		if expr!=None: # i.e. we have an expression...
			exp = expr.group(2)
			local_vars[expr.group(1)] = self.exp_perl(exp,local_vars,funcs)
			#print "\"",local_vars[expr.group(1)],"\""
			try:
				if local_vars[expr.group(1)] == int(float(local_vars[expr.group(1)])):
					local_vars[expr.group(1)] = int(float(local_vars[expr.group(1)]))
			except ValueError: # really not a number
				pass
				
			#print "Evaled "+expr.group(1)+" to be equal to "+str(local_vars[expr.group(1)])+" - ("+exp+")"
		else:
			return self.exp_perl(l,local_vars,funcs)

	def exp_perl(self,exp,local_vars,funcs):
		if len(exp)==0:
			return exp
		
		found = True
		while found:
			found = False
			for k in local_vars.keys():
				if exp.find("$"+k)!=-1:
					found = True
					exp = exp.replace("$"+k,str(local_vars[k]))
				if exp.find("${"+k+"}")!=-1:
					found = True
					exp = exp.replace("${"+k+"}",str(local_vars[k]))
				if exp.find("@"+k)!=-1:
					found = True
					exp = exp.replace("@"+k,str(local_vars[k]))

		# Ye gods the below is kludgy... but I can't be arsed doing this better!

		#if exp[0]=='(' and exp[-1]==')':
		#	exp = exp[1:-1]
		equ = re.search("([^ =]*?) *== *(.*)",exp)
		if equ!=None: # we have an equality operation...
			exp = str(self.exp_perl(equ.group(1),local_vars,funcs) == self.exp_perl(equ.group(2),local_vars,funcs))
		equ = re.search("([^ !]*?) *!= *(.*)",exp)
		if equ!=None: # we have an non-equality operation...
			#print "ne",self.exp_perl(equ.group(1),local_vars,funcs)
			exp = str(self.exp_perl(equ.group(1),local_vars,funcs) != self.exp_perl(equ.group(2),local_vars,funcs))
		equ = re.search("([^ >]*?) *> *(.*)",exp)
		if equ!=None: # we have a greater than...
			exp = str(self.exp_perl(equ.group(1),local_vars,funcs) > self.exp_perl(equ.group(2),local_vars,funcs))
		if exp[0] == '\"' and exp[len(exp)-1] == '\"':
			exp = exp[1:-1]
		#print "exp_perl ret",exp,local_vars
		try:
			ret = self.now.strftime(str(eval(exp)))
		except SyntaxError:
			if exp.find("strftime")!=-1:
				print "(syntax) eval failed for",exp
				raise		
			ret = self.now.strftime(exp)

		except TypeError:
			if exp.find("strftime")!=-1:
				print "(type) eval failed for",exp
				raise
			ret = exp
		except:
			#print "eval failed for",exp, sys.exc_type
			ret = time.strftime(exp)
		try:
			if len(ret)>1 and ret[0]=='\\' and float(ret[1:]) == int(float(ret[1:])):
				ret = int(float(ret[1:]))
			elif float(ret) == int(float(ret)):
				ret = int(float(ret))
		except ValueError:
			pass
			
		return ret
