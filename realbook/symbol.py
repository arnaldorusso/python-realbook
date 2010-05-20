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

symbols_table = {
    'n': 'N.C.', 
    '/': '/',
    'coda': u'ó', 'segno': u'ô',
}

class Symbol:
    padding_bottom = 10

    def __init__(self, measure, index, symbol=''):
        self.measure = measure
        self.index = index
        self.symbol = symbol

    def __repr__(self):
        return '<Symbol: %s index: %d>' %(self.chord, self.index)

    def reset_drawing(self):
        self.height = 0
        self.width = 0
        self.top = 0
        self.left = 0
        self.height = 0

    def draw(self, simulate=False):
        self.reset_drawing()
        if not self.symbol:
            return
        self._draw_symbol(simulate)
        self.height += self.padding_bottom

    def _draw_symbol(self, simulate=False):
        cr = self.measure.staff.score.cr
        # draw symbol
        padding_left = max(self.measure.padding_left, self.measure.chords_left)
        self.left = left = padding_left + self.index*(
                self.measure.width/float(self.measure.num_chords()))
        self.top = top = self.measure.staff.staff_lines_pos[0] - self.padding_bottom
        top_height = 0
        if self.symbol in ('%', 'x'):
            right = padding_left + (self.index+1)*(
                self.measure.width/float(self.measure.num_chords()))
            center = left + (right - left)*0.5
            if not simulate:
                if self.symbol == '%':
                    self._draw_repeat(center, top)
                elif self.symbol in ('x', 'r'):
                    self._draw_repeat_double(center, top)
        else:
            text = symbols_table.get(self.symbol)
            if not text:
                text = self.symbol
            cr.set_font_face(self.measure.staff.score.face_jazztext)
            cr.set_font_size(25)
            xbear, ybear, fwidth, fheight, xadv, yadv = cr.text_extents(text)
            top_height = max(self.measure.get_measure_height(left),
                self.measure.get_measure_height(left+fwidth))
            self.top -= top_height
            cr.move_to(left, self.top)
            self.height = max(self.height, fheight)
            self.width += fwidth + 1
            if not simulate:
                cr.show_text(text) 
        self.height += self.padding_bottom + top_height

    def _draw_repeat(self, center, top):
        cr = self.measure.staff.score.cr
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1.0)
        cr.move_to(center+12, top-10)
        cr.line_to(center-7, top+10)
        cr.line_to(center-12, top+10)
        cr.line_to(center+7, top-10)
        cr.line_to(center+12, top-10)
        cr.fill()
        cr.arc(center-6, top-5, 2.5, 0, math.pi*2)
        cr.arc(center+6, top+5, 2.5, 0, math.pi*2)
        cr.fill()
    
    def _draw_repeat_double(self, center, top):
        cr = self.measure.staff.score.cr
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1.0)
        cr.move_to(center+12, top-10)
        cr.line_to(center-7, top+10)
        cr.line_to(center-12, top+10)
        cr.line_to(center+7, top-10)
        cr.line_to(center+12, top-10)
        cr.fill()
        center += 7
        cr.move_to(center+12, top-10)
        cr.line_to(center-7, top+10)
        cr.line_to(center-12, top+10)
        cr.line_to(center+7, top-10)
        cr.line_to(center+12, top-10)
        cr.fill()
        center -= 7
        cr.arc(center-6, top-5, 2.5, 0, math.pi*2)
        cr.arc(center+12, top+5, 2.5, 0, math.pi*2)
        cr.fill()

