#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (C) 2010 Vittorio Palmisano <vpalmisano at gmail dot com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
import os
import sys
import re
import cairo
import math

from realbook.score import MusicScore

SONG_RE = r"irealbook://(?P<title>[\w\s\-\ ',\(\)?]+)=(?P<author>[\w\s\-\ ',]+)=(?P<tempo>[\w\s\-\ ',]+)=(?P<key>[\w\s-]+)=(.)=(?P<song>.+Z)"
    
class IRealBookParser:
    def __init__(self, score, s):
        s = s.strip()
        if not s:
            return
        self.score = score
        song_re = re.compile(SONG_RE)
        m = re.search(song_re, s)
        print s
        d = m.groupdict()
        self.score.title = d['title']
        self.score.author = d['author']
        self.score.tempo = d['tempo']
        #
        chord_list = ('A', 'B', 'C', 'D', 'E', 'F', 'G')
        song = d['song']
        s = self.score.add_staff()
        measure, chord, chord_index = None, None, 0
        prev_measure = None
        next_chord_lower = False
        next_chord_fermata = False
        measure_count = 0
        i = 0
        while i < len(song):
            if song[i] in ('|', '{', '[', '}', ']'):
                if measure:
                    if measure_count == 4:
                        s = self.score.add_staff()
                        measure_count = 0  
                    if song[i] == '}':
                        measure.stop_barline = 'repeat'
                    elif song[i] == ']':
                        measure.stop_barline = 'double'
                if song[i-1] in ('|', '{', '[', '}', ']', 'Y'):
                    if song[i] == '{':
                        measure.start_barline = 'repeat'
                    elif song[i] == '[' and song[i-1] != ']':
                        measure.start_barline = 'double'
                        prev_measure.stop_barline = 'single'
                    i += 1
                    continue
                # new measure
                prev_measure = measure
                measure = s.add_measure(start_barline='single', empty=True)
                if measure_count == 0 and s.index == 0:
                    key, mode = d['key'][0], 'maj'
                    if len(d['key']) == 2:
                        if d['key'][1] in ('b', '#'):
                            key += d['key'][1]
                        elif d['key'][1] == 'm':
                            mode = 'min'
                    elif len(d['key']) == 3:
                        if d['key'][1] in ('b', '#'):
                            key += d['key'][1]
                        if d['key'][2] == 'm':
                            mode = 'min'
                    measure.key_signature = (key, mode)
                measure_count += 1
                chord = None
                chord_index = 0
                if song[i] == '{':
                    measure.start_barline='repeat'
                    measure.empty = False
                elif song[i] == '[' and song[i-1] != ']':
                    prev_measure.stop_barline = 'single'
                    measure.start_barline='double'
                    measure.empty = False
            elif song[i] == '*':
                if song[i+1] in ('A', 'B', 'C', 'D', 'i'):
                    if song[i+1] == 'i':
                        measure.section = 'intro'
                    else:
                        measure.section = song[i+1]
                    i += 1
                else:
                    j = song[i:].find('*')
                    chord.chord += song[i+1:j]
                    i += j
            elif song[i] == 'T':
                try:
                    measure.time = (int(song[i+1]), int(song[i+2]))
                except Exception, e:
                    print song[i:i+3]
                    raise Exception(e)
                i += 2
            elif song[i] in chord_list:
                if chord and song[i-1] == '/':
                    chord.chord += song[i]
                else:
                    chord = measure.add_chord(chord_index, song[i])
                    measure.empty = False
                    if next_chord_lower:
                        chord.small = True
                        next_chord_lower = False
                    if next_chord_fermata:
                        chord.fermata = True
                        next_chord_fermata = False
                    chord_index += 1
            elif song[i] == ' ':
                if chord_index == 4:
                    prev_measure = measure
                    measure = s.add_measure(empty=True)
                    measure_count += 1
                    chord_index = 0
                measure.add_chord(chord_index, '')
                chord_index += 1
            elif song[i] == ',':
                chord = None
            elif song[i] == 'N':
                measure.ending = song[i+1]
                i += 1
            elif song[i] == 's' and song[i:i+3] != 'sus' and song[i-2:i+1] != 'sus':
                next_chord_lower = True
            elif song[i] == 'l' and song[i+1] in chord_list:
                next_chord_lower = False
            elif song[i] in ('Z', '='):
                measure.stop_barline = 'final'
                break
            elif song[i] in ('Y', 'p'):
                #TODO
                pass
            elif song[i] in ('%', 'x', 'r', 'n'):
                if chord_index == 4:
                    prev_measure = measure
                    measure = s.add_measure(empty=True)
                    measure_count += 1
                    chord_index = 0
                measure.add_symbol(chord_index, '%') #TODO
                measure.empty = False
                chord_index += 1
                if song[i] == 'r':
                    prev_measure = measure
                    measure = s.add_measure(empty=False)
                    measure_count += 1
                    chord_index = 0
                    j = song[i+2:].find('|')
                    i += j
            elif song[i] == '(':
                chord = measure.add_chord(chord_index-1, song[i+1], alternate=True)
                measure.empty = False
                i += 1
            elif song[i] == ')':
                chord = None
            elif song[i] == '<':
                j = song[i:].find('>')
                text = song[i+1:i+j]
                i += j
                measure.add_symbol(chord_index, text)
            elif song[i] == 'S':
                measure.add_symbol(chord_index, 'segno')
            elif song[i] == 'Q':
                measure.add_symbol(chord_index, 'segno')
            elif song[i] == 'f':
                next_chord_fermata = True
            else:
                try:
                    chord.chord += song[i]
                except Exception, e:
                    print i, song, '\nError:', song[i:], '\n'
            i += 1
        
