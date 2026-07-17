<p align="center">
  <img src="vscode-pyreo/icon.svg" alt="PyReo" width="160">
</p>

# PyReo

[![Tests](https://github.com/b-j-karl/pyreo/actions/workflows/tests.yml/badge.svg)](https://github.com/b-j-karl/pyreo/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

**Write Python in te reo Māori.**

PyReo is an open-source programming language designed for tamariki Māori learning to code. It's a thin wrapper around Python where the keywords are in te reo Māori. So `mena` is `if`, `mō` is `for`, `tā` is `print`. Under the hood it's real Python, so everything tamariki learn transfers when they're ready to work in English-medium Python.

```python
# Kia ora, te ao!
tautuhi mihi(ingoa):
    whakahoki f"Kia ora, {ingoa}!"

tā(mihi("Aotearoa"))
```

---

## ⚠️ Draft status - not ready for educational use

The te reo Māori keyword choices in `src/pyreo/keywords/mi.json` are **draft placeholders**. They have **not** been reviewed or validated by fluent te reo Māori speakers. Before this is used with learners, those keywords need to be reviewed, and likely changed, by people with the right cultural and linguistic expertise.

If you are a te reo speaker interested in helping refine the keywords, see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Why

The [NZ Digital Technologies curriculum](https://newzealandcurriculum.tahurangi.education.govt.nz/the-new-zealand-curriculum---technology/5637209125.p) has required all students to learn computational thinking and programming since 2020. But every mainstream programming language and coding tool operates in English. That means teachers in full-immersion kura face a choice: break the kaupapa to teach coding, or skip it.

PyReo exists to close that gap. It's intentionally thin: the language is free and open-source, so adoption has no friction. The value lives in the curriculum and pedagogy that gets built on top, and that's the part that has to be co-designed with kaiako and kura.

## Install

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/b-j-karl/pyreo.git
cd pyreo
uv sync
```

## Quick start

Run one of the included examples:

```bash
uv run python -m pyreo run examples/tauanga.pyreo
```

See the translated Python:

```bash
uv run python -m pyreo translate examples/kemu.pyreo
```

Write your own `hello.pyreo`:

```python
tā("Kia ora, te ao!")

ingoa = pātai("Ko wai tō ingoa? ")
tā(f"Kia ora, {ingoa}!")
```

Run it:

```bash
uv run python -m pyreo run hello.pyreo
```

## VS Code extension

A VS Code extension in `vscode-pyreo/` provides:

- Syntax highlighting (keywords, builtins, strings, numbers)
- A custom file icon
- Autocomplete for Māori keywords/builtins with descriptions
- Hover info (`mena → if` with plain-English explanation)
- Live error diagnostics (red squiggles for syntax errors)

To install locally:

```bash
cd vscode-pyreo
npm install
npm run package
code --install-extension pyreo-0.2.0.vsix
```

Then reload VS Code. Configure `pyreo.pythonPath` in settings if needed to point to a Python that has `pyreo` installed.

## Project structure

```
pyreo/
├── src/pyreo/              # The language package
│   ├── dictionary.py       # Load keyword JSON dictionaries
│   ├── protector.py        # Mask strings/comments before translation
│   ├── translator.py       # Core keyword replacement
│   ├── runner.py           # Execute translated Python
│   ├── cli.py              # `pyreo run` and `pyreo translate`
│   ├── server.py           # Language Server (autocomplete, hover, diagnostics)
│   └── descriptions.py     # Load keyword descriptions
│   ├── keywords/
│   │   ├── mi.json           # Te reo Māori keyword dictionary (draft)
│   │   └── mi.descriptions.json  # Human-readable descriptions
├── examples/               # Example .pyreo programs
├── vscode-pyreo/           # VS Code extension (syntax + LSP client)
├── scripts/                # Dev tools (icon generator, tuner)
├── docs/                   # Plans, specs, keyword review spreadsheet
└── tests/                  # pytest tests
```

## How it works

PyReo is a source-to-source transpiler:

1. **Read** the `.pyreo` file
2. **Protect** string literals and comments so keywords inside them aren't touched
3. **Translate** each te reo Māori keyword/builtin to its Python equivalent, using word-boundary regex (longest match first)
4. **Restore** the protected strings/comments
5. **Execute** the resulting standard Python

The keyword mappings live in [`src/pyreo/keywords/mi.json`](src/pyreo/keywords/mi.json). To change a keyword, edit the JSON. No code changes are needed.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). There are two very different ways to help:

- **Te reo Māori expertise**: review the keyword choices in `mi.json`. This does **not** require coding knowledge. The most valuable contribution to this project right now.
- **Code**: transpiler improvements, the language server, the VS Code extension, tests.

## Acknowledgements

- **Citrine** ([citrine-lang.org](https://citrine-lang.org)): the only other general-purpose programming language with a te reo Māori keyword set. A reference point while designing PyReo's keyword dictionary.
- **Hedy** ([hedy.org](https://hedy.org)): Felienne Hermans' gradual multilingual educational language, which demonstrated that native-language keywords work for young learners.

## License

[MIT](LICENSE)
