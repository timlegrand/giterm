# -*- coding: utf-8 -*-
import curses
import threading

from panel import Panel, PanelManager
from postponer import Postponer
import rungit


class GitermPanelManager(PanelManager):

    def __init__(self, stdscr):
        super(GitermPanelManager, self).__init__(stdscr)
        self.create_panels()

    def create_panels(self):
        """Creates a graphical-like UI:
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
            raise Exception("Height and width must be at least 8x40.\
                Currently: %sx%s" % (height, width))
        # Following sizes are percentages (e.g. w_30 is 30% of screen width)
        w_20 = min(max(width // 5, 20), 25)
        w_30 = width // 3
        w_50 = width - w_30 - w_20
        h_49 = height // 2
        h_51 = height - h_49
        h_25 = h_51 // 2
        h_26 = h_51 - h_25
        self['hier'] = Hierarchies(self.stdscr, height, w_20, 0, 0, title='')
        self['log'] = Panel(self.stdscr, h_49, w_30 + w_50, 0, w_20, title='History')
        self['stage'] = StagerUnstager(self, self.stdscr, h_25, w_30, h_49, w_20, title='Staging Area')
        self['changes'] = StagerUnstager(self, self.stdscr, h_26, w_30, h_49 + h_25, w_20, title='Local Changes')
        self['diff'] = Diff(self.stdscr, h_51, w_50, h_49, w_20 + w_30, title='Diff View')

        self['changes'].rungit = rungit.git_changed
        self['stage'].rungit = rungit.git_staged
        self['log'].rungit = rungit.git_history
        self['hier'].rungit = rungit.git_hierarchies
        self['diff'].rungit = rungit.git_diff

        self['changes'].action = self.stage_file
        self['stage'].action = self.unstage_file

    def stage_file(self, path):
        rungit.git_stage_file(path)
        self['stage'].handle_event(None)
        self['changes'].handle_event(None)

    def unstage_file(self, path):
        rungit.git_unstage_file(path)
        self['stage'].handle_event(None)
        self['changes'].handle_event(None)


class Diff(Panel):

    def __init__(self, *args, **kwargs):
        super(Diff, self).__init__(*args, **kwargs)
        self.default_title = self.title
        self.running = threading.Lock()

    def handle_event(self, filepath):
        if type(filepath) is not str:
            return
        self.running.acquire()
        self.content = self.rungit(filepath)
        self.title = ": " + filepath if type(filepath) == str else ''
        self.title = self.default_title + self.title
        self.display()
        self.running.release()


class StagerUnstager(Panel):

    def __init__(self, parent, *args, **kwargs):
        super(StagerUnstager, self).__init__(*args, **kwargs)
        self.parent = parent
        self.default_title = self.title
        self.postponer = Postponer(timeout_in_seconds=0.3)

    def filename_from_linenum(self, linenum):
        if len(self.content) <= linenum:
            # TODO: log error and raise exception
            return 'error: l.%s>%s' % (linenum, str(len(self.content)+1))
        return self.content[linenum].split()[1]

    def move_cursor(self):
        super(StagerUnstager, self).move_cursor()
        self.request_diff_in_diff_view()

    def request_diff_in_diff_view(self):
        if self.content:
            self.postponer.set(
                action=self.parent['diff'].handle_event,
                args=[self.filename_from_linenum(self.hovered_line)])

    def select(self):
        if self.selected_line == self.hovered_line:
            self.selected_line = -1
        else:
            self.selected_line = self.hovered_line
        if self.selected_line != -1:
            self.selected_file = self.filename_from_linenum(self.selected_line)
            self.cursor_y = max(self.cursor_y - 1, self.CT)
            self.action(self.selected_file)
            self.unselect()
        self.display()


class Hierarchies(Panel):

    def draw_content(self):
        top = self.topLineNum
        bottom = self.topLineNum + self.CH
        for i, line in enumerate(self.content[top:bottom]):
            y = i + self.CT
            current = True if line.endswith('*') else False
            line = line[:-1] if current else line
            self.add_content_line(y, line)
            if self.active and self.cursor_y == y or current:
                self.window.chgat(y, self.CL, self.CR, curses.A_BOLD)
            if self.selected_line != -1 and\
                    y == self.selected_line + self.CT - self.topLineNum:
                self.window.chgat(y, self.CL, self.CR, curses.A_REVERSE)
            # TODO: need to handle case of last line fulfilled
            # with scrolling disabled
