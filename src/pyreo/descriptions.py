from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DescriptionEntry:
    maori: str
    python: str
    category: str
    description: str

    @property
    def detail(self) -> str:
        return f"{self.maori} → {self.python}"

    @property
    def documentation(self) -> str:
        return f"**{self.maori}** → `{self.python}`\n\n{self.description}"


def load_descriptions(path: Path) -> dict[str, DescriptionEntry]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Descriptions file not found: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    entries: dict[str, DescriptionEntry] = {}

    for section in ("keywords", "builtins"):
        for maori, info in data.get(section, {}).items():
            entries[maori] = DescriptionEntry(
                maori=maori,
                python=info["python"],
                category=info["category"],
                description=info["description"],
            )

    return entries
