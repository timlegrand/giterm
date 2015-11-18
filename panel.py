# -*- coding: utf-8 -*-

import curses
from itertools import cycle
from collections import OrderedDict

# Callback function for remote observers
def git_status():
	import subprocess
	cmd = 'git status -s'
	process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
	return process.communicate()[0] 

class PanelManager(OrderedDict):
	def __init__(self, stdscr):
		super(PanelManager, self).__init__()
		self.stdscr = stdscr
		self.create_panels()

	def create_panels(self):
		"""Creates a SourceTree-like interface:
	┌────────┐┌────────────────────────────────┐
	│Branches││Log history                     │
	│> master││                                │
	│> devel ││                                │
	│        ││                                │
	│Remotes ││                                │
	│> origin│└────────────────────────────────┘
	│        │┌───────────────┐┌───────────────┐
	│Tags    ││ Staged files  ││               │
	│        │└───────────────┘│ Diff of       │
	│Stashes │┌───────────────┐│ selected file │
	│        ││ Changed files ││               │
	└────────┘└───────────────┘└───────────────┘
		"""
		height, width = self.stdscr.getmaxyx()
		if height < 8 or width < 40:
			raise Exception("Height and width must be at least 8x80. Currently: %sx%s" % (height, width))
		#TODO: add minimum widths and heights as requirements
		w_15_pct = width // 7 if width // 7 > 15 else 15
		w_30_pct = width // 3
		w_55_pct = width - w_30_pct - w_15_pct
		h_49_pct = height // 2
		h_51_pct = height - h_49_pct
		h_25_pct = h_51_pct // 2
		h_26_pct = h_51_pct - h_25_pct
		self['hier']    = Panel(self.stdscr, height, w_15_pct, 0, 0)
		self['loghist'] = Panel(self.stdscr, h_49_pct, w_30_pct+w_55_pct, 0, w_15_pct)
		self['stage']   = Panel(self.stdscr, h_25_pct, w_30_pct, h_49_pct, w_15_pct)
		self['changes'] = Panel(self.stdscr, h_26_pct, w_30_pct, h_49_pct+h_25_pct, w_15_pct)
		self['diff']    = Panel(self.stdscr, h_51_pct, w_55_pct, h_49_pct, w_15_pct+w_30_pct)

		self['changes'].get_changes = git_status

	def toggle(self):
		# TODO: add a reverse cycling
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
		if active:
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
		self.CNT_T, self.CNT_L, self.CNT_B, self.CNT_R, self.CNT_H, self.CNT_W = self.T+1, self.L+1, self.B-1, self.R-1, height-2, width-2
		self.cursor_y, self.cursor_x = self.CNT_T, self.CNT_L
		self.middle = (self.H//2, self.W//2)
		self.active = False
		self.topLineNum = 0
		self.selected = -1
		self.processing_event = False
		self.load_content()

	def display(self):
		self.window.clear()
		self.draw_borders()
		self.draw_content()
		self._move_cursor()
		self.window.refresh()

	def draw_content(self):
		top = self.topLineNum
		bottom = self.topLineNum + self.CNT_H
		for i, line in enumerate(self.content[top:bottom]):
			y = i+self.CNT_T
			short = self.shorten(line, self.W-3)
			self.window.addnstr(y, self.CNT_L, short, self.W-3)
			if self.selected != -1 and y == self.selected - self.topLineNum:
				self.window.chgat(y, self.CNT_L, self.CNT_R, curses.A_REVERSE)
			# TODO: need to handle case of last line fulfilled with scrolling disabled

	def draw_borders(self):
		if self.active:
			self.window.box()
		else:
			self.window.border( ' ', ' ', ' ', ' ',
				curses.ACS_BSSB, curses.ACS_BBSS, curses.ACS_SSBB, curses.ACS_SBBS)
		sb = int(self.topLineNum * self.CNT_H / (max(len(self.content) - self.CNT_H, 1)))
		if sb < self.CNT_T: sb = sb + self.CNT_T
		if sb > self.CNT_B: sb = self.CNT_B
		self.window.addnstr(sb, self.R, '<', 1)

	def shorten(self, string, size):
		if len(string) > size:
			return string[:size-3] + '...'
		return string

	def load_content(self):
		for i in range(1):
			self.content.append("Line #%s starts here and ends here." % str(i))

	# Callback function for remote observers
	def handle_event(self, event):
		if self.processing_event:
			return
		self.processing_event = True
		output = self.get_changes()
		for l in output.splitlines():
			self.content.insert(0, l)
			if self.selected != -1: self.selected += 1
		self.display()
		self.processing_event = False 
		return

		self.content.insert(0, event.content)
		if self.selected != -1: self.selected += 1
		self.display()

	def select(self):
		# y, x = self.window.getyx()
		self.selected = -1 if self.cursor_y == self.selected else self.cursor_y
		self.display()

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
		if self.cursor_x > self.CNT_L:
			self.cursor_x -= 1
			self._move_cursor()

	def move_right(self):
		if self.cursor_x < self.CNT_R:
			self.cursor_x += 1
			self._move_cursor()

	def move_up(self):
		if self.cursor_y > self.CNT_T:
			self.cursor_y -= 1
			self._move_cursor()
		elif self.topLineNum >= 1:
			self.topLineNum -= 1
			self.display()
	def move_down(self):
		if self.cursor_y < self.CNT_B:
			self.cursor_y += 1
			self._move_cursor()
		elif self.topLineNum + self.CNT_H < len(self.content):
			self.topLineNum += 1
			self.display()

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
