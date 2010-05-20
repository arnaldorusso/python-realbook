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
import math
from chord import Chord
from symbol import Symbol

def make_key_signatures():
    key_signatures = {}
    # maj
    key_signatures['C'] = {'maj': []}
    key_signatures['Cb'] = {'maj': ['B4b', 'E5b', 'A4b', 'D5b', 'G4b', 'C5b', 'F4b']}
    key_signatures['C#'] = {'maj': ['F5#', 'C5#', 'G5#', 'D5#', 'A4#', 'E5#', 'B4#']}
    key_signatures['D'] = {'maj': ['F5#', 'C5#']}
    key_signatures['Db'] = {'maj': ['B4b', 'E5b', 'A4b', 'D5b', 'G4b']}
    key_signatures['E'] = {'maj': ['F5#', 'C5#', 'G5#', 'D5#']}
    key_signatures['Eb'] = {'maj': ['B4b', 'E5b', 'A4b']}
    key_signatures['F'] = {'maj': ['B4b']}
    key_signatures['F#'] = {'maj': ['F5#', 'C5#', 'G5#', 'D5#', 'A4#', 'E5#']}
    key_signatures['G'] = {'maj': ['F5#']}
    key_signatures['Gb'] = {'maj': ['B4b', 'E5b', 'A4b', 'D5b', 'G4b', 'C5b']}
    key_signatures['G#'] = {'maj': ['F5#', 'C5#', 'G5#', 'D5#', 'A4#']}
    key_signatures['A'] = {'maj': ['F5#', 'C5#', 'G5#']}
    key_signatures['Ab'] = {'maj': ['B4b', 'E5b', 'A4b', 'D5b']}
    key_signatures['B'] = {'maj': ['F5#', 'C5#', 'G5#', 'D5#', 'A4#']}
    key_signatures['Bb'] = {'maj': ['B4b', 'E5b']}
    # min
    key_signatures['C']['min'] = key_signatures['Eb']['maj']
    key_signatures['Cb']['min'] = key_signatures['Bb']['maj']
    key_signatures['C#']['min'] = key_signatures['E']['maj']
    key_signatures['D']['min'] = key_signatures['F']['maj']
    key_signatures['Db']['min'] = key_signatures['E']['maj']
    key_signatures['E']['min'] = key_signatures['G']['maj']
    key_signatures['Eb']['min'] = key_signatures['Gb']['maj']
    key_signatures['F']['min'] = key_signatures['Ab']['maj']
    key_signatures['F#']['min'] = key_signatures['A']['maj']
    key_signatures['G']['min'] = key_signatures['Bb']['maj']
    key_signatures['Gb']['min'] = key_signatures['A']['maj']
    key_signatures['G#']['min'] = key_signatures['B']['maj']
    key_signatures['A']['min'] = key_signatures['C']['maj']
    key_signatures['Ab']['min'] = key_signatures['B']['maj']
    key_signatures['B']['min'] = key_signatures['D']['maj']
    key_signatures['Bb']['min'] = key_signatures['Db']['maj']
    return key_signatures

