# -*- coding: utf-8 -*-
import curses

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
            raise Exception("Height and width must be at least 8x80.\
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
        self['stage'] = Panel(self.stdscr, h_25, w_30, h_49, w_20, title='Staging Area')
        self['changes'] = Changes(self, self.stdscr, h_26, w_30, h_49 + h_25, w_20, title='Local Changes')
        self['diff'] = Diff(self.stdscr, h_51, w_50, h_49, w_20 + w_30, title='Diff View')

        self['changes'].rungit = rungit.git_changed
        self['stage'].rungit = rungit.git_staged
        self['log'].rungit = rungit.git_history
        self['hier'].rungit = rungit.git_hierarchies
        self['diff'].rungit = rungit.git_diff


class Diff(Panel):

    def __init__(self, *args, **kwargs):
        super(Diff, self).__init__(*args, **kwargs)
        self.default_title = self.title

    def handle_event(self, filepath):
        self.content = self.rungit(filepath)
        self.title = ": " + filepath if type(filepath) == str else ''
        self.title = self.default_title + self.title
        self.display()


class Changes(Panel):

    def __init__(self, parent, *args, **kwargs):
        super(Changes, self).__init__(*args, **kwargs)
        self.parent = parent
        self.default_title = self.title

    def filename_from_linenum(self, linenum):
        return self.content[linenum].split()[1]

    def _move_cursor(self):
        hovered = self.topLineNum + self.cursor_y - self.CT
        self.parent['diff'].handle_event(self.filename_from_linenum(hovered))
        # TODO: fire git_diff only when hovering for a given delay (0.5 s)
        super(Changes, self)._move_cursor()

    def select(self):
        hovered = self.topLineNum + self.cursor_y - self.CT
        self.selected_line = -1 if self.selected_line == hovered else hovered
        if self.selected_line != -1:
            self.selected_file = self.filename_from_linenum(self.selected_line)
            # TODO: next step, git_action_stage(file) on selection?
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
