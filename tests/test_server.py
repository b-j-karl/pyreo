from pathlib import Path

import pytest

from pyreo.server import build_completion_items


@pytest.fixture
def descriptions(keywords_dir):
    from pyreo.descriptions import load_descriptions
    return load_descriptions(keywords_dir / "mi.descriptions.json")


@pytest.fixture
def dictionary(keywords_dir):
    from pyreo.dictionary import load_dictionary
    return load_dictionary(keywords_dir / "mi.json")


class TestCompletions:
    def test_returns_all_keywords_and_builtins(self, descriptions):
        items = build_completion_items(descriptions)
        labels = {item.label for item in items}
        assert "mena" in labels
        assert "tā" in labels
        assert "tautuhi" in labels

    def test_keyword_items_have_detail(self, descriptions):
        items = build_completion_items(descriptions)
        mena = next(i for i in items if i.label == "mena")
        assert mena.detail == "mena → if"

    def test_keyword_items_have_documentation(self, descriptions):
        items = build_completion_items(descriptions)
        mena = next(i for i in items if i.label == "mena")
        assert "if" in mena.documentation.value

    def test_keywords_are_keyword_kind(self, descriptions):
        from lsprotocol.types import CompletionItemKind
        items = build_completion_items(descriptions)
        mena = next(i for i in items if i.label == "mena")
        assert mena.kind == CompletionItemKind.Keyword

    def test_builtins_are_function_kind(self, descriptions):
        from lsprotocol.types import CompletionItemKind
        items = build_completion_items(descriptions)
        ta = next(i for i in items if i.label == "tā")
        assert ta.kind == CompletionItemKind.Function

    def test_type_builtins_are_class_kind(self, descriptions):
        from lsprotocol.types import CompletionItemKind
        items = build_completion_items(descriptions)
        tau = next(i for i in items if i.label == "tau")
        assert tau.kind == CompletionItemKind.Class
