from __future__ import annotations

import re

from pyreo.dictionary import Dictionary
from pyreo.protector import protect, restore


def _maori_keyword(mappings: dict[str, str], python_keyword: str) -> str | None:
    """Return the Māori keyword that maps to the given Python keyword, or None."""
    for maori, python in mappings.items():
        if python == python_keyword:
            return maori
    return None


def translate(source: str, dictionary: Dictionary) -> str:
    """Translate PyReo source (te reo Māori keywords) to standard Python."""
    protected, tokens = protect(source)

    mappings = dictionary.all_mappings()

    # The keyword "i" (→ "in") is a single ASCII letter that is also a common
    # variable/parameter name (e.g. loop counter).  Pure word-boundary matching
    # cannot distinguish keyword use from variable use because both look like \bi\b.
    #
    # Strategy:
    # 1. Replace `mō VAR i ITERABLE` atomically → `for VAR in ITERABLE` before
    #    any other substitution.  This covers the for-loop use.
    # 2. Replace standalone `i` (preceded by an identifier and whitespace) for
    #    membership-test use: `x i collection` → `x in collection`.
    # 3. Skip the generic \bi\b pass entirely (handled by steps 1 & 2).
    _for_kw = _maori_keyword(mappings, "for")
    _in_kw = _maori_keyword(mappings, "in")

    if _for_kw and _in_kw:
        # Step 1: atomic for-loop pattern.  Handles multi-variable unpacking too:
        #   mō x, y i pairs → for x, y in pairs
        _id = r"[\w\u0100-\u017F]+"  # identifier (including macron chars)
        _var_list = rf"{_id}(?:\s*,\s*{_id})*"  # one or more comma-separated vars
        protected = re.sub(
            r"\b" + re.escape(_for_kw) + r"\b"
            + r"(\s+" + _var_list + r"\s+)"
            + r"\b" + re.escape(_in_kw) + r"\b",
            lambda m: "for" + m.group(1) + "in",
            protected,
        )

        # Step 2: membership-test use - `EXPR i COLLECTION`.
        # Only replace `i` when it follows a closing bracket/paren or a word
        # that is NOT a Python keyword (to avoid matching `for i` where `for`
        # ends with `r`, a word char).  We exclude matches preceded by Python
        # keywords by requiring the preceding character to be `)`, `]`, `}`,
        # or a digit - safe non-keyword endings.  Identifier endings that could
        # be Python keywords are left to be handled by user-facing variables;
        # this is an acceptable limitation for the MVP.
        protected = re.sub(
            r"(?<=[)\]}\d])(\s+)" + r"\b" + re.escape(_in_kw) + r"\b" + r"(?=\s)",
            lambda m: m.group(1) + "in",
            protected,
        )

    for maori, python in mappings.items():
        if maori == _in_kw:
            # Already handled above - skip to avoid clobbering variable names.
            continue
        # Use word-boundary regex to avoid partial matches.
        # re.UNICODE is default in Python 3, so \b handles macrons correctly.
        pattern = re.compile(r"\b" + re.escape(maori) + r"\b")
        protected = pattern.sub(python, protected)

    return restore(protected, tokens)
