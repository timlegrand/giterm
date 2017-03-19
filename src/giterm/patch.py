# -*- coding: utf-8 -*-
from __future__ import absolute_import

import giterm.rungit as rungit


class Patch(object):
    def __init__(self, file):
        self.file = file
        self.generate()

    def generate(self):
        self.content = rungit.git_raw_diff(self.file)
        pass

    def load(self):
        pass

    def save(self):
        pass

    def apply(self):
        # rungit.git_apply_patch(self.content)
        pass

    def __str__(self):
        return self.content


if __name__ == '__main__':
    p = Patch('src/giterm/patch.py')
    # p.apply()
    print(p)
