# -*- coding: utf-8 -*-
import curses
import pdb
import sys


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


# Use with:
# import cursutils
# cursutils.init(stdscr)   # where stdscr is a `curses` Window object
# cursutils.debug()
