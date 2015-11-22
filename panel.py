# -*- coding: utf-8 -*-

import curses
from itertools import cycle
from collections import OrderedDict
import rungit

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
		w_15_pct = width // 7 if width // 7 > 15 else 15
		w_30_pct = width // 3
		w_55_pct = width - w_30_pct - w_15_pct
		h_49_pct = height // 2
		h_51_pct = height - h_49_pct
		h_25_pct = h_51_pct // 2
		h_26_pct = h_51_pct - h_25_pct
		self['hier']    = Panel(self.stdscr, height, w_15_pct, 0, 0, title='')
		self['loghist'] = Panel(self.stdscr, h_49_pct, w_30_pct+w_55_pct, 0, w_15_pct, title='History')
		self['stage']   = Panel(self.stdscr, h_25_pct, w_30_pct, h_49_pct, w_15_pct, title='Staging Area')
		self['changes'] = ChangesPanel(self.stdscr, h_26_pct, w_30_pct, h_49_pct+h_25_pct, w_15_pct, title='Local Changes')
		self['diff']    = DiffViewPanel(self.stdscr, h_51_pct, w_55_pct, h_49_pct, w_15_pct+w_30_pct, title='Diff View')

		self['changes'].rungit = rungit.git_changed
		self['stage'].rungit = rungit.git_staged
		self['loghist'].rungit = rungit.git_history
		self['hier'].rungit = rungit.git_branch
		self['diff'].rungit = rungit.git_diff

	def toggle(self, reverse=False):
		it = cycle(sorted(self.iteritems(), reverse=reverse))
		for k, panel in it:
			if panel.active:
				panel.deactivate()
				return next(it)[1].activate()

	def display(self):
		curses.curs_set(0)
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
	def __init__(self, stdscr, height, width, y, x, border='bounding', title=''):
		self.content = []
		self.window = stdscr.derwin(height, width, y, x)
		self.title = title
		self.H, self.W = self.window.getmaxyx()
		self.T, self.L, self.B, self.R = 0, 0, height-1, width-1 # relative
		self.CNT_T, self.CNT_L, self.CNT_B, self.CNT_R, self.CNT_H, self.CNT_W = self.T+1, self.L+1, self.B-1, self.R-1, height-2, width-2
		self.cursor_y, self.cursor_x = self.CNT_T, self.CNT_L # Window display-relative cursor,
		self.middle = (self.H//2, self.W//2)
		self.active = False
		self.topLineNum = 0
		self.selected = -1 # Content-relative cursor
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
			if self.active and self.cursor_y == y:
				self.window.chgat(y, self.CNT_L, self.CNT_R, curses.A_BOLD)
			if self.selected != -1 and y == self.selected + self.CNT_T - self.topLineNum:
				self.window.chgat(y, self.CNT_L, self.CNT_R, curses.A_REVERSE)
			# TODO: need to handle case of last line fulfilled with scrolling disabled

	def draw_borders(self):
		self.window.box()
		if self.title:
			self.window.addnstr(self.T, self.L+2, ' ' + self.title + ' ', self.W-4)
			if self.active:
				self.window.addnstr(self.T, self.L+2, '[' + self.title + ']', self.W-2)
				self.window.chgat(self.T, self.L+2, len(self.title)+2, curses.A_BOLD)
		sb = int(self.topLineNum * self.CNT_H / (max(len(self.content) - self.CNT_H, 1)))
		if len(self.content) > self.CNT_H:
			if sb < self.CNT_T: sb = sb + self.CNT_T
			if sb > self.CNT_B: sb = self.CNT_B
			self.window.addnstr(sb, self.R, 'o', 1)

	def shorten(self, string, size):
		if len(string) > size:
			return string[:size-3] + '...'
		return string

	def load_content(self):
		for i in range(5):
			self.content.append("Line #%s starts here and ends here." % str(i))

	# Callback function for remote observers
	def handle_event(self, event):
		self.content = self.rungit()
		self.display()

	def select(self):
		self.selected = -1 if self.cursor_y == self.selected + self.CNT_T else self.cursor_y - self.CNT_T + self.topLineNum
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
		else:
			return
		self.display()

	def move_down(self):
		if self.cursor_y < self.CNT_B and self.cursor_y < len(self.content):
			self.cursor_y += 1
			self._move_cursor()
		elif self.topLineNum + self.CNT_H < len(self.content):
			self.topLineNum += 1
		else:
			return
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

class DiffViewPanel(Panel):

	def __init__(self, *args, **kwargs):
		super(DiffViewPanel, self).__init__(*args, **kwargs)
		self.selected_file = 'panel.py'

	def handle_event(self, event):
		self.content = self.rungit(self.selected_file)
		self.display()

class ChangesPanel(Panel):

	def __init__(self, *args, **kwargs):
		super(ChangesPanel, self).__init__(*args, **kwargs)
		self.selected_file = ''
		self.hovered_file = ''

	# def select(self):
	# 	self.selected = -1 if self.cursor_y-self.CNT_T+self.topLineNum == self.selected else self.cursor_y-self.CNT_T+self.topLineNum
	# 	if self.selected != -1:
	# 		self.selected_file = self.content[self.selected].split()[1]
	# 		#TODO: fire a rungit.git_diff(self.selected_file) event to DiffView
	# 		#TODO: next step, fire git_diff on hovering, and git_action_stage(file) on selection
	# 		#TODO: next step, fire git_diff only when hovering for a given delay (0.5 s)
	# 	self.display()

	def _move_cursor(self):
		self.hovered_file = self.content[self.cursor_y-1+self.topLineNum].split()[1]
		self.window.move(self.cursor_y, self.cursor_x)
		self.window.refresh()
