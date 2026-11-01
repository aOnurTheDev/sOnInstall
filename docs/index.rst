sOninstall Documentation
=========================

**sOninstall** is the guided installer for sOnOs, and a library which can be used to install Arch Linux based systems.
The library comes packaged with different pre-configured installers, such as the default :ref:`guided` installer.

Some of the features of sOninstall are:

* **Context friendly.** The library always executes calls in sequential order to ensure installation-steps don't overlap or execute in the wrong order. It also supports *(and uses)* context wrappers to ensure cleanup and final tasks such as ``mkinitcpio`` are called when needed.

* **Full transparency** Logs and insights can be found at ``/var/log/soninstall`` both in the live ISO and partially on the installed system.

* **Accessibility friendly** sOninstall works with ``espeakup`` and other accessibility tools thanks to the use of a TUI.

.. toctree::
   :maxdepth: 1
   :caption: Running sOninstall

   installing/guided

.. toctree::
   :maxdepth: 1
   :caption: Configuration

   cli_parameters/config/disk_config
   cli_parameters/config/disk_encryption
   cli_parameters/config/custom_commands

.. toctree::
   :maxdepth: 3
   :caption: Getting help

   help/known_issues
   help/report_bug
   help/discord

.. toctree::
   :maxdepth: 3
   :caption: sOninstall as a library

   installing/python
   examples/python
   soninstall/plugins

.. toctree::
   :maxdepth: 3
   :caption: API Reference

   soninstall/Installer
