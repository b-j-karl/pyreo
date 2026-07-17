# Contributing to PyReo

There are two very different ways to contribute to this project, and they're both valuable. You don't need to do both.

---

## Contributing te reo Māori expertise

**This is the most valuable contribution to PyReo right now.**

The keyword dictionary at `src/pyreo/keywords/mi.json` contains draft placeholders. For PyReo to be worthwhile as an educational tool, those words need to be the right words chosen by people who are fluent in te reo Māori and understand the cultural weight of each term.

You **do not** need to know how to code to help with this.

### How to contribute

1. Open `docs/keywords-review.xlsx`. This spreadsheet has every keyword with a plain-English description of what it means in programming terms.
2. For each row, look at the description and suggest a te reo Māori word that captures that meaning. Add your suggestions in the "Your Suggestion" column.
3. Email the updated spreadsheet back, or open a pull request with the changes applied to `src/pyreo/keywords/mi.json` and `src/pyreo/keywords/mi.descriptions.json`.

If you'd like to discuss the keyword choices before suggesting changes, please [open a GitHub issue](https://github.com/b-j-karl/pyreo/issues). We welcome the kōrero.

### What we're looking for

- **Words that feel natural** to a Year 6-10 student in kura kaupapa
- **Words with the right cultural register**, not jargon, not stilted, not awkwardly loan-translated
- **Consistency** related programming concepts should have words that feel related

We're explicitly NOT looking to:
- Preserve the current draft words if better options exist
- Force English concepts into te reo that don't fit. If a Python concept doesn't map cleanly to a te reo word, we'd rather discuss that honestly

---

## Contributing code

### Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/b-j-karl/pyreo.git
cd pyreo
uv sync
```

### Running tests

```bash
uv run pytest -v
```

All tests should pass before you open a PR.

### Running PyReo

```bash
uv run python -m pyreo run examples/tauanga.pyreo
uv run python -m pyreo translate examples/kemu.pyreo
```

### The VS Code extension

The extension has two parts:

- **Syntax / icon**: pure config in `vscode-pyreo/` (tmLanguage grammar, language config)
- **Language server**: Python code in `src/pyreo/server.py` that provides autocomplete, hover, and diagnostics

To regenerate the tmLanguage grammar after editing `src/pyreo/keywords/mi.json`:

```bash
uv run python vscode-pyreo/generate.py
```

To build and install the extension locally:

```bash
cd vscode-pyreo
npm install
npm run package
code --install-extension pyreo-0.2.0.vsix
```

Then reload VS Code (`Ctrl+Shift+P` > "Developer: Reload Window").

### Where to look for improvements

Some known limitations and good first issues:

- **Error messages are in English.** Integrating [friendly-traceback](https://github.com/friendly-traceback/friendly-traceback) with a te reo Māori translation would help learners understand errors.
- **No block-based editor** for younger kids. A Blockly or Scratch-style interface that generates PyReo code would extend the age range.


### Code style

- Follow existing patterns in the codebase
- No comments on code that's self-explanatory; comment *why* not *what*
- Run `uv run pytest` before committing

### Commits

Conventional commits style:

- `feat: ...` for new features
- `fix: ...` for bug fixes
- `docs: ...` for documentation
- `chore: ...` for maintenance

---

## Reporting issues

Open a GitHub issue with:

- What you were trying to do
- What you expected to happen
- What actually happened
- PyReo version (from `pyproject.toml`), Python version, OS

---

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). This project operates with respect for Te Tiriti o Waitangi and welcomes participation from anyone who shares that respect.
