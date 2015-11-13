#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
from itertools import cycle
from panel import Panel

def debug(stdscr):
	curses.nocbreak()
	stdscr.keypad(0)
	curses.echo()
	curses.endwin()
	import pdb; pdb.set_trace()

panels = []

def register(stdscr, height, width, y, x, border=True):
	panel = Panel(stdscr, height, width, y, x, border)
	panels.append(panel)
	return panel

def toggle():
	it = cycle(panels)
	for panel in it:
		if panel.active:
			panel.deactivate()
			return next(it).activate()

def keyloop(stdscr):
	stdscr.clear()
	stdscr_y, stdscr_x = stdscr.getmaxyx()
 	w_20_percent = stdscr_x * 2 // 10
 	w_80_percent = stdscr_x - w_20_percent
 	height_main = stdscr_y-1
	hier = register(stdscr, stdscr_y-4, w_20_percent, 0, 0)
	hier.display()
	hist = register(stdscr, stdscr_y-4, w_80_percent, 0, w_20_percent)
	hist.display()
	state = register(stdscr, 4, stdscr_x, stdscr_y-4, 0, border=True)

	state.display()

	active = hier.activate()
	cursor_y, cursor_x = active.content_start
	left, right, top, bottom = active.limits
	import time

	#main loop:
	while (1):
		# active.debug()
		stdscr.move(cursor_y, cursor_x)

		c = stdscr.getch()
		if 0<c<256:
			c = chr(c)
			if c in ' \n': # 'space bar' hit
				break
			elif c in 'Qq':
				break
			elif c == '\t':
				active = toggle()
				cursor_y, cursor_x = active.content_start
				active.text(0, 0, str((cursor_y, cursor_x)))
		elif c == curses.KEY_UP    and cursor_y > active.ABS_T: cursor_y -= 1
		elif c == curses.KEY_LEFT  and cursor_x > active.ABS_L: cursor_x -= 1
		elif c == curses.KEY_DOWN  and cursor_y < active.ABS_B: cursor_y += 1
		elif c == curses.KEY_RIGHT and cursor_x < active.ABS_R: cursor_x += 1
		elif c == curses.KEY_RESIZE:
			stdscr.clear()
			pass
			#TODO: handle terminal resize properly (downsize and upsize)
		else:
			pass

def main(stdscr):
	keyloop(stdscr)

if __name__ == '__main__':
	curses.wrapper(main)
