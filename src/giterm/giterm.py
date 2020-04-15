#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import curses
import argparse
import os
import six

import giterm.watch as watch
import giterm.rungit as run
import giterm.cursutils as cu

from giterm.colors import colors
from giterm.gui import GitermPanelManager
from giterm._version import __version_text__

def keyloop(stdscr):
    panels = GitermPanelManager(stdscr)
    panels.active = 'history'
    panels.display()

    w = watch.Watcher()
    for name, panel in six.iteritems(panels):
        w.event_handler.subscribe(panel.handle_event)

    # Initialize contents
    w.event_handler.fire()
    panels['changes'].request_diff_in_diff_view(even_not_active=True)

    w.start()
    
    while True:
        c = stdscr.getch()
        if 0 < c < 256:
            c = chr(c)
            if c in ' \n':  # 'SPACE BAR' or 'ENTER' hit
                panels.select()
            elif c in 'Qq' or c == chr(27):  # 27 is Escape key
                if panels.pop:
                    panels.popup_close()
                else:
                    break
            if not panels.pop:
                if c == '\t':
                    panels.toggle()
                elif c == 'h':
                    panels.active = 'history'
                elif c == 'c':
                    panels.active = 'changes'
                elif c == 's':
                    panels.active = 'stage'
                elif c == 'd':
                    panels.active = 'diff'
                elif c == 'b':
                    panels.active = 'branches'
                elif c == 'r':
                    panels.active = 'remotes'
                elif c == 't':
                    panels.active = 'tags'
        elif c == curses.KEY_BTAB:
            panels.toggle(reverse=True)
        elif c == curses.KEY_UP:
            panels.active.move_up()
        elif c == curses.KEY_LEFT:
            panels.active.move_left()
        elif c == curses.KEY_DOWN:
            panels.active.move_down()
        elif c == curses.KEY_RIGHT:
            panels.active.move_right()
        elif c == curses.KEY_PPAGE:
            panels.active.move_prev_page()
        elif c == curses.KEY_NPAGE:
            panels.active.move_next_page()
        elif c == curses.KEY_RESIZE:
            w.stop()
            for name, panel in six.iteritems(panels):
                w.event_handler.unsubscribe(panel.handle_event)
            del panels
            del w

            import time
            time.sleep(0.5)  # Give a chance to the resize event to complete
            curses.flushinp()  # prevent interpreting next queued KEY_RESIZE

            panels = GitermPanelManager(stdscr)
            panels.active = 'history'
            panels.display()

            w = watch.Watcher()
            for name, panel in six.iteritems(panels):
                w.event_handler.subscribe(panel.handle_event)

            # Initialize contents
            w.event_handler.fire()
            panels['changes'].request_diff_in_diff_view(even_not_active=True)

            w.start()
        else:
            pass

    w.stop()

def main(stdscr, repo=None):
    cu.init(stdscr)
    current_dir = os.getcwd()

    colors.create()

    # If we were given a repository directory,
    #   use it instead of our cwd.
    if repo:
        os.chdir(repo)

    try:
        run.create_repo(os.getcwd())

        keyloop(stdscr)
    except:
        raise
    finally:
        os.chdir(current_dir)


def _main():
    parser = argparse.ArgumentParser(
        description='''A terminal-based GUI client for Git.''')
    parser.add_argument(
        '-v', '--version', action='version', version=__version_text__)
    parser.add_argument('repo',
        nargs='?', help='(Optional) Path to git repository; will default to cwd if not given.')
    args = parser.parse_args()

    # Setup ESCAPE key
    os.environ.setdefault('ESCDELAY', '5')

    curses.wrapper(main, repo=args.repo)


if __name__ == '__main__':
    _main()
