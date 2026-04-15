from pathlib import Path

import pytest

from pyreo.server import build_completion_items, build_hover_response


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


class TestHover:
    def test_returns_hover_for_known_keyword(self, descriptions):
        result = build_hover_response("mena", descriptions)
        assert result is not None
        assert "if" in result.contents.value

    def test_returns_hover_for_known_builtin(self, descriptions):
        result = build_hover_response("tā", descriptions)
        assert result is not None
        assert "print" in result.contents.value
        assert "Show" in result.contents.value

    def test_returns_none_for_unknown_word(self, descriptions):
        result = build_hover_response("unknown_variable", descriptions)
        assert result is None

    def test_returns_none_for_empty_word(self, descriptions):
        result = build_hover_response("", descriptions)
        assert result is None
