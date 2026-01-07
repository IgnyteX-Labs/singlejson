import warnings
from pathlib import Path

from singlejson.fileutils import JSONFile

def test_save_atomic_is_alias_and_warns(tmp_path: Path):
    p = tmp_path / "alias.json"
    jf = JSONFile(p, default_data={})
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        jf.save_atomic()
        assert any(issubclass(x.category, DeprecationWarning) for x in w)
