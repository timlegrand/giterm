#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
from itertools import cycle

# def debug(stdscr):
# 	curses.nocbreak()
# 	stdscr.keypad(0)
# 	curses.echo()
# 	curses.endwin()
# 	import pdb; pdb.set_trace()

panels = []

class Panel:
	"""Encapsulates a window
	"""
	def __init__(self, stdscr, width, height, y, x, border=True):
		self.parent = stdscr.derwin(width, height, y, x)
		if border == True:
			self.parent.box()
		self.y, self.x = y, x
		self.H, self.W = self.parent.getmaxyx()
		self.middle = ((self.H//2)+self.y-1, (self.W//2)+self.x-1)
		self.start = self.y+1, self.x+1
		self.limits = (self.x, self.x+self.W, y, y+self.H)
		self.active = False
		panels.append(self)
		self.deactivate(force=True)

	def display(self):
		self.parent.refresh()

	def deactivate(self, force=False):
		if not self.active and not force:
			return
		self.parent.box()
		self.parent.addstr(*center(0, self.W//2, ' Inactive '))
		self.active = False
		self.parent.refresh()

	def activate(self):
		if self.active:
			return
		self.parent.box(curses.ACS_CKBOARD,curses.ACS_CKBOARD)
		self.parent.addstr(*center(0, self.W//2, '  Active  '))
		self.active = True
		self.parent.refresh()
		return self

def toggle():
	it = cycle(panels)
	for panel in it:
		if panel.active:
			panel.deactivate()
			return next(it).activate()

def center(row, col, string):
	return row, col-len(string)/2, string

def keyloop(stdscr):
	stdscr.clear()
	stdscr_y, stdscr_x = stdscr.getmaxyx()
 	width_twenty_percent = stdscr_x * 2 // 10
 	width_heighty_percent = stdscr_x - width_twenty_percent
 	height_main = stdscr_y-1
	hier = Panel(stdscr, stdscr_y-4, width_twenty_percent, 0, 0)
	hier.display()
	hist = Panel(stdscr, stdscr_y-4, width_heighty_percent, 0, width_twenty_percent)
	hist.display()
	state = Panel(stdscr, 4, stdscr_x, stdscr_y-4, 0, border=True)

	state.display()

	active = hier.activate()
	(cursor_y, cursor_x) = active.start
	(left, right, top, bottom) = active.limits
	stdscr.addstr(*center(active.middle[0], active.middle[1], str(active.middle)))

	#main loop:
	while (1):
		active.parent.addstr(1, 1, "C'est parti!")
		active.display()
		stdscr.move(cursor_y, cursor_x)     # Move the cursor
		c = stdscr.getch()                		# Get a keystroke
		if 0<c<256:
			c = chr(c)
			if c in ' \n': # 'space bar' hit
				break
			elif c in 'Qq':
				break
			elif c == '\t':
				active = toggle()
				(cursor_y, cursor_x) = active.start
				(left, right, top, bottom) = (active.x, active.x+active.W, active.y, active.y+active.H)
				stdscr.move(cursor_y, cursor_x)
				stdscr.addstr(*center(active.middle[0], active.middle[1], str(active.middle)))

			elif c == curses.KEY_UP    and cursor_y >= top:    cursor_y -= 1
			elif c == curses.KEY_DOWN  and cursor_y <  bottom: cursor_y += 1
			elif c == curses.KEY_LEFT  and cursor_x >= left:   cursor_x -= 1
			elif c == curses.KEY_RIGHT and cursor_x <  right:  cursor_x += 1
			elif c == curses.KEY_RESIZE:
				stdscr.clear()
				pass # TODO: handle resize properly (downsize and upsize)
			else:
				pass

def main(stdscr):
	keyloop(stdscr)                    # Enter the main loop


if __name__ == '__main__':
	curses.wrapper(main)
