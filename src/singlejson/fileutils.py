"""Utils for handling IO and JSON operations."""
from __future__ import annotations

import json
import logging
import os
import shutil
import threading
import warnings
from copy import deepcopy
from dataclasses import dataclass
from json import dumps, load as json_load
from pathlib import Path
from tempfile import NamedTemporaryFile
from types import TracebackType
from typing import Any, TypeAlias

JSONSerializable: TypeAlias = (
        dict[str, "JSONSerializable"]
        | list["JSONSerializable"]
        | str
        | int
        | float
        | bool
        | None
)

PathOrSimilar = str | os.PathLike[str]

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class JsonSerializationSettings:
    indent: int = 4
    sort_keys: bool = True
    ensure_ascii: bool = False
    encoding: str = "utf-8"


def abs_filename(file: PathOrSimilar) -> Path:
    """
    Return the absolute path of a file as :class:`pathlib.Path`.

    :param file: File to get the absolute path of
    :return: Absolute Path of file
    """
    return Path(file).expanduser().resolve()


def _atomic_write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    """
    Write text to a path atomically by writing to a temp file and then replacing.
    Ensures the directory exists.
    Uses os.replace for atomicity so readers never see a partial write.
    """
    try:
        if str(path.parent):  # Avoid creating ''
            path.parent.mkdir(parents=True, exist_ok=True)
            # write to a temp file in same directory then replace
            with NamedTemporaryFile(
                    "w",
                    encoding=encoding,
                    dir=path.parent,
                    delete=False,
                    suffix=".tmp") as tf:
                tf.write(text)
                temp_name = tf.name
            os.replace(temp_name, path)
    except Exception as e:
        raise FileAccessError(
            f"Could not atomically write data to file '{path}'.\nError: {e}"
        ) from e


