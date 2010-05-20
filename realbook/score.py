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
import cairo
import ctypes
import os
import sys
from staff import Staff

_initialized = False
def create_cairo_font_face_for_file(filename, faceindex=0, loadoptions=0):
    class PycairoContext(ctypes.Structure):
        _fields_ = [("PyObject_HEAD", ctypes.c_byte * object.__basicsize__),
                ("ctx", ctypes.c_void_p),
                ("base", ctypes.c_void_p)]
    global _freetype_so
    global _cairo_so
    global _ft_lib
    global _surface
    CAIRO_STATUS_SUCCESS = 0
    FT_Err_Ok = 0
    if not _initialized:
        # find shared objects
        _freetype_so = ctypes.CDLL ("libfreetype.so.6")
        _cairo_so = ctypes.CDLL ("libcairo.so.2")
        # initialize freetype
        _ft_lib = ctypes.c_void_p ()
        if FT_Err_Ok != _freetype_so.FT_Init_FreeType (ctypes.byref (_ft_lib)):
            raise "Error initialising FreeType library."
        _surface = cairo.ImageSurface (cairo.FORMAT_A8, 0, 0)
    # create freetype face
    ft_face = ctypes.c_void_p()
    cairo_ctx = cairo.Context (_surface)
    cairo_t = PycairoContext.from_address(id(cairo_ctx)).ctx
    _cairo_so.cairo_ft_font_face_create_for_ft_face.restype = ctypes.c_void_p
    if FT_Err_Ok != _freetype_so.FT_New_Face (_ft_lib, filename, faceindex, ctypes.byref(ft_face)):
        raise "Error creating FreeType font face for " + filename
    # create cairo font face for freetype face
    cr_face = _cairo_so.cairo_ft_font_face_create_for_ft_face (ft_face, loadoptions)
    if CAIRO_STATUS_SUCCESS != _cairo_so.cairo_font_face_status (cr_face):
        raise "Error creating cairo font face for " + filename
    _cairo_so.cairo_set_font_face (cairo_t, cr_face)
    if CAIRO_STATUS_SUCCESS != _cairo_so.cairo_status (cairo_t):
        raise "Error creating cairo font face for " + filename
    face = cairo_ctx.get_font_face()
    return face

class MusicScore:
    padding_left = 20
    padding_right = 20
    padding_top = 20
    padding_bottom = 20
    score_padding = 10

    def __init__(self):
        d = os.path.dirname(os.path.abspath(__file__))
        ttf_dir = os.path.join(d, '..', 'ttf')
        self.face_jazztext = create_cairo_font_face_for_file(
            os.path.join(ttf_dir, 'JazzText.ttf'), 0)
        self.face_jazz = create_cairo_font_face_for_file(
            os.path.join(ttf_dir, 'Jazz.ttf'), 0)
        self.face_jazzcord = create_cairo_font_face_for_file(
            os.path.join(ttf_dir, 'JazzCord.ttf'), 0)
        #
        self.title = ''
        self.author = ''
        self.tempo = ''
        self.key = ''
        self.staffs = []
        
    def add_staff(self, *args, **kw):
        if not kw.get('index'):
            kw['index'] = len(self.staffs)
        s = Staff(self, *args, **kw)
        self.staffs.append(s)
        return s

    def draw(self, cr, width, height, dpi=100):
        self.cr, self.width, self.height, self.dpi = cr, width, height, dpi
        # background
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.rectangle(0, 0, width, height)
        cr.fill()
        #
        top = self.draw_head()
        for staff in self.staffs:
            top = staff.draw(top + self.score_padding)

    def draw_head(self):
        cr = self.cr
        cr.set_font_face(self.face_jazztext)
        cr.set_source_rgb(0, 0, 0)
        # title
        text = self.title
        cr.set_font_size(40)
        xbear, ybear, fwidth, fheight, xadv, yadv = cr.text_extents(text)
        top = fheight + self.padding_top
        cr.move_to((self.width-fwidth)/2, top)
        cr.show_text(text)
        top += 10
        # author
        text = self.author
        cr.set_font_size(20)
        xbear, ybear, fwidth, fheight, xadv, yadv = cr.text_extents(text)
        top += fheight
        cr.move_to((self.width-self.padding_left-self.padding_right-fwidth), top)
        cr.show_text(text)
        # tempo
        text = self.tempo
        cr.set_font_size(20)
        xbear, ybear, fwidth, fheight, xadv, yadv = cr.text_extents(text)
        cr.move_to(self.padding_left, top)
        cr.show_text(text)
    

        return top

