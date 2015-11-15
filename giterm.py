#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
from itertools import cycle
from panel import Panel
import observer
#from cursutils import debug
import watch

class PanelManager(list):
	def __init__(self, stdscr):
		super(PanelManager, self).__init__()
		self.stdscr = stdscr

	def append(self, panel):
		super(PanelManager, self).append(panel)
		return panel

	def toggle(self):
		it = cycle(self)
		for panel in it:
			if panel.active:
				panel.deactivate()
				return next(it).activate()

	def display(self):
		for panel in self:
			panel.display()

def keyloop(panels):
	mainw = panels.stdscr
	mainw_y, mainw_x = mainw.getmaxyx()
	w_20_percent = mainw_x * 2 // 10
	w_80_percent = mainw_x - w_20_percent
	panels.append(Panel(mainw, mainw_y-4, w_80_percent, 0, w_20_percent))
	panels.append(Panel(mainw, 4, mainw_x, mainw_y-4, 0))
	active = panels.append(Panel(mainw, mainw_y-4, w_20_percent, 0, 0)).activate()
	panels.display()
	mainw.move(active.CNT_T, active.CNT_L)


	w = watch.Watcher()
	w.subscribe(cb=panels[0].set_content)
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
