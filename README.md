# Giterm

A terminal-based, graphical user interface for Git.


# Features

Giterm shows information about the current status of your Git working copy.
It shows in a single view:

- local branches, and which branch you're currently on;
- remote branches, and which branch the current local branch is tracking;
- commit history, and which commit you are currently working from;
- current changes;
- a *diff* view of the selected file in the *changes* list.

Giterm only *shows* Git information. It **does not** support git actions like commit checkout, branch switching, staging or committing. But it could be an idea for next realeases if you're insterested!

> Well, OK, you're now able to stage/unstage files with the spacebar, just to know it's possible.


# Requirements

Giterm needs the git executable to be installed and available in the PATH of your system.

Giterm requires the `watchdog` module to run.
If you have virtualenv installed, just run:

	pip install -r requirements.txt


# Technical background

Giterm uses subprocesses to call Git shell-based commands, and parses their outputs to bring the relevant information to the UI. All apologies. Wan't to improve that? Contribute!


# Bugs

Should contain some, as it desperatly lacks of testing at this stage. I'm not proud of it, not at all.

As for feature-requests, feel free to create a pull request for any bug you meet. I'd be happy to merge it as quickly as I can.


# Contribute

In an effort to continuously improve my coding, any help will be welcome, especially about:

- callback/event management and inter-classes communications;
- PEP8 and other community-inspired coding/architecture conventions;
- unit tests;
- Python package creation and publication;

or you can pick an item from the TODO list.


# License

This software is provided under the BSD 2-Clause License.
Please read [the LICENSE.md file](./LICENSE.md) for further information.


Many thanks for your support!
