from __future__ import annotations

import re

# Matches (in order): triple-quoted strings, f-strings, plain strings, comments.
# Triple-quoted must come first to avoid matching the opening """ as an empty string.
# F-strings must come before plain strings so the f prefix is captured.
_TOKEN_PATTERN = re.compile(
    r'(?P<triple>[fF]?"""[\s\S]*?"""|[fF]?\'\'\'[\s\S]*?\'\'\')'
    r"|(?P<fstring>[fF]\"(?:[^\"\\]|\\.)*\"|[fF]'(?:[^'\\]|\\.)*')"
    r"|(?P<string>\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*')"
    r"|(?P<comment>\#[^\n]*)",
    re.DOTALL,
)

_PLACEHOLDER_PREFIX = "__PYREO_"
_PLACEHOLDER_SUFFIX = "__"


def _protect_fstring_parts(
    fstring: str,
    next_placeholder: callable,
) -> str:
    """Protect literal segments of an f-string, leaving expressions exposed."""
    prefix = fstring[0]  # 'f' or 'F'
    quote_char = fstring[1]
    content = fstring[2:-1]  # between quotes

    parts: list[str] = []
    literal: list[str] = []
    i = 0

    while i < len(content):
        ch = content[i]

        if ch == "{" and i + 1 < len(content) and content[i + 1] == "{":
            literal.append("{{")
            i += 2
        elif ch == "}" and i + 1 < len(content) and content[i + 1] == "}":
            literal.append("}}")
            i += 2
        elif ch == "{":
            # Flush accumulated literal text as a placeholder.
            if literal:
                parts.append(next_placeholder("".join(literal)))
                literal = []
            # Collect the full expression including its braces.
            depth = 1
            expr: list[str] = ["{"]
            i += 1
            while i < len(content) and depth > 0:
                ch = content[i]
                expr.append(ch)
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                elif ch in ('"', "'"):
                    quote = ch
                    i += 1
                    while i < len(content):
                        expr.append(content[i])
                        if content[i] == "\\" and i + 1 < len(content):
                            i += 1
                            expr.append(content[i])
                        elif content[i] == quote:
                            break
                        i += 1
                i += 1
            parts.append("".join(expr))
        else:
            literal.append(ch)
            i += 1

    if literal:
        parts.append(next_placeholder("".join(literal)))

    return f'{prefix}{quote_char}{"".join(parts)}{quote_char}'


def protect(source: str) -> tuple[str, dict[str, str]]:
    """Replace string literals and comments with placeholders.

    Returns the protected source and a dict mapping placeholders to originals.
    F-string expressions are left exposed so the translator can process them.
    """
    tokens: dict[str, str] = {}
    counter = 0

    def _next_placeholder(original: str) -> str:
        nonlocal counter
        placeholder = f"{_PLACEHOLDER_PREFIX}{counter}{_PLACEHOLDER_SUFFIX}"
        tokens[placeholder] = original
        counter += 1
        return placeholder

    def _replace(match: re.Match) -> str:
        text = match.group(0)

        if match.group("fstring"):
            return _protect_fstring_parts(text, _next_placeholder)

        return _next_placeholder(text)

    protected = _TOKEN_PATTERN.sub(_replace, source)
    return protected, tokens


def restore(source: str, tokens: dict[str, str]) -> str:
    """Replace placeholders back with original strings and comments."""
    result = source
    for placeholder, original in tokens.items():
        result = result.replace(placeholder, original)
    return result
