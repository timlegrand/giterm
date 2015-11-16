#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
from panel import Panel, PanelManager
import watch

def keyloop(panels):
	mainw = panels.stdscr
	height, width = mainw.getmaxyx()
	w_25_percent = width // 4
	w_75_percent = width - w_25_percent
	panels['hier']    = Panel(mainw, height-4, w_25_percent, 0, 0)
	panels['loghist'] = Panel(mainw, height-4, w_75_percent, 0, w_25_percent)
	panels['status']  = Panel(mainw, 4, width, height-4, 0)
	active = panels['loghist'].activate()
	panels.display()

	w = watch.Watcher()
	w.subscribe(cb=panels['status'].set_content)
	w.start()

	while True:
		# active.debug()
		c = mainw.getch()
		if 0<c<256:
			c = chr(c)
			if c in ' \n': # 'space bar' hit
				break
			elif c in 'Qq':
				break
			elif c == '\t':
				active = panels.toggle()
		elif c == curses.KEY_UP    : active.move_up()
		elif c == curses.KEY_LEFT  : active.move_left()
		elif c == curses.KEY_DOWN  : active.move_down()
		elif c == curses.KEY_RIGHT : active.move_right()
		elif c == curses.KEY_RESIZE:
			mainw.clear()
			pass
			#TODO: handle terminal resize properly (downsize and upsize)
		else:
			pass

	w.stop()

def main(stdscr):
	panels = PanelManager(stdscr)
	keyloop(panels)

if __name__ == '__main__':
	curses.wrapper(main)
