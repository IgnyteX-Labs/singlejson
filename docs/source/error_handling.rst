.. _error_handling:

Error handling
--------------

By default, ``singlejson`` recovers from errors by replacing invalid
or missing files with the specified default data. You can control this behavior
using the ``strict`` parameter when creating a ``JSONFile`` or using
:func:`singlejson.load()`. If ``strict=True``, an exception will be raised
if the file does not exist or contains invalid JSON.

If the default data is not valid, singlejson will revert to an empty dictionary ``{}``.

.. code-block:: python

   from singlejson import JSONFile, JSONFileError

   # Non-strict mode (default): recovers to default data
   jf = JSONFile("not_created.json", default_data={"key": "value"}, strict=False)
   print(jf.json)  # > {"key": "value"}

   # Strict mode: raises exception on error
   try:
       jf_strict = JSONFile("not_created_file.json", default_path="path/to/nonexistent/or/corrupt/file.json", strict=True)
   except DefaultNotJSONSerializableError as e:
       print(f"Error loading JSON file: {e}")

Error types in singlejson are:

- :class:`~singlejson.fileutils.FileAccessError` Called when the file cannot be accessed due to permission issues or other I/O errors. This is **always** raised. singlejson cannot recover from this,

- :class:`~singlejson.fileutils.DefaultNotJSONSerializableError`: Raised when the provided default data either from ``default_data`` or ``default_path`` is **not valid** JSON. This is only raised when ``strict=True`` or when the default is loaded for the first time.

- :class:`~singlejson.fileutils.JSONDeserializationError`: Raised when the file content is not valid JSON and cannot be deserialized. This is only raised when ``strict=True`` and the file is loaded for the first time.


