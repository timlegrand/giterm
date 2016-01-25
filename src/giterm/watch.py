# -*- coding: utf-8 -*-
import sys

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from observer import Trigger


# Prevent tracking '.goutputstream-*' files (known Ubuntu bug)
GIT_BLACK_LIST = ['.git/index.lock', '.goutputstream']
GIT_WHITE_LIST = ['.gitignore', '.gitconfig', '.gitmodules']


class FileChangedHandler(FileSystemEventHandler, Trigger):
    def on_any_event(self, event):
        path = event.src_path
        if path.startswith('./'):
            path = path[2:]
        if path == '.git':
            # Not interested by the '.git' folder itself, only its contents
            return
        for forbidden in GIT_BLACK_LIST:
            if path.startswith(forbidden):
                if path not in GIT_WHITE_LIST:
                    return
                else:
                    break
        message = event.event_type + ': ' + path
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


if __name__ == '__main__':
    import time
    watchdir = sys.argv[1] if len(sys.argv) > 1 else '.'
    w = Watcher()
    w.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        w.stop()
