# -*- coding: utf-8 -*-
import giterm.textutils as textutils


def setup():
    pass


def teardown():
    pass


def test_shorten():

    string = 'Hi, this is a long string that should be shorten.'
    new_string, num_raw_bytes = textutils.shorten(string, size=18)

    assert len(new_string) == 18
    assert num_raw_bytes == 49  # raw_bytes(new_string) or raw_bytes(string)?
    assert new_string == 'Hi, this is a l...'


def test_blocks():

    text = '''@@ -118,6 +118,7 @@ def git_submodules():

 def git_tags():
     data = run('git tag')
+    # If Git >= 2.3.3 'git log --date-order --tags --simplify-by-decoration \
--pretty=format:"%d"'
     return data


@@ -135,8 +136,6 @@ def git_diff(path):
             error = 0
     else:
         data = data[4:]
-    # import cursutils
-    # cursutils.debug()
     if error:
         raise Exception('Error executing "' + cmd + '" (error = ' + \
str(error))
    '''.split('\n')

    blocks = textutils.blocks(text, lambda x: x and x.startswith('@@'))

    assert len(list(blocks)) == 2
