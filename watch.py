#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import observer as cb

class FileChangedHandler(FileSystemEventHandler, cb.Observable):

	def on_any_event(self, event):
		if event.src_path == "." or ".git" in event.src_path:
			return
		p = event.src_path
		if event.src_path[:2] == "./":
			p = event.src_path[2:]

		message = event.event_type + ": " + p
		message = message[0].upper() + message[1:]
		self.action(message)

	def action(self, msg):
		if self.callbacks:
			self.fire(content=msg)
		else:
			print msg

class Watcher(object):
	def __init__(self, path='.'):
		super(Watcher, self).__init__()
		self.path = path
		self.event_handler = FileChangedHandler()
		self.observer = Observer(timeout=0.4)
		self.observer.schedule(self.event_handler, self.path, recursive=True)

	def start(self):
		self.observer.start()

	def stop(self):
		self.observer.stop()
		self.observer.join()

if __name__ == "__main__":
	watchdir = sys.argv[1] if len(sys.argv) > 1 else '.'
	w = Watcher()
	w.start()
	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		w.stop()
