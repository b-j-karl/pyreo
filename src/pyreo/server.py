from __future__ import annotations

import re
import sys
from pathlib import Path

from lsprotocol import types
from pygls.lsp.server import LanguageServer

from pyreo.descriptions import DescriptionEntry, load_descriptions
from pyreo.dictionary import load_dictionary, Dictionary
from pyreo.translator import translate

# Category → CompletionItemKind mapping
_KIND_MAP = {
    "control": types.CompletionItemKind.Keyword,
    "operator": types.CompletionItemKind.Operator,
    "import": types.CompletionItemKind.Keyword,
    "storage": types.CompletionItemKind.Keyword,
    "constant": types.CompletionItemKind.Constant,
    "function": types.CompletionItemKind.Function,
    "type": types.CompletionItemKind.Class,
}


def build_completion_items(
    descriptions: dict[str, DescriptionEntry],
) -> list[types.CompletionItem]:
    items = []
    for maori, entry in descriptions.items():
        items.append(
            types.CompletionItem(
                label=maori,
                detail=entry.detail,
                documentation=types.MarkupContent(
                    kind=types.MarkupKind.Markdown,
                    value=entry.documentation,
                ),
                kind=_KIND_MAP.get(entry.category, types.CompletionItemKind.Text),
                insert_text=maori,
            )
        )
    return items


def _find_keywords_dir() -> Path:
    candidates = [
        Path.cwd() / "keywords",
        Path(__file__).parent.parent.parent / "keywords",
    ]
    for p in candidates:
        if (p / "mi.json").exists():
            return p
    raise FileNotFoundError("Cannot find keywords/ directory")


def create_server() -> tuple[LanguageServer, Dictionary, dict[str, DescriptionEntry]]:
    server = LanguageServer("pyreo-lsp", "v0.1.0")

    keywords_dir = _find_keywords_dir()
    descriptions = load_descriptions(keywords_dir / "mi.descriptions.json")
    dictionary = load_dictionary(keywords_dir / "mi.json")
    completion_items = build_completion_items(descriptions)

    @server.feature(types.TEXT_DOCUMENT_COMPLETION)
    def completions(params: types.CompletionParams):
        return types.CompletionList(is_incomplete=False, items=completion_items)

    return server, dictionary, descriptions


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    server, _, _ = create_server()
    server.start_io()


if __name__ == "__main__":
    main()
