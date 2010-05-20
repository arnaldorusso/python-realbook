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
from measure import Measure

class Staff:
    lines_distance = 8

    def __init__(self, score, index):
        self.score = score
        self.index = index
        self.measures = []

    def __repr__(self):
        return '<Staff %d (%d measures)>' %(self.index, len(self.measures))

    def add_measure(self, *args, **kw):
        if not kw.get('index'):
            kw['index'] = len(self.measures)
        m = Measure(self, *args, **kw)
        self.measures.append(m)
        return m
            
    def reset_drawing(self): 
        self.top = 0
        self.top_height = 0

    def draw(self, top):
        self.reset_drawing()
        cr = self.score.cr
        # draw lines
        cr.save()
        self.top = top
        self.staff_lines_pos = []
        for i in xrange(5):
            self.staff_lines_pos.append(top+i*self.lines_distance)
        # draw measures
        width = (self.score.width-self.score.padding_right-self.score.padding_left) \
                    / float(len(self.measures))
        self.top_height, max_height = 0, 0
        for measure in self.measures:
            measure.draw(width, simulate=True)
            self.top_height = max(self.top_height, measure.top_height)
            max_height = max(max_height, measure.total_height())
        #
        cr.restore()
        cr.translate(0, self.top_height)
        for measure in self.measures:
            measure.draw(width)
        cr.translate(0, -self.top_height)
        return self.top + max_height

