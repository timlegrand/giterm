# Contributing to Giterm

In an effort to continuously improve my coding, any help will be welcome, especially about:

- callback/event management and inter-classes communications
- community-inspired coding/architecture conventions
- unit tests

You can also pick an item from the TODO list if you want.


## Bugs

Giterm should contain some, as it desperatly lacks of testing at this stage. I'm not proud of it, not at all.

I use GitHub issues to track bugs. Please ensure your description has sufficient instructions to be able to reproduce the issue.


## Pull Requests

I actively welcome your pull requests. I'd be happy to merge it as quickly as I can.


## Philosophy

At this stage, I have to admit that Giterm code is pretty dirty. I think a clean code should:

- be readable and concise
- prefer clarity over comments
- be reusable
- have short functions focussing each on one task...
- ...and for which the input and output types are clearly specified
- use composition over inheritance
- use immutable objects where possible
- be thread-safe
- have a layered architecture
- avoid premature optimization


## Dev env

Giterm needs the `git` executable to be installed and available in the PATH of your system.

Giterm requires the externals modules to run. It is recommended to insulate your development environment with `virtualenv`.
If you don't have virtualenv installed, just run:

    sudo pip install -U virtualenv
    sudo pip install -U virtualenvwrapper
    export WORKON_HOME=~/.virtualenvs
    mkdir -p $WORKON_HOME
    source /usr/local/bin/virtualenvwrapper.sh

To set up your dev env:

    # download source
    # cd the source root directory
    mkvirtualenv giterm
    pip install .

To quit the dev env:

    deactivate giterm

To get the dev env back:

    workon giterm

To remove the dev env:

    rmvirtualenv giterm

You can check the state of your dev env any time with:

    pip freeze


## License

By contributing to Giterm, you agree that your contributions will be licensed under the terms given in the [LICENSE](./LICENSE) file.


## Miscellaneous

Recommended listening while developing: [alt-J - An Awesome Wave](https://en.wikipedia.org/wiki/An_Awesome_Wave)
