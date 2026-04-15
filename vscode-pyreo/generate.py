"""Generate VS Code grammar and language config from keywords/mi.json.

Run from the pyreo project root:
    uv run python vscode-pyreo/generate.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
KEYWORDS_FILE = PROJECT_ROOT / "keywords" / "mi.json"
GRAMMAR_FILE = Path(__file__).parent / "syntaxes" / "pyreo.tmLanguage.json"
LANG_CONFIG_FILE = Path(__file__).parent / "language-configuration.json"

# Categorise Python keywords into TextMate scopes
CONTROL = {
    "if", "elif", "else", "for", "in", "while", "break", "continue",
    "pass", "try", "except", "finally", "raise", "return", "yield",
    "as", "with", "assert", "del",
}
OPERATORS = {"and", "or", "not", "is", "is not", "not in"}
IMPORTS = {"import", "from"}
STORAGE = {"def", "class", "lambda", "global", "nonlocal"}
CONSTANTS = {"True", "False", "None"}

# Builtin types vs functions
BUILTIN_TYPES = {"int", "float", "str", "list", "dict", "set", "tuple", "bool"}


def escape_for_regex(word: str) -> str:
    """Escape special regex characters in a keyword."""
    return re.escape(word)


def build_alternation(words: list[str]) -> str:
    """Build a regex alternation, longest-first to avoid partial matches."""
    sorted_words = sorted(words, key=len, reverse=True)
    escaped = [escape_for_regex(w) for w in sorted_words]
    return "|".join(escaped)


def categorise_keywords(data: dict) -> dict[str, list[str]]:
    """Sort Māori keywords into TextMate scope categories."""
    categories: dict[str, list[str]] = {
        "control": [],
        "operator": [],
        "import": [],
        "storage": [],
        "constant": [],
    }

    for maori, python in data.get("keywords", {}).items():
        if python in CONTROL:
            categories["control"].append(maori)
        elif python in OPERATORS:
            categories["operator"].append(maori)
        elif python in IMPORTS:
            categories["import"].append(maori)
        elif python in STORAGE:
            categories["storage"].append(maori)
        elif python in CONSTANTS:
            categories["constant"].append(maori)
        else:
            # Fallback: treat as control
            categories["control"].append(maori)

    return categories


def categorise_builtins(data: dict) -> dict[str, list[str]]:
    """Sort Māori builtins into types vs functions."""
    categories: dict[str, list[str]] = {
        "types": [],
        "functions": [],
    }

    for maori, python in data.get("builtins", {}).items():
        if python in BUILTIN_TYPES:
            categories["types"].append(maori)
        else:
            categories["functions"].append(maori)

    return categories


def find_maori_for(data: dict, python_keyword: str) -> str | None:
    """Find the Māori word that maps to a Python keyword."""
    for maori, python in data.get("keywords", {}).items():
        if python == python_keyword:
            return maori
    return None


def generate_grammar(data: dict) -> dict:
    """Generate the full tmLanguage JSON structure."""
    kw = categorise_keywords(data)
    bi = categorise_builtins(data)

    def_word = find_maori_for(data, "def") or "tautuhi"
    class_word = find_maori_for(data, "class") or "momo"

    # Build indent-triggering keywords (ones that precede a colon block)
    indent_triggers = []
    for python_kw in ["if", "elif", "else", "for", "while", "def", "class",
                       "try", "except", "finally", "with"]:
        maori = find_maori_for(data, python_kw)
        if maori:
            indent_triggers.append(maori)

    return {
        "$schema": "https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json",
        "name": "PyReo",
        "scopeName": "source.pyreo",
        "_generated": "This file is auto-generated from keywords/mi.json. Do not edit manually. Run: uv run python vscode-pyreo/generate.py",
        "patterns": [
            {"include": "#comments"},
            {"include": "#strings"},
            {"include": "#numbers"},
            {"include": "#keywords-control"},
            {"include": "#keywords-operator"},
            {"include": "#keywords-import"},
            {"include": "#keywords-storage"},
            {"include": "#keywords-constant"},
            {"include": "#builtins-functions"},
            {"include": "#builtins-types"},
            {"include": "#function-def"},
            {"include": "#class-def"},
            {"include": "#function-call"},
        ],
        "repository": {
            "comments": {
                "match": "#.*$",
                "name": "comment.line.number-sign.pyreo",
            },
            "strings": {
                "patterns": [
                    {
                        "name": "string.quoted.triple.double.pyreo",
                        "begin": 'f?"""',
                        "end": '"""',
                        "patterns": [
                            {"include": "#string-escapes"},
                            {"include": "#fstring-expressions"},
                        ],
                    },
                    {
                        "name": "string.quoted.triple.single.pyreo",
                        "begin": "f?'''",
                        "end": "'''",
                        "patterns": [
                            {"include": "#string-escapes"},
                            {"include": "#fstring-expressions"},
                        ],
                    },
                    {
                        "name": "string.quoted.double.pyreo",
                        "begin": 'f?"',
                        "end": '"',
                        "patterns": [
                            {"include": "#string-escapes"},
                            {"include": "#fstring-expressions"},
                        ],
                    },
                    {
                        "name": "string.quoted.single.pyreo",
                        "begin": "f?'",
                        "end": "'",
                        "patterns": [
                            {"include": "#string-escapes"},
                            {"include": "#fstring-expressions"},
                        ],
                    },
                ],
            },
            "string-escapes": {
                "match": "\\\\.",
                "name": "constant.character.escape.pyreo",
            },
            "fstring-expressions": {
                "begin": "\\{",
                "end": "\\}",
                "name": "meta.fstring.pyreo",
                "patterns": [
                    {"include": "#keywords-constant"},
                    {"include": "#builtins-functions"},
                    {"include": "#builtins-types"},
                    {"include": "#numbers"},
                ],
            },
            "numbers": {
                "patterns": [
                    {
                        "match": "\\b0[xX][0-9a-fA-F_]+\\b",
                        "name": "constant.numeric.hex.pyreo",
                    },
                    {
                        "match": "\\b0[oO][0-7_]+\\b",
                        "name": "constant.numeric.oct.pyreo",
                    },
                    {
                        "match": "\\b0[bB][01_]+\\b",
                        "name": "constant.numeric.bin.pyreo",
                    },
                    {
                        "match": "\\b[0-9][0-9_]*(\\.[0-9_]+)?([eE][+-]?[0-9_]+)?\\b",
                        "name": "constant.numeric.pyreo",
                    },
                ],
            },
            "keywords-control": {
                "match": f"\\b({build_alternation(kw['control'])})\\b",
                "name": "keyword.control.pyreo",
            },
            "keywords-operator": {
                "match": f"\\b({build_alternation(kw['operator'])})\\b",
                "name": "keyword.operator.logical.pyreo",
            },
            "keywords-import": {
                "match": f"\\b({build_alternation(kw['import'])})\\b",
                "name": "keyword.control.import.pyreo",
            },
            "keywords-storage": {
                "match": f"\\b({build_alternation(kw['storage'])})\\b",
                "name": "storage.type.pyreo",
            },
            "keywords-constant": {
                "match": f"\\b({build_alternation(kw['constant'])})\\b",
                "name": "constant.language.pyreo",
            },
            "builtins-functions": {
                "match": f"\\b({build_alternation(bi['functions'])})\\b",
                "name": "support.function.builtin.pyreo",
            },
            "builtins-types": {
                "match": f"\\b({build_alternation(bi['types'])})\\b",
                "name": "support.type.pyreo",
            },
            "function-def": {
                "match": f"\\b({escape_for_regex(def_word)})\\s+([\\w\\u0100-\\u017F]+)\\s*\\(",
                "captures": {
                    "1": {"name": "storage.type.function.pyreo"},
                    "2": {"name": "entity.name.function.pyreo"},
                },
            },
            "class-def": {
                "match": f"\\b({escape_for_regex(class_word)})\\s+([\\w\\u0100-\\u017F]+)",
                "captures": {
                    "1": {"name": "storage.type.class.pyreo"},
                    "2": {"name": "entity.name.type.class.pyreo"},
                },
            },
            "function-call": {
                "match": "\\b([\\w\\u0100-\\u017F]+)\\s*(?=\\()",
                "name": "meta.function-call.pyreo",
                "captures": {
                    "1": {"name": "entity.name.function.pyreo"},
                },
            },
        },
    }


