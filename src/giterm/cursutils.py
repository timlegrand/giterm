# -*- coding: utf-8 -*-
from __future__ import absolute_import

import curses
import pdb
import sys
import time


screen = None


def init(stdscr):
    global screen
    screen = stdscr


def finalize(stdscr=None):
    if not stdscr and not screen:
        raise Exception('either call init() first or provide a window object')
    stdscr = screen if screen and not stdscr else stdscr
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()


def debug(stdscr=None):
    if not stdscr and not screen:
        raise Exception('either call init() first or provide a window object')
    stdscr = screen if screen and not stdscr else stdscr
    finalize(stdscr)

    debugger = pdb.Pdb()
    debugger.reset()
    debugger.do_where(None)
    users_frame = sys._getframe().f_back  # One frame up, outside this function
    debugger.interaction(users_frame, None)


def log(msg):
    with open('../giterm.log', 'a') as f:
        full_msg = '{:<18}'.format(str(time.time())) + ': ' + str(msg)
        full_msg = full_msg + '\n' if full_msg[-1] != '\n' else full_msg
        f.write(full_msg)

# Use with:
# import cursutils
# cursutils.init(stdscr)   # where stdscr is a `curses` Window object
# cursutils.debug()
