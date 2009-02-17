#!/usr/bin/python

# Author: Tom Parker <palfrey@bits.bris.ac.uk>
# Description: List rebuild script

import os
inlines = os.popen("python grabber.py -g palfrey listme")
data = inlines.readlines()
inlines.close()
#print "data",data
data.insert(0,"<script language=\"php\">$title=\"Comics read list\";$TOPDIR=\"../../\";include $TOPDIR.\"top.php3\";</script>\n<h3>Current comics read list (%d items)</h3>\n"%(len(data)-2))
data.append("<script language=\"php\">include $TOPDIR.\"bottom.php3\";</script>")
read_html = open('readlist.php','w')
read_html.writelines(data)
read_html.close()
