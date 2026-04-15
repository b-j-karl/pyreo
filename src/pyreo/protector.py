from __future__ import annotations

import re

# Matches (in order): triple-quoted strings, single-quoted strings, comments
# Triple-quoted must come first to avoid matching the opening """ as an empty string
_TOKEN_PATTERN = re.compile(
    r'(?P<triple>"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')'
    r"|(?P<string>f?\"(?:[^\"\\]|\\.)*\"|f?'(?:[^'\\]|\\.)*')"
    r"|(?P<comment>\#[^\n]*)",
    re.DOTALL,
)

_PLACEHOLDER_PREFIX = "__PYREO_"
_PLACEHOLDER_SUFFIX = "__"


def protect(source: str) -> tuple[str, dict[str, str]]:
    """Replace string literals and comments with placeholders.

    Returns the protected source and a dict mapping placeholders to originals.
    """
    tokens: dict[str, str] = {}
    counter = 0

    def _replace(match: re.Match) -> str:
        nonlocal counter
        placeholder = f"{_PLACEHOLDER_PREFIX}{counter}{_PLACEHOLDER_SUFFIX}"
        tokens[placeholder] = match.group(0)
        counter += 1
        return placeholder

    protected = _TOKEN_PATTERN.sub(_replace, source)
    return protected, tokens


def restore(source: str, tokens: dict[str, str]) -> str:
    """Replace placeholders back with original strings and comments."""
    result = source
    for placeholder, original in tokens.items():
        result = result.replace(placeholder, original)
    return result
