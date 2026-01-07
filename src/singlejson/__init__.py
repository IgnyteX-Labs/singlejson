"""Load and save JSON files easily across files.

Public API:
    - Classes: JSONFile, JsonSerializationSettings
    - Functions: load, sync, reset, close
    - Defaults: DEFAULT_SERIALIZATION_SETTINGS
"""

from .__about__ import __version__
from .fileutils import (
    DEFAULT_SERIALIZATION_SETTINGS,
    JSONFile,
    JsonSerializationSettings,
)
from .pool import close, load, reset, sync

__all__ = [
    "load",
    "DEFAULT_SERIALIZATION_SETTINGS",
    "sync",
    "JSONFile",
    "reset",
    "close",
    "JsonSerializationSettings",
    "__version__",
]
