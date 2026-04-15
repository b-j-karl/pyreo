import json
from pathlib import Path

import pytest

from pyreo.dictionary import load_dictionary, DictionaryError


class TestLoadDictionary:
    def test_loads_valid_dictionary(self, keywords_dir):
        d = load_dictionary(keywords_dir / "mi.json")
        assert d.keywords["mena"] == "if"
        assert d.builtins["tā"] == "print"

    def test_returns_all_python_keywords(self, keywords_dir):
        d = load_dictionary(keywords_dir / "mi.json")
        required = {"if", "else", "for", "while", "def", "return", "class", "import"}
        mapped_values = set(d.keywords.values())
        assert required.issubset(mapped_values)

    def test_returns_all_mappings_longest_first(self, keywords_dir):
        d = load_dictionary(keywords_dir / "mi.json")
        all_mappings = d.all_mappings()
        keys = list(all_mappings.keys())
        for i in range(len(keys) - 1):
            assert len(keys[i]) >= len(keys[i + 1])

    def test_raises_on_missing_file(self, tmp_path):
        with pytest.raises(DictionaryError, match="not found"):
            load_dictionary(tmp_path / "nonexistent.json")

    def test_raises_on_invalid_json(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not json")
        with pytest.raises(DictionaryError, match="invalid"):
            load_dictionary(bad_file)

    def test_raises_on_missing_keywords_section(self, tmp_path):
        incomplete = tmp_path / "incomplete.json"
        incomplete.write_text(json.dumps({"builtins": {}}))
        with pytest.raises(DictionaryError, match="keywords"):
            load_dictionary(incomplete)

    def test_meta_is_accessible(self, keywords_dir):
        d = load_dictionary(keywords_dir / "mi.json")
        assert d.meta["language_code"] == "mi"
