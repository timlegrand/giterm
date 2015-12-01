# -*- coding: utf-8 -*-


class Event(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)


class Trigger(object):
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


if __name__ == '__main__':

    def callback1(event):
        print 'Callback #1 got fired with: ' + event.message

    def callback2(event):
        print 'Callback #2 got fired with: ' + event.message

    o = Trigger()
    o.subscribe(callback1)
    o.subscribe(callback2)
    o.fire(message='first trigger')
    o.unsubscribe(callback1)
    o.fire(message='second trigger')
