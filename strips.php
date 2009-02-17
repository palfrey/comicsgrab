<script language="php">$title="Comics Grabber";$TOPDIR="../../";include $TOPDIR."top.php3";</script><h1 class="title">Readme for the strips.def</h1>
<p>The original version of this is copyright 2001-2003 Andrew Medico
&lt;<a class="reference" href="mailto:amedico&#64;amedico.dhs.org">amedico&#64;amedico.dhs.org</a>&gt;, and available at
<a class="reference" href="http://dailystrips.sourceforge.net/1.0.27/readme.defs.html">http://dailystrips.sourceforge.net/1.0.27/readme.defs.html</a></p>
<p>This file describes in further detail how the strips.def file is constructed.
Strips can be defined in one of two ways. Either standalone, or strips
can be provided the image URL by generating it (as from the current date) or by
searching a web page for a URL. Let's look at an example of generating first:</p>
<pre class="literal-block">
strip badtech
        name Badtech
        homepage http://www.badtech.com/
        type generate
        imageurl http://www.badtech.com/a/%-y/%-m/%-d.jpg
end
</pre>
<p>Note that all of the indenting here is strictly optional, but does make it
easier for people to read. In the &quot;strip&quot; line, we specify the short name of the
strip that will be used to refer to it on the command line. This must be
unique.</p>
<ul class="simple">
<li>&quot;name&quot; specifies the name of the strip to display in the HTML output.</li>
<li>&quot;homepage&quot; is the address of the strip's homepage, use for the link in the output.</li>
<li>&quot;type&quot; can be either &quot;generate&quot; or &quot;search&quot;. Here we are using &quot;generate&quot;
to generate a URL.</li>
<li>&quot;imageurl&quot; is the address of the image. You are allowed to use a number of
special variables. Single letters preceeded by the &quot;%&quot; symbol, such as
&quot;%Y&quot;, &quot;%d&quot;, &quot;%m&quot;, etc. are interpreted as date variables and passed to the
strftime function for conversion. &quot;date --help&quot; provides a reference that
is compatible. You can also use a &quot;$&quot; followed by any of the above
variables, such as &quot;$homepage&quot;. For the example, this will simply
subsititute &quot;<a class="reference" href="http://www.badtech.com">http://www.badtech.com</a>&quot; in place of &quot;$homepage&quot;.</li>
</ul>
<p>The other type of URL generation, searching, is as follows:</p>
<pre class="literal-block">
strip joyoftech
        name The Joy of Tech
        homepage http://www.joyoftech.com/joyoftech/
        type search
        searchpattern &lt;IMG.+?src=&quot;(joyimages/\d+\.gif)\&quot;
        baseurl http://www.joyoftech.com/joyoftech/
end
</pre>
<p>&quot;strip&quot;, &quot;name&quot;, and &quot;homepage&quot; all function as above. The difference is the
&quot;type search&quot; line and the lines that follow.</p>
<ul class="simple">
<li>&quot;searchpattern&quot; is a Python regular expression that must be written to match the strip's URL.
Not shown is &quot;searchpage&quot;. This is a URL to a web page and is only needed if the URL to the strip image is not found on the
homepage. The same special variables listed above for &quot;imageurl&quot; may also be
used here.</li>
<li>&quot;baseurl&quot; only needs to be specified if the &quot;searchpattern&quot; regular
expression does not match a full URL (that is, it does not start with <a class="reference" href="http://">http://</a>
and contain the host). If specified, it is prepended to whatever &quot;searchpattern&quot;
matched.</li>
</ul>
<p>The other method of specifying strips is to use classes. This method is used
when there are several strips provided by the same webserver that all have an
identical definition, except for some strip-specific elements. Classes work as
follows:</p>
<p>First, the class is declared:</p>
<pre class="literal-block">
class ucomics-srch
       homepage http://www.ucomics.com/%strip/view%1.htm
       type search
       searchpattern (/%1/(\d+)/%1(\d+)\.(gif|jpg))
       baseurl http://images.ucomics.com/comics
end
</pre>
<p>This is just like a strip definition, except &quot;class&quot; is the first line. The
value for &quot;class&quot; must be unique among other classes but will not conflict with
the names of strips. Strip-specific elements are specified using special
variables &quot;$x&quot;, where &quot;x&quot; is a number from 0 to 9. When the definition file is
parsed, these variables are retrieved from the strip definition, shown below:</p>
<pre class="literal-block">
strip calvinandhobbes
       name Calvin and Hobbes
       useclass ucomics-srch
       $1 ch
