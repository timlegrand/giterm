.. image:: https://badge.fury.io/py/giterm.svg
    :target: https://badge.fury.io/py/giterm

Features
========

Giterm brings information about the current status of your Git working
copy in *real-time*. It shows in a single view:

-  local branches, and which branch you’re currently on
-  remote branches, and which branch the current local branch is
   tracking
-  commit history, and which commit you are currently working from
-  current changes
-  a *diff* view of the selected file in the *changes* list

Giterm only *shows* Git information. It does not support git actions
like commit checkout, branch switching, staging or committing.

.. note:: Well OK, you should now be able to stage/unstage files with the
   space bar :)


Real-time!
----------

Every change to the working copy (file edition/move or any Git command)
refreshes the GUI instantly. You can work as usual, and keep a terminal
open with giterm to get visual feedback on your actions.


Usage
=====

.. code-block:: bash

    cd path/to/git/working/copy
    giterm


Installation
============

.. code-block:: bash

    pip install giterm

If you don’t have ``pip`` installed yet:

.. code-block:: bash

    curl -s https://bootstrap.pypa.io/get-pip.py | sudo python
    pip install giterm


Requirements
============

Giterm needs the ``git`` executable to be installed and available in the
PATH of your system. Others dependencies should be automatically handled
by ``pip``.


Technical background
====================

Giterm uses subprocesses to call Git shell-based commands, and parses
their outputs to bring the relevant information to the user interface.

It also uses a watchdog to listen file changes in the current working
directory.


License
=======

This software is provided under the BSD 2-Clause License. Please read
the `LICENSE`_ file for further information.


Contribute
==========

See the `CONTRIBUTING.md`_ file for how to help out.

Many thanks for your support!


.. _LICENSE: ./LICENSE
.. _CONTRIBUTING.md: ./CONTRIBUTING.md