def test(i, s):
    score = MusicScore()
    IRealBookParser(score, s)
    #
    w, h = (8.27*100, 11.69*100)
    if not os.path.exists('pdf'):
        os.mkdir('pdf')
    surface = cairo.PDFSurface('pdf/%03d - %s.pdf' %(i, score.title), w, h)
    cr = cairo.Context(surface)
    score.draw(cr, w, h)
    cr.show_page()
   
def test1(s):
    score = MusicScore()
    IRealBookParser(score, s)
    # write to png
    w, h = (800, 1200)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    cr = cairo.Context(surface)
    score.draw(cr, w, h)
    cr.show_page()
    surface.write_to_png(open('%s.png' %score.title, 'w'))

import urllib

if __name__ == '__main__':
    s = 'irealbook://I%20Believe%20In%20You%3DLoesser%20Frank%3DMedium%20Up%20Swing%3DG%3Dn%3D%7B*AT44A-7%20%20%20%7CA-%5E7%20%20%20%7CA-7%20%20%20%7CA-6%20%20%20%7CB-7%20%20%20%7CC9%2311%20%20%20%7CB-7%20%20%20%7CE7%20%20%20%7C%7CA-7%20%20%20%7CA-%5E7%20%20%20%7CA-7%20%20%20%7CA-6%20%20%20%7CB%5E7%20%20%20%7CC%23-7%20F%237%20%7CB%5E7%20%20%20%7CA-7%20%20%20%7CD7%20%20%20%7CG%5E7%20%20%20%7CB-7%20E7%20%7CA-7%20%20%20%7CD7%20%20Q%20%7CN1G6%20%20%20%7CE7%20%20%20%7DN2G6%20%20%20%7CBb-7%20Eb7%20%5D*BAb%5E7%20%20%20%7CBb-7%20Eb7%20%7CAb%5E7%20%20%20%7CC-7%20F7%20%7CBb-7%20%20%20%7CEb7%20%20%20%7CAb%5E7%20%20%20%7CC-7%20F7%20%7CBb%5E7%20%20%20%7CC-7%20F7%20%7CBb%5E7%20%20%20%7C%20x%20%20%7CG-7%20%20%20%7CC7%20%20%20%7CA-7%20D7%20%7CB-7%20%3CD.C.%20al%20Coda%3EE7%20%5D%20%20%20%20%20%20%20%20%20%20%20%20%5BQG6%20%20%20%7CB-7%20E7%20Z%20%20%3CSolo%20on%20entire%20form%3E%20'

    s = urllib.unquote(s)
    test1(s)
    raise SystemExit

    songs = open('songs.txt').read().split('\n')
    start = int(sys.argv[1])
    for s in songs[start:]:
        test(songs.index(s), s)
