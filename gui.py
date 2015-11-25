# -*- coding: utf-8 -*-

from panel import Panel, PanelManager
import rungit

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

class DiffViewPanel(Panel):

	def __init__(self, *args, **kwargs):
		super(DiffViewPanel, self).__init__(*args, **kwargs)
		self.selected_file = 'gui.py'

	def handle_event(self, event):
		self.content = self.rungit(self.selected_file)
		self.display()

class ChangesPanel(Panel):

	def __init__(self, *args, **kwargs):
		super(ChangesPanel, self).__init__(*args, **kwargs)
		self.selected_file = ''
		self.hovered_file = ''

	# def select(self):
	# 	self.selected = -1 if self.cursor_y == self.selected + self.CNT_T else self.cursor_y - self.CNT_T + self.topLineNum
	# 	if self.selected != -1:
	# 		self.selected_file = self.content[self.selected].split()[1]
	# 		#TODO: fire a rungit.git_diff(self.selected_file) event to DiffView
	# 		#TODO: next step, fire git_diff on hovering, and git_action_stage(file) on selection
	# 		#TODO: next step, fire git_diff only when hovering for a given delay (0.5 s)
	# 	self.display()

	# # For debug purposes only
	# def draw_content(self):
	# 	super(ChangesPanel, self).draw_content()
	# 	self.window.addnstr(self.T, self.L, self.selected_file, self.W-1)

	def _move_cursor(self):
		self.hovered_file = self.content[self.cursor_y-1+self.topLineNum].split()[1]
		self.window.move(self.cursor_y, self.cursor_x)
		self.window.refresh()
