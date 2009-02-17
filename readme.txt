Comics Grabber by Tom Parker <palfrey@tevp.net>
======================================================
Released under the GPL Version 2 (http://www.gnu.org/copyleft/gpl.html) except 
where otherwise noted in source code.

Versions:
---------
Latest version of this script can be found at http://tevp.net/projects/comicsgrab

- 1.0 - First released version
- 2.0 - Added new retrieval module, additional definitions, converted to using RST_
- 2.1 - Significant updates to strips.def, automagic old strip removal
- 2.2 - More strips.def updates, fix date_manip.py for python 2.4 (thanks to JB McMichael)

What is it?
-----------
It's a set of scripts to grab webcomics to a local page for viewing. When your 
count of webcomics that you read on a semi-daily basis reaches anything about 
about 10 or so (I'm at 92 as of writing this...), you *need* a program like 
this. This is heavily based on Dailystrips_, which I used to use quite happily. 
However, as the author is not accepting my patches for multiple-image strips, I 
eventually got around to writing this. This program uses the strips.def from 
dailystrips_ (with a few additions of my own) - so any definitions you've created 
from that should just work with this, but none of the code has been copied from 
there (heck I'm writing this in Python, not Perl!). Additionally, old comics (>7 days
old) are automatically removed, unless they're the latest one of a comic, in order
to both clean up redundant comics and stop you from seeing another copy of the
same comic.

For the interested, here's my `current readlist`_

Requirements
------------
Either
 - Python_ 2.3 (or above) for the asyncchat module that is included in 2.3
or
 - PycUrl_ in combination with Python_. Has been tested on 2.2, but may work for earlier versions. Reports/bug fixes are welcomed!

How do I use it?
----------------
Get it from here_ and use as follows:

Usage: python grabber.py [-d <debug level>] [-f <strips define file> ] [-c <cache dir>] [-g <group to get>]* [-s <strip to get>]* (-h/<output dir>/listme)

Parameters
~~~~~~~~~~
strips define:
	Location of the strips define file (defaults to ./strips.def). Documentation for the `format of strip files`_ is also available
cache dir:
	Location of the page cache folder - will be created if doesn't already exist (defaults to ./cache)
debug level (prints messages at this level and above):
 - 1 is random warnings (mostly old comic messages)
 - 2 is for when a comic page was retrieved, but the regexp couldn't be found
 - 3 is HTTP errors
 - 4 is *everything*
output dir:
	directory to put the output files into

-h prints this help message
'listme' prints out an HTML formatted list of the comics specified

For example::

	python grabber.py -g palfrey d:\www\comics

This would get the group of comics called "palfrey" and create the pages in 
d:\\www\\comics. That folder will contain an index.html, a file called 
YYYY-MM-DD.html and a folder called YYYY-MM-DD (replace Y's, M's and D's with 
current date, or old dates for archives). For more information on strips and 
groups read strips.def.txt and the strips.def provided. The cache dir is used 
to store the downloaded versions of the searched webpages, in order to determine 
whether we have a new comic or not. Only new comics will be displayed.

Effectively this is just the "local" mode from dailystrips, as this is how I 
like to view my comics, on a page just used by me on my computer.

Todo
----
 - Re-check old pages when the strips.def is updated
 - Better error messages when strip patterns fail
 - Use the urlgrab_ package rather than a modified copy


.. RST information, ignore if you're reading the .txt version
.. _RST: http://docutils.sourceforge.net/rst.html
.. _PycUrl: http://pycurl.sourceforge.net/
.. _Python: http://www.python.org
.. _Dailystrips: http://dailystrips.sourceforge.net/
.. _`format of strip files`: strips.php
.. _`current readlist`: readlist.php
.. _here: comicsgrab-2.2.tar.gz
.. _urlgrab: http://github.com/palfrey/urlgrab/
