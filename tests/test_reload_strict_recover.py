import json
from pathlib import Path

import pytest

from singlejson.fileutils import (
    DefaultNotJSONSerializableError,
    JSONDeserializationError,
    JSONFile,
)


def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_reload_invalid_json_recover_true_recovers_to_default(tmp_path):
    p = tmp_path / "bad.json"
    write_text(p, "{ invalid json")
    jf = JSONFile(p, default_data={"ok": True}, load_file=False)
    jf.reload(recover=True)
    assert jf.json == {"ok": True}
    assert read_json(p) == {"ok": True}


def test_reload_invalid_json_recover_false_raises_JSONDeserializationError(tmp_path):
    p = tmp_path / "bad.json"
    write_text(p, "{ invalid json")
    jf = JSONFile(p, default_data={"ok": True}, load_file=False)
    with pytest.raises(JSONDeserializationError):
        jf.reload(recover=False)


def test_missing_file_init_creates_default_data(tmp_path):
    p = tmp_path / "missing.json"
    jf = JSONFile(p, default_data={"a": 1})
    assert p.exists()
    assert jf.json == {"a": 1}


def test_reload_on_missing_file_writes_default_data_regardless_recover(tmp_path):
    p = tmp_path / "missing2.json"
    jf = JSONFile(p, default_data={"x": 2}, load_file=False)
    jf.reload(recover=True)
    assert jf.json == {"x": 2}

    # remove file and try with recover=False
    p.unlink()
    jf2 = JSONFile(p, default_data={"y": 3}, load_file=False)
    jf2.reload(recover=False)
    assert jf2.json == {"y": 3}


def test_default_path_missing_strict_true_raises_on_init(tmp_path):
    p = tmp_path / "target.json"
    default_path = tmp_path / "nope.json"
    with pytest.raises(DefaultNotJSONSerializableError):
        JSONFile(p, default_path=default_path, strict=True)


def test_default_path_missing_strict_false_reload_behaviour(tmp_path):
    p = tmp_path / "target2.json"
    default_path = tmp_path / "nope2.json"
    jf = JSONFile(p, default_path=default_path, strict=False, load_file=False)
    # recover=True should create a file (empty dict)
    jf.reload(recover=True)
    assert jf.json == {}

    # Now when recover=False, reinstantiate_default should raise DefaultNotJSONSerializableError
    # remove the file so reload will attempt to reinstantiate the default_path (which is missing)
    p.unlink()
    jf2 = JSONFile(p, default_path=default_path, strict=False, load_file=False)
    with pytest.raises(DefaultNotJSONSerializableError):
        jf2.reload(recover=False)


def test_default_path_pointing_to_invalid_json_strict_true_raises_on_init(tmp_path):
    p = tmp_path / "target3.json"
    defp = tmp_path / "def_invalid.json"
    write_text(defp, "{ not valid }")
    with pytest.raises(DefaultNotJSONSerializableError):
        JSONFile(p, default_path=defp, strict=True)


def test_default_path_pointing_to_invalid_json_strict_false_reload_handles_recovery(tmp_path):
    p = tmp_path / "target4.json"
    defp = tmp_path / "def_invalid2.json"
    write_text(defp, "{ not valid }")
    jf = JSONFile(p, default_path=defp, strict=False, load_file=False)
    # recover=True should not infinite loop; expect fallback to {}
    jf.reload(recover=True)
    assert jf.json == {}

    # recover=False should raise DefaultNotJSONSerializableError when trying to reinstantiate
    # remove file so reload will try to reinstantiate from the invalid default_path
    p.unlink()
    jf2 = JSONFile(p, default_path=defp, strict=False, load_file=False)
    with pytest.raises(DefaultNotJSONSerializableError):
        jf2.reload(recover=False)


def test_default_data_non_serializable_strict_true_raises_DefaultNotJSONSerializableError(tmp_path):
    p = tmp_path / "target5.json"
    non_serializable = {"x": set([1])}
    with pytest.raises(DefaultNotJSONSerializableError):
        JSONFile(p, default_data=non_serializable, strict=True, load_file=False)


def test_default_data_non_serializable_reload_recover_behavior(tmp_path):
    p = tmp_path / "target6.json"
    non_serializable = {"x": set([1])}
    jf = JSONFile(p, default_data=non_serializable, strict=False, load_file=False)
    # recover=True should fallback to {}
    jf.reload(recover=True)
    assert jf.json == {}

    # recover=False should raise DefaultNotJSONSerializableError when trying to
    # reinstantiate remove file so reload will try to write the non-serializable
    # default and raise
    p.unlink()
    jf2 = JSONFile(p, default_data=non_serializable, strict=False, load_file=False)
    with pytest.raises(DefaultNotJSONSerializableError):
        jf2.reload(recover=False)
