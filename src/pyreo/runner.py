from __future__ import annotations

import traceback
from pathlib import Path

from pyreo.dictionary import Dictionary
from pyreo.translator import translate


class PyReoError(Exception):
    pass


def run_source(source: str, dictionary: Dictionary, filename: str = "<pyreo>") -> None:
    """Translate and execute PyReo source code."""
    python_code = translate(source, dictionary)

    try:
        compiled = compile(python_code, filename, "exec")
        exec(compiled, {"__name__": "__main__", "__builtins__": __builtins__})
    except SyntaxError as e:
        raise PyReoError(
            f"SyntaxError in {filename}: {e.msg} (line {e.lineno})"
        ) from e
    except Exception as e:
        tb = traceback.format_exc()
        raise PyReoError(
            f"{type(e).__name__}: {e}\n\nTranslated Python:\n{python_code}\n\nTraceback:\n{tb}"
        ) from e


def run_file(path: Path, dictionary: Dictionary) -> None:
    """Load and execute a .pyreo file."""
    path = Path(path)
    if not path.exists():
        raise PyReoError(f"File not found: {path}")

    source = path.read_text(encoding="utf-8")
    run_source(source, dictionary, filename=str(path))