def _atomic_copy_file(src: Path, dest: Path) -> None:
    """
    Copy a file into dest atomically by copying to a temp file and then replacing.

    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    # create temp file name in destination dir
    with NamedTemporaryFile("wb", dir=dest.parent, delete=False, suffix=".tmp") as tf:
        temp_name = tf.name
    try:
        shutil.copyfile(src, temp_name)
        os.replace(temp_name, dest)
    except Exception as orig_e:
        # best-effort cleanup
        try:
            if os.path.exists(temp_name):
                os.remove(temp_name)
        except Exception as e:
            raise FileAccessError(
                f"Error while copying '{src}' (default of a file) "
                f"to '{dest}'. Could not remove temporary file because of {e}!\n"
                f"Original error: {orig_e}"
            ) from orig_e
        raise FileAccessError(
            f"Error while copying '{src}' (default of a file) to '{dest}'.\n"
            f"Error: {orig_e}"
        ) from orig_e


class FileAccessError(Exception):
    """Raised when the file cannot be accessed due to permissions or IO errors."""


class DefaultNotJSONSerializableError(Exception):
    """Raised when the provided default data is not JSON-serializable."""


class JSONDeserializationError(Exception):
    """Raised when JSON data loaded from a file cannot be deserialized."""


class JSONFile:
    """
    A .json file on the disk.
    """

    __path: Path  # Full absolute path
    json: Any
    """Python representation of the JSON data."""
    __default_data: JSONSerializable | None = None
    #: If not None, default data to use when the file at path is missing or corrupted
    __default_path: PathOrSimilar | None = None
    #: If not None, path to JSON file to use as default data
    settings: JsonSerializationSettings
    """Serialization settings of this instance"""
    __auto_save: bool

    def __init__(
            self,
            path: PathOrSimilar,
            default_data: JSONSerializable = None,
            default_path: PathOrSimilar | None = None,
            *,
            settings: JsonSerializationSettings | None = None,
            auto_save: bool = True,
            strict: bool = True,
            load_file: bool = True
    ) -> None:
        """
        Create a new JSONFile instance and load data from disk
        Specify defaults preferably with default_data or default_path.

        :param path: path to file (str or PathLike)
        :param default_data:
            Default data to use if file at path is nonexistent or
            corrupted. Keep in mind that None is serializable as JSON "null" - will
            not throw an error if not specified.
        :param default_path:
            **Overrides** default_data if provided.
            Path to a JSON file to use as default data.
        :param settings: JsonSerializationSettings object
        :param auto_save: if True, context manager will save on exit
        :param strict:
            if True, will throw error if file cannot be read or
            if default_data is not JSON-serializable
        :param load_file:
            True by default, causes file to be loaded on init.
            Set to False to suppress loading.
        :raises ~singlejson.fileutils.FileAccessError:
            if file cannot be accessed (always)
        :raises ~singlejson.fileutils.JSONDeserializationError:
            if strict is True and an error occurs during loading
        :raises ~singlejson.fileutils.DefaultNotJSONSerializableError:
            if strict is True and default_data is not JSON-serializable
        """
        self.__path = abs_filename(path)
        self.settings = settings or DEFAULT_SERIALIZATION_SETTINGS
        self.__auto_save = auto_save
        # Per-instance reentrant lock to make file operations thread-safe
        self._lock = threading.RLock()

        if default_path:
            if strict:
                # Ensure default file can be loaded with json.loads
                path = Path(default_path)
                if path.exists():
                    # Load from file
                    try:
                        with path.open("r", encoding=self.settings.encoding) as file:
                            json_load(file)
                            # If this works without errors, fine!
                    except (PermissionError, OSError) as e:
                        raise FileAccessError(
                            f"Cannot access default JSON file '{path}': {e}") from e
                    except Exception as e:
                        raise DefaultNotJSONSerializableError(
                            f"Cannot load default JSON from file '{path}': {e}"
                        ) from e
                else:
                    raise DefaultNotJSONSerializableError(
                        f"Default JSON file '{path}' does not exist.")
            # Wether checked or not, use default_path default initialization method.
            self.__default_path = default_path

        else:
            # Default data and no default_path
            if strict:
                try:
                    dumps(default_data,
                          indent=self.settings.indent,
                          sort_keys=self.settings.sort_keys,
                          ensure_ascii=self.settings.ensure_ascii)
                    # If this works without errors, fine!
                except (TypeError, ValueError, json.JSONDecodeError) as e:
                    raise DefaultNotJSONSerializableError(
                        f"default_data for '{self.__path}' isn't JSON-serializable: {e}"
                    ) from e
            # No matter the validity, set default data.
            self.__default_data = deepcopy(default_data)

        # Load from disk (this will create the file if needed and apply defaults)
        if load_file:
            self.reload(recover=strict)
        else:
            self.json = None

    def __reinstantiate_default(self, recover: bool) -> None:
        """
        Revert the file to the default.

        :param recover:
            If True, recover when an error occurs during default loading.
            Otherwise will throw DefaultNotJSONSerializableError.

        :return:
        """
        with self._lock:
            if self.__default_path:
                default_path = Path(self.__default_path)
                if default_path.exists():
                    # Valid default file, copy
                    _atomic_copy_file(default_path, self.__path)
                else:
                    # Default file does not exist, create empty file
                    if not recover:
                        raise DefaultNotJSONSerializableError(
                            f"Default JSON file '{default_path}' does not exist!"
                        )
                    _atomic_write_text(self.__path,
                                       "{}",
                                       encoding=self.settings.encoding)
            else:
                # Default is dict, write it to file and then open it.
                # No need to deepcopy again as default is
                # saved to file and then re-constructed
                try:
                    text = dumps(self.__default_data,
                                 indent=self.settings.indent,
                                 sort_keys=self.settings.sort_keys,
                                 ensure_ascii=self.settings.ensure_ascii)
                    _atomic_write_text(self.__path, text,
                                       encoding=self.settings.encoding)
                except (TypeError, ValueError, json.JSONDecodeError) as e:
                    if not recover:
                        raise DefaultNotJSONSerializableError(
                            f"Default for file '{self.__path}' is not serializable!"
                            f"\nError: {e}"
                        ) from e
                    _atomic_write_text(self.__path, "{}",
                                       encoding=self.settings.encoding)
                # Continue to load file as normal

    @property
    def path(self) -> Path:
        """
        Return the absolute path of the file.

        :return: absolute path
        """
        return self.__path

    def reload(self, *, recover: bool = True) -> None:
        """
        Reload from disk, recovering to default on invalid JSON.
        Always raises FileAccessError on permission issues.

        :param recover:
            If True, recover when an error occurs during default loading.
            If False {} will be used if default loading fails.
        :type recover: bool

        :raises ~singlejson.fileutils.FileAccessError:
            if file cannot be accessed (always)
        :raises ~singlejson.fileutils.DefaultNotJSONSerializableError:
            if recover is False and JSON is invalid
        """
        # Use the per-instance lock to guard load/recovery operations
        with self._lock:
            # 1: See if file exists
            if not self.__path.exists():
                # Create file with no data
                self.__reinstantiate_default(recover)
            # 2: File now surely exists
            try:
                with self.__path.open("r", encoding=self.settings.encoding) as file:
                    self.json = json_load(file)
            except (PermissionError, OSError) as e:
                raise FileAccessError(
                    f"Cannot read file '{self.__path}': {e}"
                ) from e
            except json.JSONDecodeError as e:
                # Loading failed. Recover to default if allowed.
                if not recover:
                    # If a default_path is configured,
                    # the error likely came from copying an invalid default file.
                    if self.__default_path:
                        raise DefaultNotJSONSerializableError(
                            f"Default JSON file '{self.__default_path}' "
                            f"is not valid JSON: {e}"
                        ) from e
                    raise JSONDeserializationError(
                        f"Cannot read json from file '{self.__path}': {e}"
                    ) from e
                logger.warning(
                    "Cannot read json from file '%s'. Using default!\n"
                    "Decoding error: %s",
                    self.__path, e)
                self.__reinstantiate_default(recover)
                # Try loading again (single safe retry to avoid infinite recursion)
                try:
                    with self.__path.open("r", encoding=self.settings.encoding) as file:
                        self.json = json_load(file)
                except json.JSONDecodeError as e2:
                    if not recover:
                        if self.__default_path:
                            raise DefaultNotJSONSerializableError(
                                f"Default JSON file '{self.__default_path}' "
                                f"is not valid JSON on retry: {e2}"
                            ) from e2
                        raise JSONDeserializationError(
                            f"Cannot read json from file '{self.__path}' on retry: {e2}"
                        ) from e2
                    # fallback to empty dict if recovery still fails
                    logger.warning(
                        "Recovery also failed for '%s'. Falling back to empty object.",
                        self.__path)
                    _atomic_write_text(self.__path, "{}",
                                       encoding=self.settings.encoding)
                    self.json = {}

    def save(self, settings: JsonSerializationSettings | None = None) -> None:
        """
        Save the data to the disk (atomically by default).

        :param settings:
            :class:`JsonSerializationSettings` object
            (``None`` for instance settings)
        """
        settings = settings or self.settings
        # guard save with the per-instance lock
        with self._lock:
            try:
                # Ensure directory exists
                self.__path.parent.mkdir(parents=True, exist_ok=True)
                # Serialize to text then atomically write
                data_to_save = self.json
                text = dumps(data_to_save,
                             indent=settings.indent,
                             sort_keys=settings.sort_keys,
                             ensure_ascii=settings.ensure_ascii)
                _atomic_write_text(self.__path, text, encoding=self.settings.encoding)
            except (PermissionError, OSError) as e:
                raise FileAccessError(f"Cannot write file '{self.__path}': {e}") from e

    def save_atomic(self, tmp_suffix: str = ".tmp") -> None:
        """
        Deprecated alias for `save()` — saves atomically by default.
        """
        warnings.warn(
            "JSONFile.save_atomic is deprecated; use JSONFile.save() "
            "which is atomic by default",
            DeprecationWarning,
            stacklevel=2)
        # delegate to new save implementation
        return self.save()

    # Context manager support
    def __enter__(self) -> JSONFile:
        """
        Enter the context manager.

        :return: self
        """
        return self

    def __exit__(self,
                 exc_type: type[BaseException] | None,
                 exc: BaseException | None,
                 tb: TracebackType | None,
                 ) -> None:
        """
        Exit the context manager and save if auto_save is True
        and no exception occurred.

        :param exc_type: exception type
        :param exc: exception instance
        :param tb: traceback
        """
        if exc_type is None and self.__auto_save:
            self.save()


# Default settings instance used by JSONFile.save() when not provided
DEFAULT_SERIALIZATION_SETTINGS = JsonSerializationSettings()
"""Default JsonSerializationSettings used by JSONFile instances 
with indent=4, sort_keys=True, ensure_ascii=False"""
