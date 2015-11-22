#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
from panel import Panel, PanelManager
import watch

def keyloop(stdscr):
	panels = PanelManager(stdscr)
	active = panels['loghist'].activate()
	panels.display()

	w = watch.Watcher()
	w.event_handler.subscribe(panels['changes'].handle_event)
	w.event_handler.subscribe(panels['stage'].handle_event)
	w.event_handler.subscribe(panels['loghist'].handle_event)
	w.event_handler.subscribe(panels['hier'].handle_event)
	w.event_handler.subscribe(panels['diff'].handle_event)

	w.event_handler.fire()

	w.start()

	while True:
		c = stdscr.getch()
		if 0<c<256:
			c = chr(c)
			if c in ' \n': # 'SPACE BAR' or 'ENTER' hit
				active.select()
			elif c in 'Qq':
				break
			elif c == '\t':
				active = panels.toggle()
		elif c == curses.KEY_BTAB  : active = panels.toggle(reverse=True)
		elif c == curses.KEY_UP    : active.move_up()
		elif c == curses.KEY_LEFT  : active.move_left()
		elif c == curses.KEY_DOWN  : active.move_down()
		elif c == curses.KEY_RIGHT : active.move_right()
		elif c == curses.KEY_RESIZE:
			pass #TODO: handle terminal resize properly (downsize and upsize)
		else:
			pass

	w.stop()

def main(stdscr):
	keyloop(stdscr)

if __name__ == '__main__':
	curses.wrapper(main)
