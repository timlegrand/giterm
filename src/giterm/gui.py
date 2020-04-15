# coding: utf-8
from __future__ import absolute_import

import curses
import threading

from giterm.panels import *
from giterm.panelmanager import PanelManager
from giterm.postponer import Postponer

import giterm.rungit as rungit
import giterm.textutils as text

class GitermPanelManager(PanelManager):

    def __init__(self, stdscr):
        super(GitermPanelManager, self).__init__(stdscr)
        self.create_panels()

    def create_panels(self):
        """Creates a graphical-like UI:
    ┌────────┐┌────────────────────────────────┐
    │Branches││ Log history                    │
    │> master││                                │
    │> devel ││                                │
    └────────┘│                                │
    │Remotes ││                                │
    └────────┘└────────────────────────────────┘
    │Tags    │┌───────────────┐┌───────────────┐
    └────────┘│ Staged files  ││               │
    │Stashes │└───────────────┘│ Diff of       │
    └────────┘┌───────────────┐│ selected file │
    │Submod. ││ Changed files ││               │
    └────────┘└───────────────┘└───────────────┘
        """
        # Following sizes are percentages (e.g. w_30 is 30% of screen width)
        w_20 = min(max(self.width // 5, 20), 25)
        w_30 = self.width // 3
        w_50 = self.width - w_30 - w_20
        h_49 = self.height // 2
        h_51 = self.height - h_49
        h_25 = h_51 // 2
        h_26 = h_51 - h_25
        h_l = self.height // 5
        h_br = self.height - 4 * h_l
        self.add('branches', BranchesPanel(
            self, self.stdscr,
            h_br, w_20, 0, 0, title='Branches'
        ))
        self.add('remotes', Panel(
            self, self.stdscr,
            h_l, w_20, h_br, 0, title='Remotes'
        ))
        self.add('tags', StateLinePanel(
            self, self.stdscr,
            h_l, w_20, h_br + h_l, 0, title='Tags'
        ))
        self.add('stashes', Panel(
            self, self.stdscr,
            h_l, w_20, h_br + 2 * h_l, 0, title='Stashes'
        ))
        self.add('submodules', Panel(
            self, self.stdscr,
            h_l, w_20, h_br + 3 * h_l, 0, title='Submodules'
        ))
        self.add('history', HistoryPanel(
            self, self.stdscr,
            h_49, w_30 + w_50, 0, w_20, title='History'
        ))
        self.add('stage', StagerUnstagerPanel(
            self, self.stdscr,
            h_25, w_30, h_49, w_20, title='Staging Area'
        ))
        self.add('changes', StagerUnstagerPanel(
            self, self.stdscr,
            h_26, w_30, h_49 + h_25, w_20, title='Changes'
        ))
        self.add('diff', DiffPanel(
            self, self.stdscr,
            h_51, w_50, h_49, w_20 + w_30, title='Diff View'
        ))

        self['changes'].rungit = rungit.git_changed
        self['stage'].rungit = rungit.git_staged
        self['history'].rungit = rungit.git_history
        self['remotes'].rungit = rungit.git_remotes
        self['stashes'].rungit = rungit.git_stashes
        self['submodules'].rungit = rungit.git_submodules
        self['tags'].rungit = rungit.git_tags
        self['diff'].rungit = rungit.git_diff

        self['changes'].action = self.stage_file
        self['stage'].action = self.unstage_file

    def stage_file(self, path):
        rungit.git_stage_file(path)
        self['stage'].handle_event()
        self['changes'].handle_event()

    def unstage_file(self, path):
        if not path:
            raise Exception('path is mandatory')
        rungit.git_unstage_file(path)
        self['stage'].handle_event()
        self['changes'].handle_event()
