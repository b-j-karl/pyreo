# PyReo for VS Code

Language support for [PyReo](https://github.com/b-j-karl/pyreo), Python in te reo Maori.

## Features

- Syntax highlighting for `.pyreo` files
- LSP-backed autocomplete, hover info, and diagnostics (transpile + compile errors)
- Auto-indent, bracket matching, and folding

## Requirements

The `pyreo` Python package must be installed and available on your PATH (or configured via `pyreo.pythonPath`):

```bash
pip install pyreo
```

## Settings

- `pyreo.pythonPath`: path to a Python executable with `pyreo` installed. Leave empty to use `python` from PATH.
- `pyreo.keywordsPath`: path to a custom `keywords/` directory. Leave empty to auto-detect.
