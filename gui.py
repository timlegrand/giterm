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
		self['changes'] = ChangesPanel(self, self.stdscr, h_26_pct, w_30_pct, h_49_pct+h_25_pct, w_15_pct, title='Local Changes')
		self['diff']    = DiffViewPanel(self.stdscr, h_51_pct, w_55_pct, h_49_pct, w_15_pct+w_30_pct, title='Diff View')

		self['changes'].rungit = rungit.git_changed
		self['stage'].rungit   = rungit.git_staged
		self['loghist'].rungit = rungit.git_history
		self['hier'].rungit    = rungit.git_branch
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
			#TODO: fire a rungit.git_diff(self.selected_file) event to DiffView
			#TODO: next step, fire git_diff on hovering, and git_action_stage(file) on selection
			#TODO: next step, fire git_diff only when hovering for a given delay (0.5 s)
		else:
			self.parent['diff'].handle_event(None) # Force refresh
		self.display()
