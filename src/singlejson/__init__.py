"""Load and save JSON files easily across files.

Public API:
- Classes: JSONFile, JsonSerializationSettings
- Functions: load, sync, reset, close
- Defaults: DEFAULT_SERIALIZATION_SETTINGS
"""

from .fileutils import (
    JSONFile,
    JsonSerializationSettings,
    DEFAULT_SERIALIZATION_SETTINGS,
)
from .pool import load, sync, reset, close
from .__about__ import __version__

__all__ = [
    "JSONFile",
    "JsonSerializationSettings",
    "DEFAULT_SERIALIZATION_SETTINGS",
    "load",
    "sync",
    "reset",
    "close",
]
