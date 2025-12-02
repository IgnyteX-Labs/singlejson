Advanced usage
==============

Context manager and auto-save
-----------------------------

``JSONFile`` implements ``__enter__``/``__exit__``. By default it saves
automatically on a clean exit (no exception). You can disable this by
passing ``auto_save=False``.

.. code-block:: python

   from singlejson import JSONFile

   # Auto-save on clean exit
   with JSONFile("data.json", default_data={}) as jf:
       jf.json["counter"] = 1

   # No auto-save
   with JSONFile("scratch.json", default_data={}, auto_save=False) as jf:
       jf.json["tmp"] = True


Pooling: one instance per path
------------------------------

``singlejson.load(path)`` returns a shared instance per absolute path,
so different parts of your code operate on the same in-memory object.

.. code-block:: python

   from singlejson import load, sync

   a = load("shared.json", default_data={})
   b = load("shared.json")
   assert a is b
   a.json["x"] = 1
   sync()  # persists changes to disk


Serialization settings
----------------------

Use :class:`singlejson.JsonSerializationSettings` to control indentation,
key ordering, and ASCII escaping. You can set a per-instance default via
``JSONFile(..., settings=...)`` or override on each ``save()``.

.. code-block:: python

   from singlejson import JSONFile, JsonSerializationSettings

   jf = JSONFile("fmt.json", default_data={},
                 settings=JsonSerializationSettings(indent=2, sort_keys=True, ensure_ascii=False))
   jf.json = {"b": 2, "a": 1}
   jf.save()                 # uses the instance settings
   jf.save_atomic()          # atomic write using the same settings


Atomic saves
------------

``JSONFile.save_atomic()`` writes to a temporary file and replaces the target
file in a single operation, helping avoid corruption on crashes.


Error handling
--------------

- Invalid JSON on load is handled gracefully by falling back to ``default_data``.
- ``FileAccessError`` is raised for permission or IO errors during prepare/read/write.
