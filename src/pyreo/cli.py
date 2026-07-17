from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pyreo import __version__
from pyreo.dictionary import load_dictionary, DictionaryError
from pyreo.keywords import find_keywords_file
from pyreo.runner import run_file, PyReoError
from pyreo.translator import translate


def main(argv: list[str] | None = None) -> None:
    # Ensure stdout and stderr use UTF-8 on Windows (cp1252 can't encode macrons).
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        prog="pyreo",
        description="PyReo - Write Python in te reo Māori",
    )
    parser.add_argument(
        "--version", action="version", version=f"pyreo {__version__}"
    )
    parser.add_argument(
        "--keywords",
        type=Path,
        help="Path to keyword dictionary JSON file",
    )

    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run a .pyreo file")
    run_parser.add_argument("file", type=Path, help="Path to .pyreo file")

    translate_parser = subparsers.add_parser(
        "translate", help="Show translated Python code"
    )
    translate_parser.add_argument("file", type=Path, help="Path to .pyreo file")

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return

    try:
        dict_path = args.keywords if args.keywords else find_keywords_file()
        dictionary = load_dictionary(dict_path)
    except DictionaryError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.command == "run":
        try:
            run_file(args.file, dictionary)
        except PyReoError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "translate":
        path = Path(args.file)
        if not path.exists():
            print(f"Error: File not found: {path}", file=sys.stderr)
            sys.exit(1)
        source = path.read_text(encoding="utf-8")
        print(translate(source, dictionary))
