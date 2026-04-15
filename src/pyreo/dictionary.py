from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


class DictionaryError(Exception):
    pass


@dataclass
class Dictionary:
    keywords: dict[str, str]
    builtins: dict[str, str]
    meta: dict[str, str] = field(default_factory=dict)

    def all_mappings(self) -> dict[str, str]:
        """Return all keyword + builtin mappings, sorted longest-first."""
        combined = {**self.keywords, **self.builtins}
        return dict(sorted(combined.items(), key=lambda item: len(item[0]), reverse=True))


def load_dictionary(path: Path) -> Dictionary:
    path = Path(path)
    if not path.exists():
        raise DictionaryError(f"Dictionary file not found: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError) as e:
        raise DictionaryError(f"Dictionary file invalid: {e}") from e

    if "keywords" not in data:
        raise DictionaryError("Dictionary missing required 'keywords' section")

    return Dictionary(
        keywords=data["keywords"],
        builtins=data.get("builtins", {}),
        meta=data.get("_meta", {}),
    )
