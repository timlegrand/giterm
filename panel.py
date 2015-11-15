# -*- coding: utf-8 -*-

import curses
from itertools import cycle
from collections import OrderedDict

class PanelManager(OrderedDict):
	def __init__(self, stdscr):
		super(PanelManager, self).__init__()
		self.stdscr = stdscr

	def toggle(self):
		it = cycle(self.iteritems())
		for k, panel in it:
			if panel.active:
				panel.deactivate()
				return next(it)[1].activate()

	def display(self):
		active = None
		for k, panel in self.iteritems():
			panel.display()
			if panel.active:
				active = panel
		self.stdscr.move(*active.getcontentyx())

class Panel(object):
	"""Encapsulates a window
	"""
	def __init__(self, stdscr, height, width, y, x, border='bounding'):
		self.content = []
		self.window = stdscr.derwin(height, width, y, x)
		self.border = border
		self.H, self.W = self.window.getmaxyx()
		self.T, self.L, self.B, self.R = 0, 0, height-1, width-1 # relative
		self.CNT_T, self.CNT_L, self.CNT_B, self.CNT_R = self.T+1, self.L+1, self.B-1, self.R-1
		self.middle = (self.H//2, self.W//2)
		self.abs_middle = ((self.H//2)+y-1, (self.W//2)+x-1)
		self.active = False
		self.changed = False
		self.load_content()

	def display(self):
		self.window.clear()
		if self.active:
			self.window.box()
		else:
			self.window.border( ' ', ' ', ' ', ' ',
				curses.ACS_BSSB, curses.ACS_BBSS, curses.ACS_SSBB, curses.ACS_SBBS)
		self.add_content()
		self.window.move(self.CNT_T, self.CNT_L)
		self.window.refresh()

	def add_content(self):
		for i in range(len(self.content)):
			self.window.addnstr(i+1, 1, str(self.content[i]), self.W-3)

	def load_content(self):
		for i in range(self.H-2):
			self.content.append("Content starts here...")
		self.changed = True

	# Callback function for remote observers
	def set_content(self, event):
		self.content[0] = event.content
		self.changed = True
		self.display()
		self.window.move(self.CNT_T, self.CNT_L)

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
		return y+self.CNT_T, x+self.CNT_L

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
		self.cursor_y, self.cursor_x = self.window.getyx()
		if self.cursor_x > self.CNT_L:
			self.cursor_x -= 1
			self._move_cursor()

	def move_right(self):
		self.cursor_y, self.cursor_x = self.window.getyx()
		if self.cursor_x < self.CNT_R:
			self.cursor_x += 1
			self._move_cursor()

	def move_up(self):
		self.cursor_y, self.cursor_x = self.window.getyx()
		if self.cursor_y > self.CNT_T:
			self.cursor_y -= 1
			self._move_cursor()

	def move_down(self):
		self.cursor_y, self.cursor_x = self.window.getyx()
		if self.cursor_y < self.CNT_B:
			self.cursor_y += 1
			self._move_cursor()

	def _move_cursor(self):
		self.window.move(self.cursor_y, self.cursor_x)
		self.window.refresh()

	def debug(self, refresh=True):
		self.window.box(curses.ACS_CKBOARD,curses.ACS_CKBOARD)
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
