API Reference
=============

Top-level package
-----------------

The main ``singlejson`` package.

singlejson exports the :class:`~singlejson.fileutils.JSONFile` class
as well as many functions from the :mod:`singlejson.pool` module:

* :func:`~singlejson.pool.load`
* :func:`~singlejson.pool.sync`
* :func:`~singlejson.pool.reset`
* :func:`~singlejson.pool.close`

To access default serialization settings, use:

* :data:`~singlejson.DEFAULT_SERIALIZATION_SETTINGS`
* :class:`~singlejson.fileutils.JsonSerializationSettings`

.. py:data:: singlejson.DEFAULT_SERIALIZATION_SETTINGS
    :type: JsonSerializationSettings

    The global default serialization settings instance.

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

