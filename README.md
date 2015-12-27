# Giterm

A terminal-based GUI client for Git.


# Features

Giterm shows information about the current status of your Git working copy.
It shows in a single view:

- local branches, and which branch you're currently on
- remote branches, and which branch the current local branch is tracking
- commit history, and which commit you are currently working from
- current changes
- a *diff* view of the selected file in the *changes* list

Giterm only *shows* Git information. It does not support git actions like commit *checkout*, *branch switching*, *staging* or *committing*. But it could be in a future realease if you want!

> Well OK, you should now be able to stage/unstage files with the spacebar :)


# Installation

    pip install giterm

If you don't have `pip` installed yet:

    curl -s https://bootstrap.pypa.io/get-pip.py | sudo python
    pip install giterm


# Requirements

Giterm needs the `git` executable to be installed and available in the PATH of your system.
Others dependencies should be automatically handled by `pip`.


# Technical background

Giterm uses subprocesses to call Git shell-based commands, and parses their outputs to bring the relevant information to the user interface.


# License

This software is provided under the BSD 2-Clause License.
Please read the [LICENSE](./LICENSE) file for further information.


# Contribute

See the [CONTRIBUTING.md](./CONTRIBUTING.md) file for how to help out.


Many thanks for your support!
