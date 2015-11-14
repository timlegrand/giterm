# -*- coding: utf-8 -*-

import curses

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
		self.load_content()

	def move_left(self):
		y, x = self.window.getyx()
		if x > self.CNT_L: x -= 1
		self.window.move(y, x)
		self.window.refresh()

	def move_right(self):
		y, x = self.window.getyx()
		if x < self.CNT_R: x += 1
		self.window.move(y, x)
		self.window.refresh()

	def move_up(self):
		y, x = self.window.getyx()
		if y > self.CNT_T: y -= 1
		self.window.move(y, x)
		self.window.refresh()

	def move_down(self):
		y, x = self.window.getyx()
		if y < self.CNT_B: y += 1
		self.window.move(y, x)
		self.window.refresh()

	def display(self):
		if not self.active:
			if self.border == 'box':
				self.window.box()
			elif self.border == 'bounding':
				self.window.border( ' ', ' ', ' ', ' ',
					curses.ACS_BSSB, curses.ACS_BBSS, curses.ACS_SSBB, curses.ACS_SBBS)
		self.add_content()
		self.window.move(self.CNT_T, self.CNT_L)
		self.window.refresh()

	def add_content(self):
		for i in xrange(len(self.content)-1):
			self.window.addnstr(i+1, 1, self.content[i], self.W-2)

	def load_content(self):
		for i in range(self.H-2):
			self.content.append("Content starts here...")

	def activate(self):
		if self.active:
			return
		self.active = True
		self.window.box()
		self.window.move(self.CNT_T, self.CNT_L)
		self.window.refresh()
		return self

	def deactivate(self, force=False):
		if not self.active and not force:
			return
		self.window.border( ' ', ' ', ' ', ' ',
			curses.ACS_BSSB, curses.ACS_BBSS, curses.ACS_SSBB, curses.ACS_SBBS)
		self.active = False
		self.window.refresh()

	def text_center(self, row, col, string):
		self.window.addstr(row, col-len(string)/2, string)

	def text(self, y, x, string):
		self.window.addstr(y, x, string)

	def text_right_align(self, y, x, string):
		self.window.addstr(y, x-len(string), string)

	def text_force_right_align(self, y, x, string):
		'''Forces right-aligned text to be printed
		until the last char position of the panel
		even with scrolling disabled''' 
		try:
			self.window.addstr(y, x-len(string), string)
		except curses.error:
			pass
			#window.addstr(0, 0, 'CAUGHT')

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
		self.text_right_align(self.T, self.R+1, TR)
		BL = str((self.B, self.L))
		self.window.addstr(self.B, self.L, BL)
		BR = str((self.B, self.R))
		if refresh:
			self.window.refresh()
