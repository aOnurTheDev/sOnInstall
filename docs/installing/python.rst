.. _installing.python:

Python library
==============

sOninstall can also be used as a Python library, imported as ``soninstall``.

.. warning::
    These steps are not required if you want to use sOninstall on the sOnOs ISO, where it is already installed.

Installing from the AUR
-----------------------

The ``soninstall-git`` package in the `AUR <https://aur.archlinux.org/>`_ installs both the library and the ``soninstall`` command:

.. code-block:: console

    git clone https://aur.archlinux.org/soninstall-git.git
    cd soninstall-git
    makepkg -si

.. _installing.python.manual:

Install using source code
-------------------------

You can also install using the source code.
For sake of simplicity we will use ``git clone`` in this example.

.. code-block:: console

    git clone https://github.com/aOnurTheDev/sOnInstall

You can either move the folder into your project and simply do

.. code-block:: python

    import soninstall

Or you can use PyPA's `build <https://github.com/pypa/build>`_ and `installer <https://github.com/pypa/installer>`_ to install it into pythons module path.

.. code-block:: console

    $ cd sOnInstall
    $ python -m build .
    $ python -m installer dist/*.whl
