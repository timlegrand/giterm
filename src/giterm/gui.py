# coding: utf-8
from __future__ import absolute_import

import curses
import threading

from giterm.panel import Panel
from giterm.panelmanager import PanelManager
from giterm.postponer import Postponer

import giterm.rungit as rungit
import giterm.textutils as text


class GitermPanelManager(PanelManager):

    def __init__(self, stdscr):
        super(GitermPanelManager, self).__init__(stdscr)
        self.create_panels()
        self.pops = 0

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
        height, width = self.stdscr.getmaxyx()
        if height < 8 or width < 40:
            raise Exception("Height and width must be at least 8x40.\
                Currently: %sx%s" % (height, width))
        self.middle_point = height // 2, width // 2
        # Following sizes are percentages (e.g. w_30 is 30% of screen width)
        w_20 = min(max(width // 5, 20), 25)
        w_30 = width // 3
        w_50 = width - w_30 - w_20
        h_49 = height // 2
        h_51 = height - h_49
        h_25 = h_51 // 2
        h_26 = h_51 - h_25
        h_l = height // 5
        h_br = height - 4 * h_l
        self['branches'] = BranchesPanel(
            self.stdscr,
            h_br, w_20, 0, 0, title='Branches')
        self['remotes'] = Panel(
            self.stdscr,
            h_l, w_20, h_br, 0, title='Remotes')
        self['tags'] = StateLinePanel(
            self.stdscr,
            h_l, w_20, h_br + h_l, 0, title='Tags')
        self['stashes'] = Panel(
            self.stdscr,
            h_l, w_20, h_br + 2 * h_l, 0, title='Stashes')
        self['submodules'] = Panel(
            self.stdscr,
            h_l, w_20, h_br + 3 * h_l, 0, title='Submodules')
        self['history'] = HistoryPanel(
            self.stdscr,
            h_49, w_30 + w_50, 0, w_20, title='History')
        self['stage'] = StagerUnstager(
            self, self.stdscr,
            h_25, w_30, h_49, w_20, title='Staging Area')
        self['changes'] = StagerUnstager(
            self, self.stdscr,
            h_26, w_30, h_49 + h_25, w_20, title='Changes')
        self['diff'] = Diff(
            self.stdscr,
            h_51, w_50, h_49, w_20 + w_30, title='Diff View')

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

    def popup(self, title, msg):
        self.pops += 1
        t, l = self.middle_point
        h, w = 12, 50
        self.message_box = Panel(
            self.stdscr,
            h, w, t - h // 2, l - w // 2,
            title=title + str(self.pops))
        self.message_box.content = [
            '''I'm a cute popup message box''',
            '''Close me if you dare!''']
        self.message_box.display()
        return self.message_box.activate()

    def popup_close(self):
        del self.message_box
        self.pops = 0
        self.display()

class Diff(Panel):

    def __init__(self, *args, **kwargs):
        super(Diff, self).__init__(*args, **kwargs)
        self.default_title = self.title
        self.running = threading.Lock()

    def setup_content(self):
        if not self.data:
            return
        self.content = []
        cut_line = '-' * (self.CW // 2 - 1) + '8<' + '-' * (self.CW // 2 - 1)
        for h in self.data:
            self.content += text.remove_superfluous_alineas(h)
            self.content.append(cut_line)

    def handle_event(self, filepath, staged=False):
        self.running.acquire()
        if filepath is None or type(filepath) is not str:
            self.running.release()
            return
        self.data = self.rungit(filepath, staged)
        self.setup_content()
        self.topLineNum = 0
        self.selected_content_line = -1
        self.hovered_content_line = 0
        message = ": " + filepath if type(filepath) == str else ''
        self.title = self.default_title + message
        self.display()
        self.running.release()

    def activate(self):
        self.cursor_y = 1
        super(Diff, self).activate()
        return self


class StagerUnstager(Panel):

    def __init__(self, parent, *args, **kwargs):
        super(StagerUnstager, self).__init__(*args, **kwargs)
        self.parent = parent
        self.default_title = self.title
        self.postponer = Postponer(timeout_in_seconds=0.3)

    def filename_from_linenum(self, linenum):
        if linenum < 0 or linenum >= len(self.content):
            return ''
        line = None
        try:
            line = self.content[linenum]
        except:
            return ''
        return line.split()[1]

    def move_cursor(self):
        super(StagerUnstager, self).move_cursor()
        if self.active:
            self.request_diff_in_diff_view()

    def handle_event(self, event=None):
        super(StagerUnstager, self).handle_event()
        self.request_diff_in_diff_view()

    def activate(self):
        this = super(StagerUnstager, self).activate()
        self.request_diff_in_diff_view()
        return this

    def request_diff_in_diff_view(self, even_not_active=False):
        if not self.active and not even_not_active:
            return
        self.hovered_content_line = self.cursor_y + self.topLineNum - self.CT
        if self.hovered_content_line < 0 or self.hovered_content_line >= len(self.content):
            return
        filepath = self.filename_from_linenum(self.hovered_content_line)
        if self.content and filepath:
            self.postponer.set(
                action=self.parent['diff'].handle_event,
                args=[filepath, (self.title == 'Staging Area')])

    def select(self):
        self.update_selection()
        if self.selected_content_line != -1:
            self.selected_file = self.filename_from_linenum(self.selected_content_line)
            self.cursor_y = max(self.cursor_y - 1, self.CT)
            self.action(self.selected_file)
            self.unselect()
        self.display()


class StateLinePanel(Panel):

    def handle_event(self, event=None):
        self.content = self.rungit()
        for i, line in enumerate(self.content):
            if line.startswith('*'):
                self.decorations[i] = curses.A_BOLD
                self.content[i] = line[1:]
        self.display()


class HistoryPanel(StateLinePanel):

    def handle_event(self, event):
        data = self.rungit()
        self.content = []
        for e in data:
            (labels, msg, author, date, sha1) = e
            for i, b in enumerate(labels):
                labels[i] = '(' + b + ')'
            l2 = min(19, int(self.CW * 0.1))
            l3 = min(19, int(self.CW * 0.15))
            l4 = len(sha1) + 1
            l1 = int(self.CW - l2 - l3 - l4 - 3 * len(' | '))
            message, lm = text.shorten(''.join(labels) + msg, l1)
            author, la = text.shorten(author, l2, dots=False)
            date, ld = text.shorten(date, l3, dots=False)
            sha1, ls = text.shorten(sha1, l4, dots=False)
            line = "{:<{col1}} | {:<{col2}} | {:<{col3}} | {:<{col4}}".format(
                message,
                author,
                date,
                sha1,
                col1=l1,
                col2=l2,
                col3=l3,
                col4=l4)
            self.content.append(line)
        self.content[0] = '*' + self.content[0]
        for i, line in enumerate(self.content):
            if line.startswith('*'):
                self.decorations[i] = curses.A_BOLD
                self.content[i] = line[1:]
        self.display()

class BranchesPanel(StateLinePanel):
    def __init__(self, *args, **kwargs):
        StateLinePanel.__init__(self, *args, **kwargs)
        self.rungit = rungit.git_branches

    def select(self):
        self.update_selection()
        if self.selected_content_line != -1:
            selected_branch = self.content[self.selected_content_line]
            self.decorations = {}
            self.action(selected_branch)
        self.display()

    def action(self, branch):
        rungit.git_checkout_branch(branch)
        self.handle_event()