end
</pre>
<p>This definition is like a normal definition except the second line is &quot;useclass&quot;
followed by the name of the class to use. Below that, the strip-specific &quot;$x&quot;
variables must be specified. Values already declared in the class can be
overridden (if necessary) by simply specifying them in the strip definition.</p>
<p>&quot;days&quot; is another useful variable. This is a list of days on which you expect
the comic to update. This is a series of day names, either separated by spaces
for individual days, or by dashes for a sequence of days. The names can be
shortened to 2 letters if you wish (e.g. Mo, Tu, etc), and the script will
recognise any short form of a day name varying between 2 letters long and the
full length. If we already have what should be the most recent version of a
strip, we don't need to check the page again. If on the other hand, a strip has
not been updated when it should have been, all subsequent days are automatically
checked until the strip is updated. Default setting for days is &quot;Mo-Sun&quot; i.e.
every day.</p>
<dl class="docutils">
<dt>e.g. days Mo-Fri</dt>
<dd># Monday to Friday, not Saturday or Sunday.</dd>
</dl>
<p>Additional sections that can be added are &quot;subbeg/subend&quot; blocks. These define a
subsection of a definition that allow for strips that have varying definitions
e.g. keenspace. A good example of this is the Keenspace class:</p>
<pre class="literal-block">
class keenspace
        type search
        subbeg
                baseurl $homepage
                searchpattern document.write\('&lt;(?:IMG|img)[^S]*SRC=&quot;(/comics/$1[^\&quot;]*)&quot;
        subend
        subbeg
                searchpattern &lt;(?:IMG|img)[^S]*SRC=&quot;($homepage/comics/$1[^\&quot;]*)&quot;
        subend
        subbeg
                baseurl $homepage
                searchpattern &lt;(?:IMG|img)[^S]*SRC=&quot;(/comics/$1[^\&quot;]*)&quot;
        subend
end
</pre>
<p>All of the subsections are of type search, but as you can see they have
different searchpatterns, and the middle one doesn't have a baseurl. You can
place any of the other variables inside a sub-block (nested sub-blocks are
currently not supported). A sub-block will have all of the variables defined
outside of it's block (e.g &quot;type search&quot; in this example) plus the variables
defined inside its block. So effectively this one class defines 3 different
variants of the class, to allow to check for all 3.</p>
<p>You can now put little snippets of Perl code right into the definition. For
example, the definition for The Norm uses this to generate the day number for 14
days ago. The Norm website uses Javascript to generate the image URL, so it
couldn't be searched for and previously there was no way to work with dates
other than the current date. Here's how it works: just insert &lt;code:Perl code&gt;.
No need to quote the code, just put it where &quot;Perl code&quot; is. Just don't forget
to escape any &gt; that may happen to be in your code. Note that this is then
interpreted by a Python module (incomplete, YMMV with it) - Python doesn't have
a default method for putting code in regexps - the exact behaviour of this may
alter in future versions.</p>
<p>For your convenience, &quot;groups&quot; of strips may also be defined. These allow you to
use a single keyword on the command line to refer to a whole set of strips. The
construct is as follows:</p>
<pre class="literal-block">
group favorites
       desc My Favorite Comics
       include peanuts
       include foxtrot userfriendly
end
</pre>
<p>The group name must be unique among all groups, but will not conflict with
strips or classes. Everything after an &quot;include&quot; is added to the list of strips.
You may specify one or more strips per &quot;include&quot; line, whatever you prefer.</p>
<p>Notes:</p>
<ul class="simple">
<li>For classes, variables declared in the strip definition take precedence
over those specified in the class, if there is any conflict. Any variables
that you might use in a &quot;strip&quot; section can also be used in a &quot;class&quot;
section.</li>
<li>If no &quot;searchpage&quot; is specified for definitions of type &quot;search&quot;, the
value of &quot;homepage&quot; is used.</li>
<li>The default referer for HTTP is the value of &quot;searchpage&quot;. If this has not
been set (in the case of definitions that generate the URL or search
definitions that use the homepage as the searchpage), the value of
&quot;homepage&quot; is used.</li>
<li>Group, strip, and class names can contain pretty much any character.</li>
</ul>
<script language="php">include $TOPDIR."bottom.php3";</script>