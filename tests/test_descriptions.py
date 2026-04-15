import pytest

from pyreo.descriptions import load_descriptions, DescriptionEntry


class TestLoadDescriptions:
    def test_loads_keyword_descriptions(self, keywords_dir):
        descs = load_descriptions(keywords_dir / "mi.descriptions.json")
        entry = descs["mena"]
        assert entry.python == "if"
        assert entry.category == "control"
        assert "true" in entry.description.lower()

    def test_loads_builtin_descriptions(self, keywords_dir):
        descs = load_descriptions(keywords_dir / "mi.descriptions.json")
        entry = descs["tā"]
        assert entry.python == "print"
        assert entry.category == "function"

    def test_all_mi_json_keywords_have_descriptions(self, keywords_dir):
        from pyreo.dictionary import load_dictionary
        dictionary = load_dictionary(keywords_dir / "mi.json")
        descs = load_descriptions(keywords_dir / "mi.descriptions.json")
        for maori in dictionary.keywords:
            assert maori in descs, f"Missing description for keyword: {maori}"
        for maori in dictionary.builtins:
            assert maori in descs, f"Missing description for builtin: {maori}"

    def test_raises_on_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_descriptions(tmp_path / "nonexistent.json")

    def test_description_entry_has_detail_string(self, keywords_dir):
        descs = load_descriptions(keywords_dir / "mi.descriptions.json")
        entry = descs["mena"]
        assert entry.detail == "mena → if"

    def test_description_entry_has_markdown_docs(self, keywords_dir):
        descs = load_descriptions(keywords_dir / "mi.descriptions.json")
        entry = descs["tā"]
        assert "print" in entry.documentation
        assert "Show" in entry.documentation
