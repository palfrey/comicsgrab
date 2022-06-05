#!/usr/bin/env python

# Author: Tom Parker <palfrey@tevp.net>
# Description: Docs rebuild script
# Requires: Docutils (http://docutils.sourceforge.net/)
# Hacked together from rst2html.py by David Goodger <goodger@users.sourceforge.net>

import locale
try:
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

try:
	from docutils.core import publish_file
except:
	print("You need docutils (http://docutils.sourceforge.net/)\n")
	raise
from .html import Writer

def rebuild(rst,php):
	read_txt = open(rst,'r')
	read_html = open(php,'w')
	html = Writer()
	publish_file(writer=html, source=read_txt, destination=read_html)

	read_html = open(php,'r')
	data = read_html.readlines()
	read_html.close()
	data.insert(0,"<script language=\"php\">$title=\"Comics Grabber\";$TOPDIR=\"../../\";include $TOPDIR.\"top.php3\";</script>")
	data.append("<script language=\"php\">include $TOPDIR.\"bottom.php3\";</script>")
	read_html = open(php,'w')
	read_html.writelines(data)
	read_html.close()

rebuild('readme.txt','index.php')
rebuild('strips.def.txt','strips.php')
