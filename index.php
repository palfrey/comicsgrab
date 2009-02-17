<script language="php">$title="Comics Grabber";$TOPDIR="../../";include $TOPDIR."top.php3";</script><h1 class="title">Comics Grabber by Tom Parker &lt;<a class="reference" href="mailto:palfrey&#64;tevp.net">palfrey&#64;tevp.net</a>&gt;</h1>
<p>Released under the GPL Version 2 (<a class="reference" href="http://www.gnu.org/copyleft/gpl.html">http://www.gnu.org/copyleft/gpl.html</a>) except
where otherwise noted in source code.</p>
<div class="section">
<h1><a id="versions" name="versions">Versions:</a></h1>
<p>Latest version of this script can be found at <a class="reference" href="http://tevp.net/projects/comicsgrab">http://tevp.net/projects/comicsgrab</a></p>
<ul class="simple">
<li>1.0 - First released version</li>
<li>2.0 - Added new retrieval module, additional definitions, converted to using <a class="reference" href="http://docutils.sourceforge.net/rst.html">RST</a></li>
<li>2.1 - Significant updates to strips.def, automagic old strip removal</li>
<li>2.2 - More strips.def updates, fix date_manip.py for python 2.4 (thanks to JB McMichael)</li>
</ul>
</div>
<div class="section">
<h1><a id="what-is-it" name="what-is-it">What is it?</a></h1>
<p>It's a set of scripts to grab webcomics to a local page for viewing. When your
count of webcomics that you read on a semi-daily basis reaches anything about
about 10 or so (I'm at 92 as of writing this...), you <em>need</em> a program like
this. This is heavily based on <a class="reference" href="http://dailystrips.sourceforge.net/">Dailystrips</a>, which I used to use quite happily.
However, as the author is not accepting my patches for multiple-image strips, I
eventually got around to writing this. This program uses the strips.def from
<a class="reference" href="http://dailystrips.sourceforge.net/">dailystrips</a> (with a few additions of my own) - so any definitions you've created
from that should just work with this, but none of the code has been copied from
there (heck I'm writing this in Python, not Perl!). Additionally, old comics (&gt;7 days
old) are automatically removed, unless they're the latest one of a comic, in order
to both clean up redundant comics and stop you from seeing another copy of the
same comic.</p>
<p>For the interested, here's my <a class="reference" href="readlist.php">current readlist</a></p>
</div>
<div class="section">
<h1><a id="requirements" name="requirements">Requirements</a></h1>
<dl class="docutils">
<dt>Either</dt>
<dd><ul class="first last simple">
<li><a class="reference" href="http://www.python.org">Python</a> 2.3 (or above) for the asyncchat module that is included in 2.3</li>
</ul>
</dd>
<dt>or</dt>
<dd><ul class="first last simple">
<li><a class="reference" href="http://pycurl.sourceforge.net/">PycUrl</a> in combination with <a class="reference" href="http://www.python.org">Python</a>. Has been tested on 2.2, but may work for earlier versions. Reports/bug fixes are welcomed!</li>
</ul>
</dd>
</dl>
</div>
<div class="section">
<h1><a id="how-do-i-use-it" name="how-do-i-use-it">How do I use it?</a></h1>
<p>Get it from <a class="reference" href="comicsgrab-2.2.tar.gz">here</a> and use as follows:</p>
<p>Usage: python grabber.py [-d &lt;debug level&gt;] [-f &lt;strips define file&gt; ] [-c &lt;cache dir&gt;] [-g &lt;group to get&gt;]* [-s &lt;strip to get&gt;]* (-h/&lt;output dir&gt;/listme)</p>
<div class="section">
<h2><a id="parameters" name="parameters">Parameters</a></h2>
<dl class="docutils">
<dt>strips define:</dt>
<dd>Location of the strips define file (defaults to ./strips.def). Documentation for the <a class="reference" href="strips.php">format of strip files</a> is also available</dd>
<dt>cache dir:</dt>
<dd>Location of the page cache folder - will be created if doesn't already exist (defaults to ./cache)</dd>
<dt>debug level (prints messages at this level and above):</dt>
<dd><ul class="first last simple">
<li>1 is random warnings (mostly old comic messages)</li>
<li>2 is for when a comic page was retrieved, but the regexp couldn't be found</li>
<li>3 is HTTP errors</li>
<li>4 is <em>everything</em></li>
</ul>
</dd>
<dt>output dir:</dt>
<dd>directory to put the output files into</dd>
</dl>
<p>-h prints this help message
'listme' prints out an HTML formatted list of the comics specified</p>
<p>For example:</p>
<pre class="literal-block">
python grabber.py -g palfrey d:\www\comics
</pre>
<p>This would get the group of comics called &quot;palfrey&quot; and create the pages in
d:\www\comics. That folder will contain an index.html, a file called
YYYY-MM-DD.html and a folder called YYYY-MM-DD (replace Y's, M's and D's with
current date, or old dates for archives). For more information on strips and
groups read strips.def.txt and the strips.def provided. The cache dir is used
to store the downloaded versions of the searched webpages, in order to determine
whether we have a new comic or not. Only new comics will be displayed.</p>
<p>Effectively this is just the &quot;local&quot; mode from dailystrips, as this is how I
like to view my comics, on a page just used by me on my computer.</p>
</div>
</div>
<div class="section">
<h1><a id="todo" name="todo">Todo</a></h1>
<blockquote>
<ul class="simple">
<li>Re-check old pages when the strips.def is updated</li>
<li>Better error messages when strip patterns fail</li>
<li>Use the <a class="reference" href="http://tevp.net/projects/darcs/darcs.php/urlgrab">urlgrab</a> package rather than a modified copy</li>
</ul>
</blockquote>
<!-- RST information, ignore if you're reading the .txt version -->
</div>
<script language="php">include $TOPDIR."bottom.php3";</script>