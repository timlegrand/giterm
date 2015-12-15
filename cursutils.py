# -*- coding: utf-8 -*-
import curses
import pdb
import sys


screen = None
initialized = False


def init(stdscr):
    global screen
    screen = stdscr
    global initialized
    initialized = True


def debug(stdscr=screen):
    if not initialized:
        raise Exception('cursutils must be initialized first')
    if not stdscr:
        raise Exception('stdscr must be a valid window object')
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()
    debugger = pdb.Pdb()
    debugger.reset()
    debugger.do_where(None)
    users_frame = sys._getframe().f_back  # One frame up, not this function
    debugger.interaction(users_frame, None)


# Use with:
# import cursutils
# cursutils.init(stdscr)   # where stdscr is a curses window object
# cursutils.debug(cursutils.screen)
