.. _defaults:

Default handling
-----------------
You can specify default data to be used when the file does not exist or
contains invalid JSON.
This can be done in multiple ways:
Pass these options to :class:`singlejson.JSONFile` or :func:`singlejson.load`.

``default_data``
""""""""""""""""""
Pass a ``dict`` which will be copied and then used as is.
This is useful if you only have one place where you call load but gets tedious
if you need to call load() in multiple places.

.. code-block:: python
    :caption: Using default_data

    import singlejson

    # If 'config.json' doesn't exist, it will be created with these contents
    config = singlejson.load(
        "config.json",
        default_data={"theme": "dark", "notifications": True}
    )

    print(config.json["theme"])  # > dark

``default_data`` will be overruled by ``default_path`` if both are provided.

``default_path``
""""""""""""""""""""
Pass a path to a JSON file which will be loaded and used as default.
You can ship a defaults/ folder with your application and point to files there.
Every load call always refers to this file.

.. code-block:: python
    :caption: Using default_path

    import singlejson
    from pathlib import Path

    # Assuming 'defaults/settings_template.json' exists with some data
    template = Path("defaults/settings_template.json")

    # If 'user_settings.json' is missing, it copies the template
    settings = singlejson.load("user_settings.json", default_path=template)

``default_path`` takes precedence over ``default_data`` if both are provided.

Strict mode
""""""""""""""""""
You can also pass the option ``strict`` which checks defaults before
loading for the first time.
If ``strict=True`` (the default), an exception is raised if the default file does not exist
or contains invalid JSON, or if the provided ``default_data`` is not JSON-serializable.

.. code-block:: python
    :caption: More about :ref:`error_handling`.

    import singlejson
    from singlejson.fileutils import DefaultNotJSONSerializableError

    try:
        # This will fail because a set() is not JSON serializable
        singlejson.load("data.json", default_data={"myset": {1, 2, 3}}, strict=True)
    except DefaultNotJSONSerializableError as e:
        print(f"Caught expected error: {e}")


