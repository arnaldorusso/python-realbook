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

chord_table = {
    'm':    u'-',
    '^7':   u'J', 'Maj7':   u'J', '7+':   u'J',
    '-7':   u'Ñ',
    '7':    u'7', 
    '7sus': u'Z',
    'h7':   u'º', '07':   u'º',
    'o7':   u'o7', 
    '5':    u'5',
    '2':    u'2',   
    'add9': u'add9', 
    '+':    u'Ø', '+9':    u'Ø9',
    'o':    u'o', 
    'h':    u'ª',
    'sus':  u'W', 
    '^':    u'J', 
    '-':    u'-', 
    '^9':   u'K',
    '^13':  u'L', 
    '6':    u'6', 
    '69':   u'H', 
    '^7#11': u'N',
    '^9#11': u'O', 
    '^7#5': u'T', 
    '-6':   u'Ç', 
    '-69':  u'É',
    '-b6':  u'-b6', 
    '-^7':  u'é', 
    '-^9':  u'è', 
    '-9':   u'Ö',
    '-11':  u'Ü', 
    'h9':   u'ª9', 
    '-7b5': u'à', 
    '9':    u'9',
    '7b9':  u'ï', 
    '7#9':  u'ñ', 
    '7#11': u'ö', 
    '9#11': u'O',
    '9#5':  u'U', 
    '9b5':  u'V', 
    '7b5':  u'S', 
    '7#5':  u'T',
    '7b13': u'713-', 
    '7#9#5': u'ò', 
    '7#9b5': u'ù', 
    '7#9#11': u'ÀÃ',
    '7b9#11': u'ü', 
    '7b9b5': u'ú', 
    '7b9#5': u'ó', '7b9b13': u'ó',
    '7b9#9': u'û',
    '7b9b13': u'ó', 
    '7alt': u'7alt', 
    '13': u'13', 
    '13#11': u'13Ã',
    '13#9': u'13À', 
    '13b9': u'ß', '13b9b5': u'ß',
    '7b9sus': u'ïW', 
    '7susadd3': u'Zadd3',
    '9sus': u'9W', 
    '13sus': u'13W', 
    '7b13sus': u'7b13W', 
    '11': u'11',
}

class Chord:
    padding_bottom = 4

    def __init__(self, measure, index, chord='', small=False, alternate=False, 
                 fermata=False):
        self.measure = measure
        self.index = index
        self.chord = chord
        self.alternate = alternate
        self.small = small
        self.fermata = fermata

    def __repr__(self):
        return '<Chord: %s index: %d>' %(self.chord, self.index)

    def reset_drawing(self):
        self.height = 0
        self.width = 0
        self.top = 0
        self.left = 0
        self.height = 0

    def draw(self, simulate=False):
        self.reset_drawing()
        if not self.chord:
            return
        cr = self.measure.staff.score.cr
        left = max(self.measure.padding_left, self.measure.chords_left)
        width = (self.measure.width - self.measure.chords_padding_left) \
            / float(self.measure.num_chords())
        self.left = chord_left = left + self.index*width
        self.top = self.measure.staff.staff_lines_pos[0] - self.padding_bottom
        if self.alternate:
            self.top -= 32
        # extract parts
        parts = self.chord.split('/', 1)
        if len(parts) == 2:
            chord, bass = parts
        else:
            chord, bass = self.chord, ''
        if len(chord) > 1 and chord[1] in ('#', 'b'):
            chord_name, qual = chord[0:2], chord[2:]
        else:
            chord_name, qual = chord[0], chord[1:]
        # draw chord
        self._draw_chord(chord_name, simulate)
        # draw qualities
        if qual:
            cr.set_font_face(self.measure.staff.score.face_jazzcord)
            if self.alternate or self.small:
                cr.set_font_size(20)
            else:
                cr.set_font_size(30)
            cr.move_to(self.left, self.top)
            text = unicode(chord_table[qual])
            xbear, ybear, fwidth, fheight, xadv, yadv = cr.text_extents(text)
            self.left += fwidth + 1
            self.width += fwidth + 1
            if not simulate:
                cr.show_text(text)
            self.height = max(self.height, fheight)
        # bass
        if bass:
            cr.set_font_face(self.measure.staff.score.face_jazz)
            if self.alternate or self.small:
                cr.set_font_size(10)
            else:
                cr.set_font_size(20)
            cr.move_to(self.left, self.top+5)
            cr.rotate(-math.pi*0.25)
            text = str(u'Y')
            xbear, ybear, fwidth, fheight, xadv, yadv = cr.text_extents(text)
            self.left += 7
            self.width += 7
            if not simulate:
                cr.show_text(text)
            cr.rotate(math.pi*0.25)
            self._draw_chord(bass, simulate)
        self.height += self.padding_bottom
        if self.alternate:
            self.height += 34
        if self.fermata:
            self._draw_fermata(simulate)
        self.left = chord_left

    def _draw_chord(self, chord_name, simulate=False):
        if len(chord_name) == 2:
            chord_name, alt = chord_name
        else:
            alt = ''
        cr = self.measure.staff.score.cr
        # draw chord
        cr.set_font_face(self.measure.staff.score.face_jazzcord)
        if self.alternate or self.small:
            cr.set_font_size(20)
        else:
            cr.set_font_size(30)
        cr.move_to(self.left, self.top)
        text = str(chord_name)
        xbear, ybear, fwidth, fheight, xadv, yadv = cr.text_extents(text)
        self.height = max(self.height, fheight)
        self.left += fwidth + 1
        self.width += fwidth + 1
        if not simulate:
            cr.show_text(text)
        # draw # or b
        if alt:
            cr.set_font_face(self.measure.staff.score.face_jazz)
            cr.move_to(self.left, self.top-fheight*.4)
            text = str(alt)
            xbear, ybear, fwidth, fheight, xadv, yadv = cr.text_extents(text)
            self.height = max(self.height, fheight)
            self.left += fwidth
            self.width += fwidth
            if not simulate:
                cr.show_text(text)

    def _draw_fermata(self, simulate):
        cr = self.measure.staff.score.cr
        cr.set_font_face(self.measure.staff.score.face_jazz)
        text = u'U'
        xbear, ybear, fwidth, fheight, xadv, yadv = cr.text_extents(text)
        left = max(self.measure.padding_left, self.measure.chords_left)
        width = (self.measure.width - self.measure.chords_padding_left) \
            / float(self.measure.num_chords())
        left = left + self.index*width
        top = self.measure.staff.staff_lines_pos[0] - self.height
        cr.move_to(left, top)
        if not simulate:
            cr.show_text(text)
        self.height += fheight

