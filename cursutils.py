# -*- coding: utf-8 -*-

import curses
import pdb
import sys

def debug(stdscr):
	curses.nocbreak()
	stdscr.keypad(0)
	curses.echo()
	curses.endwin()
	debugger = pdb.Pdb()
	debugger.reset()
	debugger.do_where(None)
	users_frame = sys._getframe().f_back # One frame up, not this function
	debugger.interaction(users_frame, None)

# Use with:
# import cursutils ; cursutils.debug(self.window)
