# coding: utf-8
from __future__ import absolute_import

import curses
import six

from itertools import cycle
from collections import OrderedDict


class PanelManager(OrderedDict):

    def __init__(self, stdscr):
        super(PanelManager, self).__init__()
        self.stdscr = stdscr

    def toggle(self, reverse=False):
        if reverse:
            items = self.items()
            reversed(items)
            reverse = OrderedDict(items)
            it = cycle(reversed(list(six.iteritems(self))))
        else:
            it = cycle(six.iteritems(self))
        for k, panel in it:
            if panel.active:
                panel.deactivate()
                return next(it)[1].activate()

    def display(self):
        curses.curs_set(0)
        active = None
        for k, panel in six.iteritems(self):
            panel.display()
            if panel.active:
                active = panel
        if active:
            self.stdscr.move(*active.getcontentyx())
