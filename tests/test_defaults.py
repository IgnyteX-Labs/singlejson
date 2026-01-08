import json
from pathlib import Path

from singlejson.fileutils import JSONFile


def test_default_data_is_deepcopied(tmp_path: Path):
    path = tmp_path / "test.json"

    # Original mutable data
    default_data = {"nested": {"key": "value"}, "list": [1, 2, 3]}

    # Initialize JSONFile. Since file doesn't exist, it will use default_data
    jf = JSONFile(path, default_data=default_data)

    # Verify initial state
    assert jf.json == default_data
    assert jf.json is not default_data
    assert jf.json["nested"] is not default_data["nested"]
    assert jf.json["list"] is not default_data["list"]

    # Mutate original default_data
    default_data["nested"]["key"] = "changed"
    default_data["list"].append(4)

    # JSONFile's data should remain unchanged
    assert jf.json["nested"]["key"] == "value"
    assert jf.json["list"] == [1, 2, 3]

    # Even if we reload (it should still be the same on disk)
    jf.reload()
    assert jf.json["nested"]["key"] == "value"
    assert jf.json["list"] == [1, 2, 3]


def test_default_data_reinstantiation_is_consistent(tmp_path: Path):
    path = tmp_path / "test_reinstantiate.json"

    default_data = {"a": [1]}
    jf = JSONFile(path, default_data=default_data)

    # Delete file and reload to force reinstantiation from stored __default_data
    path.unlink()
    jf.reload()

    assert jf.json == {"a": [1]}

    # Mutate jf.json and then reload after unlinking again
    jf.json["a"].append(2)
    path.unlink()
    jf.reload()

    # Should still be the original default, not the mutated one
    assert jf.json == {"a": [1]}


def test_default_file_is_copied(tmp_path: Path):
    template = tmp_path / "template.json"
    content = {"hello": "world", "num": 5}
    with template.open("w", encoding="utf-8") as f:
        json.dump(content, f)

    dest = tmp_path / "dest.json"
    jf = JSONFile(dest, default_path=str(template))

    assert dest.exists()
    with dest.open("r", encoding="utf-8") as f:
        d = json.load(f)
    assert d == content
    assert jf.json == content