def generate_language_config(data: dict) -> dict:
    """Generate the language-configuration.json."""
    indent_keywords = []
    for python_kw in ["if", "elif", "else", "for", "while", "def", "class",
                       "try", "except", "finally", "with"]:
        maori = find_maori_for(data, python_kw)
        if maori:
            indent_keywords.append(escape_for_regex(maori))

    dedent_keywords = []
    for python_kw in ["elif", "else", "except", "finally"]:
        maori = find_maori_for(data, python_kw)
        if maori:
            dedent_keywords.append(escape_for_regex(maori))

    return {
        "comments": {"lineComment": "#"},
        "brackets": [
            ["{", "}"],
            ["[", "]"],
            ["(", ")"],
        ],
        "autoClosingPairs": [
            {"open": "{", "close": "}"},
            {"open": "[", "close": "]"},
            {"open": "(", "close": ")"},
            {"open": '"', "close": '"', "notIn": ["string"]},
            {"open": "'", "close": "'", "notIn": ["string"]},
        ],
        "surroundingPairs": [
            {"open": "{", "close": "}"},
            {"open": "[", "close": "]"},
            {"open": "(", "close": ")"},
            {"open": '"', "close": '"'},
            {"open": "'", "close": "'"},
        ],
        "indentationRules": {
            "increaseIndentPattern": f"^\\s*({"|".join(indent_keywords)})\\b.*:\\s*$",
            "decreaseIndentPattern": f"^\\s*({"|".join(dedent_keywords)})\\b",
        },
        "folding": {"offSide": True},
    }


def main():
    import sys
    sys.stdout.reconfigure(encoding="utf-8")

    data = json.loads(KEYWORDS_FILE.read_text(encoding="utf-8"))

    grammar = generate_grammar(data)
    GRAMMAR_FILE.write_text(
        json.dumps(grammar, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Generated {GRAMMAR_FILE}")

    lang_config = generate_language_config(data)
    LANG_CONFIG_FILE.write_text(
        json.dumps(lang_config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Generated {LANG_CONFIG_FILE}")

    # Summary
    kw = categorise_keywords(data)
    bi = categorise_builtins(data)
    total = sum(len(v) for v in kw.values()) + sum(len(v) for v in bi.values())
    print(f"\n{total} keywords/builtins mapped from {KEYWORDS_FILE.name}:")
    for name, words in [*kw.items(), *bi.items()]:
        print(f"  {name}: {len(words)} ({', '.join(words[:5])}{'...' if len(words) > 5 else ''})")


if __name__ == "__main__":
    main()
