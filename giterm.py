#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
from panel import Panel, PanelManager
import watch

def keyloop(panels):
	mainw = panels.stdscr
	height, width = mainw.getmaxyx()
	w_15_pct = width // 7
	w_30_pct = width // 3
	w_55_pct = width - w_30_pct - w_15_pct
	h_49_pct = height // 2
	h_51_pct = height - h_49_pct
	h_25_pct = h_51_pct // 2
	h_26_pct = h_51_pct - h_25_pct
	panels['hier']    = Panel(mainw, height, w_15_pct, 0, 0)
	panels['loghist'] = Panel(mainw, h_49_pct, w_30_pct+w_55_pct, 0, w_15_pct)
	panels['stage']   = Panel(mainw, h_25_pct, w_30_pct, h_49_pct, w_15_pct)
	panels['changes'] = Panel(mainw, h_26_pct, w_30_pct, h_49_pct+h_25_pct, w_15_pct)
	panels['diff']    = Panel(mainw, h_51_pct, w_55_pct, h_49_pct, w_15_pct+w_30_pct)
	active = panels['loghist'].activate()
	panels.display()

	w = watch.Watcher()
	w.subscribe(cb=panels['loghist'].handle_event)
	w.start()

	while True:
		# active.debug()
		c = mainw.getch()
		if 0<c<256:
			c = chr(c)
			if c in ' \n': # 'SPACE BAR' or 'ENTER' hit
				active.select()
			elif c in 'Qq':
				break
			elif c == '\t':
				active = panels.toggle()
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
	panels = PanelManager(stdscr)
	keyloop(panels)

if __name__ == '__main__':
	curses.wrapper(main)
