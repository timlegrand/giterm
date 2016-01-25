# -*- coding: utf-8 -*-
from threading import Timer


class Postponer(object):
    '''Fires a callback on timeout, unless timer is reset by new instructions.
    '''
    def __init__(self, timeout_in_seconds=None, action=None, *args, **kwargs):
        self.timeout = timeout_in_seconds if timeout_in_seconds else 1.0
        self.handler = action if action else self.defaultHandler
        self.timer = Timer(self.timeout, self.handler)
        # self.set(self.timeout, self.handler, *args, **kwargs)

    def set(self, timeout_in_seconds=None, action=None, *args, **kwargs):
        '''Fires a callback with its arguments on timeout.
        If called again before timeout, registers new instructions and
        resets timer.
        '''
        self.timer.cancel()

        if action:
            self.handler = action
        if timeout_in_seconds:
            self.timeout = timeout_in_seconds

        self.timer = Timer(self.timeout, self.handler, *args, **kwargs)
        self.timer.start()

    def reset(self, timeout_in_seconds=None, action=None, *args, **kwargs):
        self.set(timeout_in_seconds, action)

    def cancel(self):
        self.timer.cancel()

    def defaultHandler(self):
        raise Exception('Timeout reached!')


if __name__ == '__main__':

    import time

    def cancel_with_logging(self):
        self.timer.cancel()
        print 'Timer reset.'

    Postponer.cancel = cancel_with_logging

    def print_args(args, kwargs):
        if args or kwargs:
            arguments = [x for x in args]
            arguments += [k + '=' + x for k, x in kwargs.iteritems()]
        else:
            arguments = 'no arguments'
        return arguments

    def please_work(*args, **kwargs):
        print 'please_work() executed with: %s' % print_args(args, kwargs)

    def no_do_that_instead(*args, **kwargs):
        print 'no_that_instead() executed with: %s' % print_args(args, kwargs)

    # Instanciation does not start the timer
    p = Postponer(timeout_in_seconds=1.0)
    p.set()  # start timer for one second
    time.sleep(0.5)
    p.set(action=please_work)  # new callback, timer reset
    time.sleep(0.5)
    # Let's input new parameters, the timer resets
    p.set(
        timeout_in_seconds=0.6,
        args=['arg#1', 'arg#2'],
        kwargs={'file': 'this'})
    time.sleep(1.5)
    # Let's input new parameters, the timer resets
    p.set(timeout_in_seconds=0.6, action=no_do_that_instead)
    time.sleep(0.5)
    # Timer resets again
    p.set(timeout_in_seconds=0.6)
    time.sleep(0.7)
    # Ang again
    p.set(timeout_in_seconds=0.6, args=['no this file instead'])
    time.sleep(0.5)
