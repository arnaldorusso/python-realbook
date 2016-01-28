# python-realbook library #

python-realbook is an high quality music score drawing library for creating Real Book style sheet music. It uses Cairo as drawing backend.

## Features ##
  * High quality score drawing
  * Realbook-style chord writing
  * Support: node, chords, symbols
  * irealbook:// format parser (http://irealbook.net/)

**To do**:
  * Code cleanup
  * Add documentation and examples
  * irealbook parser debugging
  * Writing notes support

## Examples ##

# A simple score #
```
import cairo
from realbook import MusicScore

# Create a new MusicScore
score = MusicScore()
score.title = 'Title'
score.author = 'Author'
score.tempo = 'Swing'
s = score.add_staff()
m = s.add_measure(section='A', stop_barline='final')
m.add_chord(0, 'C')
# print to pdf
w, h = (8.27*100, 11.69*100)
surface = cairo.PDFSurface('score.pdf', w, h)
cr = cairo.Context(surface)
score.draw(cr, w, h)
cr.show_page()
```

![http://python-realbook.googlecode.com/svn/wiki/img/score.png](http://python-realbook.googlecode.com/svn/wiki/img/score.png)

# irealbook parser #
```
import cairo
from realbook import MusicScore
from parser import IRealBookParser
import urllib

s = 'irealbook://I%20Believe%20In%20You%3DLoesser%20Frank%3DMedium%20Up%20Swing%3DG%3Dn%3D%7B*AT44A-7%20%20%20%7CA-%5E7%20%20%20%7CA-7%20%20%20%7CA-6%20%20%20%7CB-7%20%20%20%7CC9%2311%20%20%20%7CB-7%20%20%20%7CE7%20%20%20%7C%7CA-7%20%20%20%7CA-%5E7%20%20%20%7CA-7%20%20%20%7CA-6%20%20%20%7CB%5E7%20%20%20%7CC%23-7%20F%237%20%7CB%5E7%20%20%20%7CA-7%20%20%20%7CD7%20%20%20%7CG%5E7%20%20%20%7CB-7%20E7%20%7CA-7%20%20%20%7CD7%20%20Q%20%7CN1G6%20%20%20%7CE7%20%20%20%7DN2G6%20%20%20%7CBb-7%20Eb7%20%5D*BAb%5E7%20%20%20%7CBb-7%20Eb7%20%7CAb%5E7%20%20%20%7CC-7%20F7%20%7CBb-7%20%20%20%7CEb7%20%20%20%7CAb%5E7%20%20%20%7CC-7%20F7%20%7CBb%5E7%20%20%20%7CC-7%20F7%20%7CBb%5E7%20%20%20%7C%20x%20%20%7CG-7%20%20%20%7CC7%20%20%20%7CA-7%20D7%20%7CB-7%20%3CD.C.%20al%20Coda%3EE7%20%5D%20%20%20%20%20%20%20%20%20%20%20%20%5BQG6%20%20%20%7CB-7%20E7%20Z%20%20%3CSolo%20on%20entire%20form%3E%20'
score = MusicScore()
IRealBookParser(score, urllib.unquote(s))
# write to png
w, h = (800, 1200)
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
cr = cairo.Context(surface)
score.draw(cr, w, h)
cr.show_page()
surface.write_to_png(open('%s.png' %score.title, 'w'))
```

![http://python-realbook.googlecode.com/svn/wiki/img/I%20Believe%20In%20You.png](http://python-realbook.googlecode.com/svn/wiki/img/I%20Believe%20In%20You.png)

## Dependencies ##
  * [Python](http://pythohn.org/)
  * [Cairo](http://cairographics.org/)

## Support the project ##
[![](https://www.paypal.com/en_GB/i/btn/btn_donate_SM.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=U2T8SJJGJTVUJ&lc=US&currency_code=EUR&bn=PP%2dDonationsBF%3abtn_donate_LG%2egif%3aNonHosted)