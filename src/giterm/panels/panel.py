# coding: utf-8
from __future__ import absolute_import

import curses

import giterm.textutils as textutils
import giterm.cursutils as cursutils


class Panel(object):
    """Encapsulates a (sub-)window.
           < W >
    (0,0)▒▒▒ T ▒▒▒▒▒▒▒▒ <── border
    ▒       CT        ▒ ┐
    ▒                 o <── slider
  ^ ▒                 ▒ │
  H ▒CL             CR▒ │ content goes from
  v L                 R │ (CT,CL) to (CB,CR)
    ▒cursor(y,x)▒     ▒ │
    ▒       CB        ▒ ┘
    ▒▒▒▒▒▒▒▒ B ▒▒▒(H,W)
    """

    def __init__(self, parent, stdscr, h, w, y, x, title=''):
        self.parent = parent
        self.call_on_display = True
        self.content = []
        self.data = []
        self.decorations = {}
        self.window = stdscr.derwin(h, w, y, x)
        self.title = title
        self.H, self.W = self.window.getmaxyx()
        self.T, self.L, self.B, self.R = 0, 0, h - 1, w - 1  # Window-relative
        self.CT, self.CL, self.CB, self.CR, self.CH, self.CW\
            = self.T + 1, self.L + 1, self.B - 1, self.R - 1, h - 2, w - 2
        self.cursor_y, self.cursor_x = self.CT, self.CL  # Window-relative
        self.middle = (self.H // 2, self.W // 2)
        self.active = False
        self.topLineNum = 0
        self.selected_content_line = -1  # Content-relative line number [0..N-1]
        self.hovered_content_line = 0  # Content-relative line number [0..N-1]

    def display(self):
        self.window.erase()
        self.draw_borders()
        self.draw_content()
        self.check_cursor_position()
        self.draw_hover()
        self.draw_selected()
        self.window.refresh()
        self.parent.on_display()

    def draw_content(self):
        top = self.topLineNum
        bottom = self.topLineNum + self.CH
        for i, line in enumerate(self.content[top:bottom]):
            y = i + self.CT
            self.add_content_line(y, line)
            index = y + self.topLineNum - self.CT
            if index in self.decorations:
                self.window.chgat(y, self.CL, self.CR, self.decorations[index])
            # TODO: need to handle case of last line fulfilled when
            # scrolling disabled

    def check_cursor_position(self):
        self.allowed_cursor_range_start = min(self.CT, len(self.content))
        self.allowed_cursor_range_end = max(
            self.allowed_cursor_range_start,
            len(self.content) - 1 - self.topLineNum + self.CT)
        if self.cursor_y < self.allowed_cursor_range_start:
            self.cursor_y = self.allowed_cursor_range_start
        elif self.cursor_y > self.allowed_cursor_range_end:
            self.cursor_y = self.allowed_cursor_range_end

    def draw_hover(self):
        self.hovered_content_line = self.cursor_y + self.topLineNum - self.CT
        y = self.cursor_y
        if (self.active and y >= self.CT and y <= self.CB and self.content):
            index = y + self.topLineNum - self.CT
            mode = curses.A_NORMAL
            if index in self.decorations:
                mode = self.decorations[index]
            self.window.chgat(y, self.CL, self.CR, mode | curses.A_REVERSE)

    def draw_selected(self):
        if self.selected_content_line != -1:
            y = self.selected_content_line + self.CT - self.topLineNum
            if y < self.CT or y > self.CB:
                return
            char = self.window.inch(y, self.CL)
            attr = char & curses.A_ATTRIBUTES
            self.window.chgat(y, self.CL, self.CR, attr | curses.A_BOLD)

    def add_content_line(self, line_num, content):
        short, num_raw_bytes = textutils.shorten(content, self.CW)
        self.window.addnstr(line_num, self.CL, short, num_raw_bytes)

    def draw_borders(self):
        try:
            self.window.box()
            top, left, title, n = self.T, self.L + 2, self.title, self.W - 4
            if title:
                self.window.addnstr(top, left, ' ' + title + ' ', n)
                if self.active:
                    self.window.addnstr(top, left, '[' + title + ']', n + 2)
                    self.window.chgat(top, left, len(title) + 2, curses.A_BOLD)
            slider_pos = int(
                self.topLineNum * self.CH /
                (max(len(self.content) - self.CH, 1)))
            if len(self.content) > self.CH:
                if slider_pos < self.CT:
                    slider_pos = slider_pos + self.CT
                if slider_pos > self.CB:
                    slider_pos = self.CB
                self.window.addnstr(slider_pos, self.R, 'o', 1)
        except:
            # Window might just be downsided and is not large enough
            # to draw borders with old dimensions. Let's wait for the
            # second chance draw and skip this one.
            pass

    def setup_content(self):
        self.content = self.data

    # Callback function for remote observers
    def handle_event(self, event=None):
        self.data = self.rungit()
        self.setup_content()
        self.display()

    def update_selection(self):
        if self.hovered_content_line == self.selected_content_line:
            self.selected_content_line = -1
        else:
            self.selected_content_line = self.hovered_content_line

    def select(self):
        self.update_selection()
        self.display()

    def unselect(self):
        self.selected_content_line = -1
        self.display()

    def activate(self):
        if self.active:
            return
        self.active = True
        self.display()
        return self

    def deactivate(self, force=False):
        if not self.active and not force:
            return
        self.active = False
        self.display()

    def getcontentyx(self):
        y, x = self.window.getbegyx()
        return y + self.CT, x + self.CL

    def text_center(self, row, col, string):
        self.window.addstr(row, col - len(string) / 2, string)

    def text(self, y, x, string):
        self.window.addstr(y, x, string)

    def text_right_align(self, y, x, string):
        self.window.addstr(y, x - len(string) + 1, string)

    def text_force_right_align(self, y, x, string):
        '''Forces right-aligned text to be printed
        until the last char position of the panel
        even with scrolling disabled'''
        try:
            self.window.addstr(y, x - len(string) + 1, string)
        except curses.error:
            pass

    def move_left(self):
        if self.cursor_x > self.CL:
            self.cursor_x -= 1
            self.move_cursor()

    def move_right(self):
        if self.cursor_x < self.CR:
            self.cursor_x += 1
            self.move_cursor()

    def move_up(self):
        if self.cursor_y > self.CT:
            self.cursor_y -= 1
        elif self.topLineNum > 0:
            self.topLineNum -= 1
        else:
            return
        self.move_cursor()

    def move_down(self):
        if self.cursor_y < self.CB and self.cursor_y < len(self.content):
            self.cursor_y += 1
        elif self.topLineNum + self.CH < len(self.content):
            self.topLineNum += 1
        else:
            return
        self.move_cursor()

    def move_prev_page(self):
        if self.topLineNum < self.CH:
            self.topLineNum = 0
        else:
            self.topLineNum -= self.CH
        self.hovered_content_line = self.topLineNum
        self.move_cursor()

    def move_next_page(self):
        if self.topLineNum + self.CH < len(self.content):
            self.topLineNum += self.CH
        else:
            return
        self.hovered_content_line = self.topLineNum
        self.move_cursor()

    def move_cursor(self):
        self.hovered_content_line = self.topLineNum + self.cursor_y - self.CT
        self.window.move(self.cursor_y, self.cursor_x)
        self.display()

    def debug(self, refresh=True):
        self.window.box(curses.ACS_CKBOARD, curses.ACS_CKBOARD)
        active = '  Active  ' if self.active else ' Inactive '
        self.text_center(0, self.W // 2, active)
        self.text_center(self.middle[0], self.middle[1], str(self.middle))
        size = '[' + str(self.H) + ' x ' + str(self.W) + ']'
        self.text_center(self.middle[0] + 1, self.middle[1], size)
        TL = str((self.T, self.L))
        self.window.addstr(self.T, self.L, TL)
        TR = str((self.T, self.R))
        self.text_force_right_align(self.T, self.R, TR)
        BL = str((self.B, self.L))
        self.window.addstr(self.B, self.L, BL)
        BR = str((self.B, self.R))
        self.text_force_right_align(self.B, self.R, BR)
        if refresh:
            self.window.refresh()

    def log(self, msg):
        cursutils.log(f'{self.title}: {str(msg)}')

class Popup(Panel):
    def display(self):
        self.window.erase()
        self.draw_borders()
        self.draw_content()
        self.check_cursor_position()
        self.draw_hover()
        self.draw_selected()
        self.window.refresh()
    
    def select(self):
        pass

class StateLinePanel(Panel):
    def handle_event(self, event=None):
        self.content = self.rungit()
        for i, line in enumerate(self.content):
            if line.startswith('*'):
                self.decorations[i] = curses.A_BOLD
                self.content[i] = line[1:]
        self.display()
