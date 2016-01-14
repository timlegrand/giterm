# -*- coding: utf-8 -*-
from nose.tools import *

import giterm.textutils


def setup():
    pass


def teardown():
    pass


def test_shorten():

    string = 'Hi, this is a long string that should be shorten.'
    new_string, num_raw_bytes = giterm.textutils.shorten(string, size=18)

    assert len(new_string) == 18
    assert num_raw_bytes == 49  # raw_bytes(new_string) or raw_bytes(string)?
    assert new_string == 'Hi, this is a l...'
