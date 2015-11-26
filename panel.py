# -*- coding: utf-8 -*-
import curses

from itertools import cycle
from collections import OrderedDict
import locale
locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()


class PanelManager(OrderedDict):
    def __init__(self, stdscr):
        super(PanelManager, self).__init__()
        self.stdscr = stdscr

    def toggle(self, reverse=False):
        it = cycle(sorted(self.iteritems(), reverse=reverse))
        for k, panel in it:
            if panel.active:
                panel.deactivate()
                return next(it)[1].activate()

    def display(self):
        curses.curs_set(0)
        active = None
        for k, panel in self.iteritems():
            panel.display()
            if panel.active:
                active = panel
        if active:
            self.stdscr.move(*active.getcontentyx())


class Panel(object):
    """Encapsulates a window
    """
    def __init__(self, stdscr, h, w, y, x, title=''):
        self.content = []
        self.window = stdscr.derwin(h, w, y, x)
        self.title = title
        self.H, self.W = self.window.getmaxyx()
        self.T, self.L, self.B, self.R = 0, 0, h-1, w-1  # Window-relative
        self.CT, self.CL, self.CB, self.CR, self.CH, self.CW\
            = self.T+1, self.L+1, self.B-1, self.R-1, h-2, w-2
        self.cursor_y, self.cursor_x = self.CT, self.CL  # Window-relative
        self.middle = (self.H//2, self.W//2)
        self.active = False
        self.topLineNum = 0
        self.selected = -1  # Content-relative cursor
        self.load_content()

    def display(self):
        self.window.clear()
        self.draw_borders()
        self.draw_content()
        self._move_cursor()
        self.window.refresh()

    def draw_content(self):
        top = self.topLineNum
        bottom = self.topLineNum + self.CH
        for i, line in enumerate(self.content[top:bottom]):
            y = i + self.CT
            self.add_content_line(y, line)
            if self.active and self.cursor_y == y:
                self.window.chgat(y, self.CL, self.CR, curses.A_BOLD)
            if (self.selected != -1 and
                    y == self.selected + self.CT - self.topLineNum):
                self.window.chgat(y, self.CL, self.CR, curses.A_REVERSE)
            # TODO: need to handle case of last line fulfilled when
            # scrolling disabled

    def add_content_line(self, line_num, content):
        short, num_raw_bytes = self.shorten(content, self.CW)
        # import cursutils ; cursutils.debug(self.window)
        self.window.addnstr(line_num, self.CL, short, num_raw_bytes)

    def draw_borders(self):
        self.window.box()
        top, left, title, n = self.T, self.L+2, self.title, self.W-4
        if title:
            self.window.addnstr(top, left, ' ' + title + ' ', n)
            if self.active:
                self.window.addnstr(top, left, '[' + title + ']', n+2)
                self.window.chgat(top, left, len(title)+2, curses.A_BOLD)
        sidebar_pos = int(self.topLineNum * self.CH /
                          (max(len(self.content) - self.CH, 1)))
        if len(self.content) > self.CH:
            if sidebar_pos < self.CT:
                sidebar_pos = sidebar_pos + self.CT
            if sidebar_pos > self.CB:
                sidebar_pos = self.CB
            self.window.addnstr(sidebar_pos, self.R, 'o', 1)

    def shorten(self, string, size):
        printable = string.decode(code)
        # Is that really efficient? Shouldn't we store the raw data
        # in self.content instead?
        if len(printable) > size:
            printable = printable[:size-3] + '...'
        return printable.encode(code), len(string)

    def load_content(self):
        for i in range(5):
            self.content.append("Line #%s starts here and ends here." % str(i))

    # Callback function for remote observers
    def handle_event(self, event):
        self.content = self.rungit()
        self.display()

    def select(self):
        hovered = self.topLineNum + self.cursor_y - self.CT
        self.selected = -1 if self.selected == hovered else hovered
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
        return y+self.CT, x+self.CL

    def text_center(self, row, col, string):
        self.window.addstr(row, col-len(string)/2, string)

    def text(self, y, x, string):
        self.window.addstr(y, x, string)

    def text_right_align(self, y, x, string):
        self.window.addstr(y, x-len(string)+1, string)

    def text_force_right_align(self, y, x, string):
        '''Forces right-aligned text to be printed
        until the last char position of the panel
        even with scrolling disabled'''
        try:
            self.window.addstr(y, x-len(string)+1, string)
        except curses.error:
            pass

    def move_left(self):
        if self.cursor_x > self.CL:
            self.cursor_x -= 1
            self._move_cursor()

    def move_right(self):
        if self.cursor_x < self.CR:
            self.cursor_x += 1
            self._move_cursor()

    def move_up(self):
        if self.cursor_y > self.CT:
            self.cursor_y -= 1
            self._move_cursor()
        elif self.topLineNum >= 1:
            self.topLineNum -= 1
        else:
            return
        self.display()

    def move_down(self):
        if self.cursor_y < self.CB and self.cursor_y < len(self.content):
            self.cursor_y += 1
            self._move_cursor()
        elif self.topLineNum + self.CH < len(self.content):
            self.topLineNum += 1
        else:
            return
        self.display()

    def _move_cursor(self):
        self.window.move(self.cursor_y, self.cursor_x)
        self.window.refresh()

    def debug(self, refresh=True):
        self.window.box(curses.ACS_CKBOARD, curses.ACS_CKBOARD)
        active = '  Active  ' if self.active else ' Inactive '
        self.text_center(0, self.W//2, active)
        self.text_center(self.middle[0], self.middle[1], str(self.middle))
        size = '[' + str(self.H) + ' x ' + str(self.W) + ']'
        self.text_center(self.middle[0]+1, self.middle[1], size)
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
