from __future__ import annotations

import re
import sys
from pathlib import Path

from lsprotocol import types
from pygls.lsp.server import LanguageServer

from pyreo.descriptions import DescriptionEntry, load_descriptions
from pyreo.dictionary import load_dictionary, Dictionary
from pyreo.keywords import find_keywords_file
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


def _word_at_position(line: str, character: int) -> str:
    """Extract the word at the given character position in a line."""
    pattern = re.compile(r'[\w\u0100-\u017F]+')
    for match in pattern.finditer(line):
        if match.start() <= character <= match.end():
            return match.group()
    return ""


def build_hover_response(
    word: str,
    descriptions: dict[str, DescriptionEntry],
) -> types.Hover | None:
    if not word or word not in descriptions:
        return None
    entry = descriptions[word]
    return types.Hover(
        contents=types.MarkupContent(
            kind=types.MarkupKind.Markdown,
            value=entry.documentation,
        )
    )


def get_diagnostics(
    source: str,
    dictionary: Dictionary,
) -> list[types.Diagnostic]:
    try:
        python_code = translate(source, dictionary)
        compile(python_code, "<pyreo>", "exec")
        return []
    except SyntaxError as e:
        line = max((e.lineno or 1) - 1, 0)
        col = max((e.offset or 1) - 1, 0)
        return [
            types.Diagnostic(
                range=types.Range(
                    start=types.Position(line=line, character=col),
                    end=types.Position(line=line, character=col + 1),
                ),
                severity=types.DiagnosticSeverity.Error,
                source="pyreo",
                message=f"SyntaxError: {e.msg}",
            )
        ]
    except Exception as e:
        return [
            types.Diagnostic(
                range=types.Range(
                    start=types.Position(line=0, character=0),
                    end=types.Position(line=0, character=1),
                ),
                severity=types.DiagnosticSeverity.Error,
                source="pyreo",
                message=str(e),
            )
        ]


def _find_keywords_dir() -> Path:
    return find_keywords_file("mi.json").parent


def create_server(keywords_dir: Path | None = None) -> tuple[LanguageServer, Dictionary, dict[str, DescriptionEntry]]:
    server = LanguageServer("pyreo-lsp", "v0.1.0")

    if keywords_dir is None:
        keywords_dir = _find_keywords_dir()
    descriptions = load_descriptions(keywords_dir / "mi.descriptions.json")
    dictionary = load_dictionary(keywords_dir / "mi.json")
    completion_items = build_completion_items(descriptions)

    @server.feature(types.TEXT_DOCUMENT_COMPLETION)
    def completions(params: types.CompletionParams):
        return types.CompletionList(is_incomplete=False, items=completion_items)

    @server.feature(types.TEXT_DOCUMENT_HOVER)
    def hover(params: types.HoverParams):
        doc = server.workspace.get_text_document(params.text_document.uri)
        line = doc.lines[params.position.line]
        word = _word_at_position(line, params.position.character)
        return build_hover_response(word, descriptions)

    @server.feature(types.TEXT_DOCUMENT_DID_OPEN)
    def did_open(params: types.DidOpenTextDocumentParams):
        doc = server.workspace.get_text_document(params.text_document.uri)
        diags = get_diagnostics(doc.source, dictionary)
        server.publish_diagnostics(params.text_document.uri, diags)

    @server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
    def did_change(params: types.DidChangeTextDocumentParams):
        doc = server.workspace.get_text_document(params.text_document.uri)
        diags = get_diagnostics(doc.source, dictionary)
        server.publish_diagnostics(params.text_document.uri, diags)

    @server.feature(types.TEXT_DOCUMENT_DID_SAVE)
    def did_save(params: types.DidSaveTextDocumentParams):
        doc = server.workspace.get_text_document(params.text_document.uri)
        diags = get_diagnostics(doc.source, dictionary)
        server.publish_diagnostics(params.text_document.uri, diags)

    return server, dictionary, descriptions


def main():
    import argparse

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser()
    parser.add_argument("--keywords", type=Path, help="Path to keywords/ directory")
    args = parser.parse_args()

    if args.keywords:
        keywords_dir = args.keywords
    else:
        keywords_dir = _find_keywords_dir()

    server, _, _ = create_server(keywords_dir)
    server.start_io()


if __name__ == "__main__":
    main()
