#!/usr/bin/env python
# -*- coding: utf-8 -*-
import curses
import argparse
import os

import watch
import rungit
import cursutils

from gui import GitermPanelManager
from _version import __version_text__
from exception import *


def keyloop(stdscr):
    panels = GitermPanelManager(stdscr)
    active = panels['history'].activate()
    panels.display()

    w = watch.Watcher()
    for name, panel in panels.iteritems():
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
                active.select()
            elif c in 'Qq':
                break
            elif c == '\t':
                active = panels.toggle()
            elif c == 'h':
                active.deactivate()
                active = panels['history'].activate()
            elif c == 'c':
                active.deactivate()
                active = panels['changes'].activate()
            elif c == 's':
                active.deactivate()
                active = panels['stage'].activate()
            elif c == 'd':
                active.deactivate()
                active = panels['diff'].activate()
            elif c == 'b':
                active.deactivate()
                active = panels['branches'].activate()
            elif c == 'r':
                active.deactivate()
                active = panels['remotes'].activate()
            elif c == 't':
                active.deactivate()
                active = panels['tags'].activate()
        elif c == curses.KEY_BTAB:
            active = panels.toggle(reverse=True)
        elif c == curses.KEY_UP:
            active.move_up()
        elif c == curses.KEY_LEFT:
            active.move_left()
        elif c == curses.KEY_DOWN:
            active.move_down()
        elif c == curses.KEY_RIGHT:
            active.move_right()
        elif c == curses.KEY_PPAGE:
            active.move_prev_page()
        elif c == curses.KEY_NPAGE:
            active.move_next_page()
        elif c == curses.KEY_RESIZE:
            pass  # TODO: handle terminal resize properly (downsize and upsize)
        else:
            pass

    w.stop()


def main(stdscr):
    cursutils.init(stdscr)
    current_dir = os.getcwd()
    try:
        git_root_dir = rungit.git_root_path()
        os.chdir(git_root_dir)
        keyloop(stdscr)
    except Exception as e:
        cursutils.finalize(stdscr)
        t = type(e)
        if t == NotAGitRepositoryException or t == GitNotFoundException:
            print e
        else:
            raise
    finally:
        os.chdir(current_dir)


def _main():
    parser = argparse.ArgumentParser(
        description='''A terminal-based GUI client for Git.''')
    parser.add_argument(
        '-v', '--version', action='version', version=__version_text__)
    parser.parse_args()
    curses.wrapper(main)


if __name__ == '__main__':
    _main()
