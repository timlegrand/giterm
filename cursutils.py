# -*- coding: utf-8 -*-

import curses

def debug(stdscr):
	curses.nocbreak()
	stdscr.keypad(0)
	curses.echo()
	curses.endwin()
	import pdb; pdb.set_trace()