def test():
    self = MusicScore()
    #
    s = self.add_staff()
    m = s.add_measure(section='A')
    m.add_chord(0, 'C')
    m.add_chord(1, '')
    m.add_chord(2, 'A-7')
    m.add_chord(3, '')
    m.add_symbol(0, 'segno')
    m = s.add_measure()
    m.add_chord(0, 'C')
    m.add_chord(1, 'A-7')
    m = s.add_measure()
    m.add_chord(0, 'C')
    m.add_chord(1, 'A-7')
    m = s.add_measure()
    m.add_chord(0, 'C')
    m.add_chord(1, 'A-7')
    m.add_chord(2, '')
    m.add_chord(3, '')
    m.add_symbol(3, 'to coda')
    #
    s = self.add_staff()
    s.add_measure(section='intro',
        time=(12,8), key_signature=('C', 'maj')).add_chords(('C',))
    s.add_measure(start_barline='single', stop_barline='double',
        key_signature=('D', 'maj')).add_chords(('D',))
    s.add_measure(section='A', key_signature=('E', 'maj')).add_chords(('E',))
    s.add_measure(key_signature=('F', 'maj')).add_chords(('F',))
    s.add_measure(key_signature=('G', 'maj')).add_chords(('G',))
    s.add_measure(key_signature=('A', 'maj')).add_chords(('A',))
    s.add_measure(key_signature=('B', 'maj')).add_chords(('B',))
    s.add_measure(key_signature=('C#', 'maj')).add_chords(('C#',))
    #
    s = self.add_staff()
    s.add_measure(start_barline='repeat', stop_barline='repeat',
        key_signature=('Db', 'maj')).add_chords(('Db',))
    s.add_measure(ending='1', key_signature=('Eb', 'maj')).add_chords(('Eb',))
    s.add_measure(key_signature=('F#', 'maj')).add_chords(('F#',))
    s.add_measure(key_signature=('Gb', 'maj')).add_chords(('Gb',))
    s.add_measure(section='B', key_signature=('G#', 'maj')).add_chords(('G#',))
    s.add_measure(key_signature=('Ab', 'maj')).add_chords(('Ab',))
    s.add_measure(key_signature=('Bb', 'maj')).add_chords(('Bb',))
    s.add_measure(ending='2', key_signature=('C', 'min')).add_chords(('Cm',))
    s.add_measure(key_signature=('D', 'min')).add_chords(('Dm',))
    s.add_measure(key_signature=('E', 'min')).add_chords(('Em',))
    s.add_measure(stop_barline='final', key_signature=('F', 'min')).add_chords(('Fm',))
    #
    s = self.add_staff()
    s.add_measure(empty=True)
    s.add_measure(section='C', time=(3,4)).add_chords(('C^7', 'C-7', 'C7', 'C7sus'))
    s.add_measure(ending='1').add_chords(('Ch7', 'Co7', 'C5', 'C2'))
    s = self.add_staff()
    s.add_measure(time=(7,12)).add_chords(('Cadd9', 'C+', 'Co', 'Ch'))
    s.add_measure().add_chords(('Csus', 'C^', 'C-', 'C^9'))
    s = self.add_staff()
    s.add_measure().add_chords(('C^13', 'C6', 'C69', 'C^7#11'))
    m = s.add_measure()
    m.add_chords(('C^9#11/Bb', 'C^7#5/C#', 'C-6', 'C-69'))
    m.add_chord(0, 'C^9#11/Bb', alternate=True)
    s = self.add_staff()
    s.add_measure(section='B', ).add_chords(('C-b6', 'C-^7', 'C-^9', 'C-9'))
    s.add_measure().add_chords(('C-11', 'Ch9', 'C-7b5', 'C9'))
    s = self.add_staff()
    s.add_measure().add_chords(('C7b9', 'C7#9', 'C7#11', 'C9#11'))
    s.add_measure().add_chords(('C9#5', 'C9b5', 'C7b5', 'C7#5'))
    s = self.add_staff()
    s.add_measure().add_chords(('C7b13', 'C7#9#5', 'C7#9b5', 'C7#9#11'))
    s.add_measure().add_chords(('C7b9#11', 'C7b9b5', 'C7b9#5', 'C7b9#9'))
    s.add_measure().add_chords(('C7b9b13', 'C7alt', 'C13', 'C13#11'))
    s = self.add_staff()
    s.add_measure().add_chords(('C13#9', 'C13b9', 'C7b9sus', 'C7susadd3'))
    s.add_measure().add_chords(('C9sus', 'C13sus', 'C7b13sus', 'C11'))
    s = self.add_staff()
    m = s.add_measure(ending='1',)
    m.add_chord(0, 'Eb', fermata=True)
    m.add_chord(1, 'Eb7alt')
    m.add_chord(2, 'C#7alt', fermata=True)
    m.add_chord(1, 'C7b9b13', alternate=True, fermata=True)

    #
    w, h = (8.27*100, 11.69*100)
    surface = cairo.PDFSurface('score.pdf', w, h)
    cr = cairo.Context(surface)
    self.draw(cr, w, h)
    cr.show_page()

def test1():
    score = MusicScore()
    score.title = 'Title'
    score.author = 'Author'
    score.tempo = 'Swing'
    s = score.add_staff()
    m = s.add_measure(section='A')
    m.add_chord(0, 'C')
    # print to pdf
    w, h = (8.27*100, 11.69*100)
    surface = cairo.PDFSurface('score.pdf', w, h)
    cr = cairo.Context(surface)
    score.draw(cr, w, h)
    cr.show_page()

if __name__ == '__main__':
    test1()
