import json
import warnings
from pathlib import Path

from singlejson.fileutils import JSONFile


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


def test_save_atomic_is_alias_and_warns(tmp_path: Path):
    p = tmp_path / "alias.json"
    jf = JSONFile(p, default_data={})
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        jf.save_atomic()
        assert any(issubclass(x.category, DeprecationWarning) for x in w)
