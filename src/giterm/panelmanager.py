# coding: utf-8
from __future__ import absolute_import

import curses
import six

from itertools import cycle
from collections import OrderedDict
from giterm.panel import Panel, Popup

class PanelManager(OrderedDict):

    def __init__(self, stdscr):
        super(PanelManager, self).__init__()
        self.stdscr = stdscr
        self._active = None
        self.pop = None

        self.height, self.width = self.stdscr.getmaxyx()
        if self.height < 8 or self.width < 40:
            raise Exception("Height and width must be at least 8x40.\
                Currently: %sx%s" % (self.height, self.width))
        self.middle_point = self.height // 2, self.width // 2

    @property
    def active(self):
        if not (self._active or self.pop):
            raise Exception('Panel manager has no active panel')
        return self.pop or self._active

    @active.setter
    def active(self, _active):
        if self._active:
            self._active.deactivate()

        if isinstance(_active, str):
            _active = self[_active]
        
        self._active = _active.activate()

    def select(self):
        self.active.select()

    def add(self, name, panel):
        self[name] = panel

    def toggle(self, reverse=False):
        if reverse:
            items = self.items()
            reversed(items)
            reverse = OrderedDict(items)
            it = cycle(reversed(list(self.items())))
        else:
            it = cycle(self.items())
        for _, panel in it:
            if panel.active:
                panel.deactivate()
                self.active = next(it)[0]

    def on_display(self):
        if self.pop:
            self.pop.display()

    def display(self):
        curses.curs_set(0)
        active = None
        for _, panel in self.items():
            panel.display()
            if panel.active:
                active = panel
        if active:
            self.stdscr.move(*active.getcontentyx())

    def popup(self, title, msg):
        lines = msg.split('\n')
        t, l = self.middle_point
        h, w = len(lines), max([len(line) for line in lines])
        self.pop = Popup(
            self, self.stdscr,
            h, w, t - h // 2, l - w // 2,
            title=title
        )
        self.pop.content = lines
        self.pop.active = True
        self.pop.display()
        self._active.active = False

    def popup_close(self):
        del self.pop
        self.pop = None
        self._active.active = True
        self.display()
