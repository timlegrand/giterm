Contributing to Giterm
======================

In an effort to continuously improve my coding, any help will be
welcome, especially about:

-  callback/event management and inter-classes communications
-  community-inspired coding/architecture conventions
-  unit tests

You can also pick an item from the TODO list if you want.


TODO
----

- [ ] move `utils/` scripts to a Makefile
- [ ] complete Python2 support removal
- [ ] plug back CI
- [ ] check and update badges
- [ ] move Git commands to `GitPython_`
- [ ] add graph to history
- [ ] move TUI to rich and/or textual


Bugs
----

Giterm should contain some, as it desperatly lacks of testing at this
stage. I’m not proud of it, not at all.

I use GitHub issues to track bugs. Please ensure your description has
sufficient instructions to be able to reproduce the issue.


Pull Requests
-------------

I actively welcome your pull requests. I’d be happy to merge it as
quickly as I can.


Philosophy
----------

At this stage, I have to admit that Giterm code is pretty dirty. I think
a clean code should:

-  be readable and concise
-  prefer clarity over comments
-  be reusable
-  have short functions focussing each on one task…
-  …and for which the input and output types are clearly specified
-  use composition over inheritance
-  use immutable objects where possible
-  be thread-safe
-  have a layered architecture
-  avoid premature optimization


Dev env
-------

Giterm needs the ``git`` executable to be installed and available in the
PATH of your system.

Giterm requires externals modules to run. It is recommended to
insulate your development environment with ``virtualenv``. If you don’t
have virtualenv installed, just run:

.. code-block:: bash

    sudo pip install -U virtualenv
    sudo pip install -U virtualenvwrapper
    export WORKON_HOME=~/.virtualenvs
    mkdir -p $WORKON_HOME
    source /usr/local/bin/virtualenvwrapper.sh

To set up your dev env:

.. code-block:: bash

    # download source
    # cd the source root directory
    mkvirtualenv giterm
    pip install -r requirements.txt

To quit the dev env:

.. code-block:: bash

    deactivate giterm

To get the dev env back:

.. code-block:: bash

    workon giterm

To remove the dev env:

.. code-block:: bash

    rmvirtualenv giterm

You can check the state of your dev env any time with:

.. code-block:: bash

    pip freeze


Tests
-----

To set up the testing/packaging env:

.. code-block:: bash

    mkvirtualenv packaging
    pip install -r packaging-requirements.txt

Testing:

.. code-block:: bash

    tox -e py38


Package testing
---------------

One can test setup.py installers::

    mkvirtualenv --python=python3 giterm
    pip install -e .
    giterm
    deactivate
    rmvirtualenv giterm


License
-------

By contributing to Giterm, you agree that your contributions will be
licensed under the terms given in the `LICENSE file`_.


Miscellaneous
-------------

Recommended listening while developing: `alt-J - An Awesome Wave`_


.. _LICENSE file: ./LICENSE
.. _alt-J - An Awesome Wave: https://en.wikipedia.org/wiki/An_Awesome_Wave
.. _GitPython: https://gitpython.readthedocs.io/