class Measure:
    def __init__(self, staff, index=0, time=(), key_signature=(), 
                 start_barline='single', stop_barline='single',
                 ending='', section='', empty=False):
        self.staff = staff
        self.index = index
        self.time = time
        self.start_barline = start_barline
        self.stop_barline = stop_barline
        self.ending = ending
        self.section = section
        self.empty = empty
        self.chords = []
        self.symbols = []
        self.key_signature = key_signature
        self.key_signatures = make_key_signatures()
        # drawing properties
        self.reset_drawing()

    def __repr__(self):
        return '<Measure %d>' %(self.index)

    def add_chord(self, index, chord='', **kw):
        c = Chord(self, index, chord, **kw)
        self.chords.append(c)
        return c

    def add_symbol(self, index, symbol='', **kw):
        s = Symbol(self, index, symbol, **kw)
        self.symbols.append(s)
        return s

    def add_chords(self, chords, **kw):
        added = []
        for i in xrange(len(chords)):
            c = Chord(self, i, chords[i], **kw)
            self.chords.append(c)
            added.append(c)
        return added

    def num_chords(self):
        n = 0
        for chord in self.chords:
            if not chord.alternate:
                n += 1
        return n

    def total_height(self):
        return self.height + self.top_height + self.bottom_height

    def reset_drawing(self):
        self.padding_left = 0
        self.width = 0
        self.height = 0
        self.top_height = 0
        self.bottom_height = 0
        self.chords_left = 0
        self.chords_padding_left = 0
        self.top_heights = []

    def draw(self, width, simulate=False):
        self.reset_drawing()
        self.width = width
        self.simulate = simulate
        self.height = self.staff.staff_lines_pos[-1]-self.staff.staff_lines_pos[0]
        cr = self.staff.score.cr
        self.padding_left = self.staff.score.padding_left+self.index*self.width
        #
        if self.empty:
            return
        self.draw_lines()
        # draw start measure
        if self.index == 0 and self.staff.index == 0:
            self.draw_clef()
        if self.start_barline:
            self.draw_start_barline()
        if self.stop_barline:
            self.draw_stop_barline()
        if self.time:
            self.draw_time_signature()
        if self.key_signature:
            self.draw_key_signature()
        if self.section:
            self.draw_section()
        # draw chords
        for chord in self.chords:
            chord.draw(simulate=self.simulate)
            self.top_height = max(self.top_height, chord.height)
            self.top_heights.append((chord.left, chord.width, chord.height))
        # draw symbols
        for symbol in self.symbols:
            symbol.draw(simulate=self.simulate)
            self.top_height = max(self.top_height, symbol.height)
            self.top_heights.append((symbol.left, symbol.width, symbol.height))
        if self.ending:
            self.draw_ending()

    def get_measure_height(self, position):
        for left, width, height in self.top_heights:
            if left <= position and (left+width) >= position:
                return height
        return 0

    def draw_lines(self):
        if self.simulate:
            return
        cr = self.staff.score.cr
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(0.5)
        for i in xrange(5):
            left = self.staff.score.padding_left + self.index*self.width
            right = self.staff.score.padding_left + (self.index+1)*self.width
            cr.move_to(left, self.staff.top+i*self.staff.lines_distance)
            cr.line_to(right, self.staff.top+i*self.staff.lines_distance)
        cr.stroke()

    def draw_clef(self):
        cr = self.staff.score.cr
        cr.set_font_face(self.staff.score.face_jazz)
        cr.set_font_size(30)
        xbear, ybear, fwidth, fheight, xadv, yadv = cr.text_extents('V')
        self.padding_left += 2
        cr.move_to(self.padding_left, self.staff.staff_lines_pos[3])
        if not self.simulate:
            cr.show_text('V')
        # update dist
        top_dist = self.staff.staff_lines_pos[3]-self.staff.staff_lines_pos[0]
        height = -ybear - top_dist
        self.top_height =  max(self.top_height, height)
        self.top_heights.append((self.padding_left, fwidth+2, height))
        self.padding_left += fwidth + 2
        bottom_dist = self.staff.staff_lines_pos[-1]-self.staff.staff_lines_pos[3]
        self.bottom_height = max(self.bottom_height, fheight + ybear - bottom_dist)

    def draw_start_barline(self):
        if self.start_barline == 'single':
            if self.staff.index == 0 and self.index == 0:
                return
            self.draw_measure_start()
        elif self.start_barline == 'double':
            self.draw_measure_start_double()
        elif self.start_barline == 'repeat':
            self.draw_start_repeat()

    def draw_stop_barline(self):
        if self.stop_barline == 'single':
            self.draw_measure_stop()
        elif self.stop_barline == 'double':
            self.draw_measure_stop_double()
        elif self.stop_barline == 'repeat':
            self.draw_stop_repeat()
        elif self.stop_barline == 'final':
            self.draw_measure_stop_final()

    def draw_measure_start(self):
        if not self.simulate:
            cr = self.staff.score.cr
            cr.set_source_rgb(0, 0, 0)
            cr.set_line_width(1.0)
            cr.move_to(self.padding_left, self.staff.staff_lines_pos[0])
            cr.line_to(self.padding_left, self.staff.staff_lines_pos[-1])
            cr.stroke()
        self.padding_left += 2
    
    def draw_measure_start_double(self):
        cr = self.staff.score.cr
        if not self.simulate:
            cr.set_source_rgb(0, 0, 0)
            cr.set_line_width(1.0)
            cr.move_to(self.padding_left, self.staff.staff_lines_pos[0])    
            cr.line_to(self.padding_left, self.staff.staff_lines_pos[-1])
            cr.move_to(self.padding_left+3, self.staff.staff_lines_pos[0])
            cr.line_to(self.padding_left+3, self.staff.staff_lines_pos[-1])
            cr.stroke()
        self.padding_left += 5

    def draw_measure_stop(self):
        if not self.simulate:
            cr = self.staff.score.cr
            cr.set_source_rgb(0, 0, 0)
            cr.set_line_width(1.0)
            left = self.staff.score.padding_left+(self.index+1)*self.width
            cr.move_to(left, self.staff.staff_lines_pos[0])
            cr.line_to(left, self.staff.staff_lines_pos[-1]) 
            cr.stroke()
        
    def draw_measure_stop_double(self):
        if not self.simulate:
            cr = self.staff.score.cr
            cr.set_source_rgb(0, 0, 0)
            cr.set_line_width(1.0)
            left = self.staff.score.padding_left+(self.index+1)*self.width
            cr.move_to(left-3, self.staff.staff_lines_pos[0])
            cr.line_to(left-3, self.staff.staff_lines_pos[-1])
            cr.move_to(left, self.staff.staff_lines_pos[0])
            cr.line_to(left, self.staff.staff_lines_pos[-1])
            cr.stroke()
        
    def draw_measure_stop_final(self):
        if not self.simulate:
            cr = self.staff.score.cr
            cr.set_source_rgb(0, 0, 0)
            cr.set_line_width(1.0)
            left = self.staff.score.padding_left+(self.index+1)*self.width
            cr.move_to(left-4, self.staff.staff_lines_pos[0])
            cr.line_to(left-4, self.staff.staff_lines_pos[-1])
            cr.stroke()
            cr.set_line_width(3.0)
            cr.move_to(left, self.staff.staff_lines_pos[0])
            cr.line_to(left, self.staff.staff_lines_pos[-1])
            cr.stroke()

    def draw_start_repeat(self):
        cr = self.staff.score.cr
        cr.set_font_face(self.staff.score.face_jazz)
        cr.set_source_rgb(0, 0, 0)
        cr.set_font_size(32)
        cr.move_to(self.padding_left-2, self.staff.staff_lines_pos[2])
        text = u'Ú'
        if not self.simulate:
            cr.show_text(text)
        xbear, ybear, fwidth, fheight, xadv, yadv = cr.text_extents(text)
        self.padding_left += fwidth + 2

    def draw_stop_repeat(self):
        cr = self.staff.score.cr
        cr.set_font_face(self.staff.score.face_jazz)
        cr.set_source_rgb(0, 0, 0)
        cr.set_font_size(32)
        left = self.staff.score.padding_left+(self.index+1)*self.width
        cr.move_to(left+2, self.staff.staff_lines_pos[2])
        text = u'Ú'
        cr.rotate(math.pi)
        if not self.simulate:
            cr.show_text(text)
        cr.rotate(-math.pi)

    ending_padding_bottom = 10
    ending_padding_top = 0
    def draw_ending(self):
        cr = self.staff.score.cr
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1.0)
        left = self.staff.score.padding_left+self.index*self.width
        if self.ending:
            cr.set_font_face(self.staff.score.face_jazz)
            cr.set_font_size(22)
            xbear, ybear, fwidth, fheight, xadv, yadv = cr.text_extents(self.ending)
        else:
            fheight = 0
        top = self.staff.staff_lines_pos[0] - self.top_height - \
                self.ending_padding_top - fheight - 10
        cr.move_to(left, self.staff.staff_lines_pos[0]-self.ending_padding_bottom)
        if not self.simulate:
            cr.line_to(left, top)
            cr.line_to(left+self.width*0.9, top)
            cr.stroke()
        if self.ending != 'empty':
            cr.move_to(left+2, top+fheight-4)
            if not self.simulate:
                cr.show_text(self.ending)
        self.top_height += self.ending_padding_top + fheight + 10

    section_table = {
            'A': u'Ø', 'B': u'Ù', 'C': u'Ú', 'D': u'Û', 'E': u'Ü', 'F': u'Ý', 
            'G': u'Þ', 'H': u'ß', 'I': u'à', 'J': u'á', 'K': u'â', 'L': u'ã', 
            'M': u'ä', 'N': u'å', 'O': u'æ', 'P': u'ç', 'Q': u'è', 'R': u'é', 
            'S': u'ê', 'T': u'ë', 'U': u'ì', 'V': u'í', 'W': u'î', 'X': u'ï', 
            'Y': u'ð', 'Z': u'ñ', ' ': u'ò', 
            'intro': u'Intro', 'verse': u'Verse',
        }
    section_padding_bottom = 4
    def draw_section(self):
        cr = self.staff.score.cr
        cr.set_font_face(self.staff.score.face_jazztext)
        cr.set_source_rgb(0, 0, 0)
        cr.set_font_size(25)
        text = self.section_table.get(self.section)
        xbear, ybear, fwidth, fheight, xadv, yadv = cr.text_extents(text)
        left = self.staff.score.padding_left+self.index*self.width
        top = self.staff.staff_lines_pos[0] - self.top_height - (fheight+ybear) - \
            self.section_padding_bottom
        cr.move_to(left, top)
        if not self.simulate:
            cr.show_text(text)
        self.top_height += fheight + self.section_padding_bottom
        self.chords_left = left + fwidth + 8
        self.chords_padding_left = fwidth + 8
        self.top_heights.append((left, fwidth, fheight + self.section_padding_bottom))

    def draw_time_signature(self):
        cr = self.staff.score.cr
        cr.set_font_face(self.staff.score.face_jazztext)
        cr.set_source_rgb(0, 0, 0)
        cr.set_font_size(22)
        self.padding_left += 2
        #
        num = str(self.time[0])
        den = str(self.time[1])
        xbear, ybear, num_width, fheight, xadv, yadv = cr.text_extents(num)
        xbear, ybear, den_width, fheight, xadv, yadv = cr.text_extents(den)
        if num_width > den_width:
            num_padding = 0
            den_padding = (num_width-den_width)*0.5
        else:
            den_padding = 0
            num_padding = (den_width-num_width)*0.5 
        # draw num
        cr.move_to(self.padding_left+num_padding, self.staff.staff_lines_pos[2])
        if not self.simulate:
            cr.show_text(num)
        # draw den
        cr.move_to(self.padding_left+den_padding, self.staff.staff_lines_pos[-1])
        if not self.simulate:
            cr.show_text(den)
        # update padding left
        self.padding_left += max(num_width, den_width) + 2
    
    def get_note_y(self, note):
        d = self.staff.lines_distance
        return {
            'G5': self.staff.staff_lines_pos[0]-d/2,
            'F5': self.staff.staff_lines_pos[0],
            'E5': self.staff.staff_lines_pos[0]+d/2.,
            'D5': self.staff.staff_lines_pos[1],
            'C5': self.staff.staff_lines_pos[1]+d/2.,
            'B4': self.staff.staff_lines_pos[2],
            'A4': self.staff.staff_lines_pos[2]+d/2.,
            'G4': self.staff.staff_lines_pos[3],
            'F4': self.staff.staff_lines_pos[3]+d/2,
        }[note]

    def draw_key_signature(self):
        cr = self.staff.score.cr
        cr.set_font_face(self.staff.score.face_jazz)
        cr.set_source_rgb(0, 0, 0)
        cr.set_font_size(25)
        key, mode = self.key_signature
        top_height = 0
        left = self.padding_left
        for note in self.key_signatures[key][mode]:
            top = self.get_note_y(note[:2])
            cr.move_to(self.padding_left, top)
            xbear, ybear, width, fheight, xadv, yadv = cr.text_extents(note[2])
            top_height = max(top_height, self.staff.staff_lines_pos[0] - top - ybear)
            if not self.simulate:
                cr.show_text(note[2])
            self.padding_left += 6
        self.padding_left += 6
        self.top_height = max(self.top_height, top_height)
        self.top_heights.append((left, self.padding_left, top_height))
