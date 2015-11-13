#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses

class Panel(object):
	"""Encapsulates a window
	"""
	def __init__(self, stdscr, height, width, y, x, border=True):
		self.content = []
		self.window = stdscr.derwin(height, width, y, x)
		if border == True:
			self.window.box()
		self.y, self.x = y, x
		self.H, self.W = self.window.getmaxyx()
		self.T, self.L, self.B, self.R = 0, 0, height-1, width-1 # relative
		self.ABS_T, self.ABS_L, self.ABS_B, self.ABS_R = y, x, y+height-1, x+width-1 # absolute
		self.middle = (self.H//2, self.W//2)
		self.abs_middle = ((self.H//2)+self.y-1, (self.W//2)+self.x-1)
		self.content_start = self.y+1, self.x+1
		self.content_end = self.y+1, self.x+1
		self.limits = (self.x, self.x+self.W, y, y+self.H)
		self.active = False
		self.deactivate(force=True)
		self.load_content()
		self.add_content()

	def display(self):
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
		self.window.refresh()
		return self

	def deactivate(self, force=False):
		if not self.active and not force:
			return
		self.window.box()
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
