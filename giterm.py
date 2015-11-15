#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
from itertools import cycle
from panel import Panel
import observer
#from cursutils import debug
import watch

class PanelManager(dict):
	def __init__(self, stdscr):
		super(PanelManager, self).__init__()
		self.stdscr = stdscr

	def append(self, name, panel):
		# super(PanelManager, self).append(panel)
		self[name] = panel
		return panel

	def toggle(self):
		it = cycle(self.iteritems())
		for k, panel in it:
			if panel.active:
				panel.deactivate()
				return next(it)[1].activate()

	def display(self):
		active = None
		for k, panel in self.iteritems():
			panel.display()
			if panel.active:
				active = panel
		self.stdscr.move(*active.getcontentyx())

def keyloop(panels):
	mainw = panels.stdscr
	width, height = mainw.getmaxyx()
	w_20_percent = height * 2 // 10
	w_80_percent = height - w_20_percent
	panels['hier']    = Panel(mainw, width-4, w_20_percent, 0, 0)
	panels['loghist'] = Panel(mainw, width-4, w_80_percent, 0, w_20_percent)
	panels['status']  = Panel(mainw, 4, height, width-4, 0)
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
