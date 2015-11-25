# -*- coding: utf-8 -*-

from panel import Panel, PanelManager
import rungit
import curses

class GitermPanelManager(PanelManager):
	def __init__(self, stdscr):
		super(GitermPanelManager, self).__init__(stdscr)
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
		w_20_pct = min(max(width // 5, 20), 25)
		w_30_pct = width // 3
		w_50_pct = width - w_30_pct - w_20_pct
		h_49_pct = height // 2
		h_51_pct = height - h_49_pct
		h_25_pct = h_51_pct // 2
		h_26_pct = h_51_pct - h_25_pct
		self['hier']    = HierarchiesPanel(self.stdscr, height, w_20_pct, 0, 0, title='')
		self['loghist'] = Panel(self.stdscr, h_49_pct, w_30_pct+w_50_pct, 0, w_20_pct, title='History')
		self['stage']   = Panel(self.stdscr, h_25_pct, w_30_pct, h_49_pct, w_20_pct, title='Staging Area')
		self['changes'] = ChangesPanel(self, self.stdscr, h_26_pct, w_30_pct, h_49_pct+h_25_pct, w_20_pct, title='Local Changes')
		self['diff']    = DiffViewPanel(self.stdscr, h_51_pct, w_50_pct, h_49_pct, w_20_pct+w_30_pct, title='Diff View')

		self['changes'].rungit = rungit.git_changed
		self['stage'].rungit   = rungit.git_staged
		self['loghist'].rungit = rungit.git_history
		self['hier'].rungit    = rungit.git_hierarchies
		self['diff'].rungit    = rungit.git_diff

class DiffViewPanel(Panel):

	def __init__(self, *args, **kwargs):
		super(DiffViewPanel, self).__init__(*args, **kwargs)
		self.default_title = self.title

	def handle_event(self, filepath):
		self.content = self.rungit(filepath)
		self.title = ": " + filepath if type(filepath) == str else ''
		self.title = self.default_title + self.title
		self.display()

class ChangesPanel(Panel):

	def __init__(self, parent, *args, **kwargs):
		super(ChangesPanel, self).__init__(*args, **kwargs)
		self.parent = parent
		self.default_title = self.title

	def select(self):
		hovered = self.topLineNum + self.cursor_y - self.CNT_T
		self.selected = -1 if self.selected == hovered else hovered
		if self.selected != -1:
			selected_file = self.content[self.selected].split()[1]
			self.parent['diff'].handle_event(selected_file)
			#TODO: next step, fire git_diff on hovering, and git_action_stage(file) on selection
			#TODO: next step, fire git_diff only when hovering for a given delay (0.5 s)
		else:
			self.parent['diff'].handle_event(None) # Force refresh
		self.display()

class HierarchiesPanel(Panel):

	def draw_content(self):
		top = self.topLineNum
		bottom = self.topLineNum + self.CNT_H
		for i, line in enumerate(self.content[top:bottom]):
			y = i + self.CNT_T
			current = True if line[-1] == '*' else False
			line = line[:-1] if current else line
			self.add_content_line(y, line)
			if self.active and self.cursor_y == y or current:
				self.window.chgat(y, self.CNT_L, self.CNT_R, curses.A_BOLD)
			if self.selected != -1 and y == self.selected + self.CNT_T - self.topLineNum:
				self.window.chgat(y, self.CNT_L, self.CNT_R, curses.A_REVERSE)
			# TODO: need to handle case of last line fulfilled with scrolling disabled
