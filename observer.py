# -*- coding: utf-8 -*-

class Event(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)


class Observable(object):
    def __init__(self):
        self.callbacks = set()

    def subscribe(self, callback):
        self.callbacks.add(callback)
        
    def unsubscribe(self, callback):
        self.callbacks.discard(callback)

    def fire(self, **attrs):
        e = Event(source=self, **attrs)
        for fn in self.callbacks:
            fn(e)