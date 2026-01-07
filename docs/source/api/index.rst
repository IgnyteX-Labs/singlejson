API Reference
=============

Top-level package
-----------------

The main interface for ``singlejson``. These members are re-exported from
internal modules for convenience.

.. automodule:: singlejson
    :members:
    :undoc-members:
    :show-inheritance:
    :imported-members:


File utilities
--------------

This module contains the implementation details for file I/O and JSON serialization.
Most of these are also available directly from the :mod:`singlejson` package.

.. automodule:: singlejson.fileutils
   :members:
   :undoc-members:
   :show-inheritance:


Pooling
-------

This module manages the global file pool.
The functions here are also available directly from the :mod:`singlejson` package.

.. automodule:: singlejson.pool
   :members:
   :undoc-members:
   :show-inheritance:


Version metadata
----------------

.. automodule:: singlejson.__about__
   :members:
   :undoc-members:
   :show-inheritance:
