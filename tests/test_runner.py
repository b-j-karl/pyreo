from pathlib import Path
from textwrap import dedent

import pytest

from pyreo.dictionary import load_dictionary
from pyreo.runner import run_source, run_file, PyReoError


@pytest.fixture
def dictionary(keywords_dir):
    return load_dictionary(keywords_dir / "mi.json")


class TestRunSource:
    def test_runs_simple_print(self, dictionary, capsys):
        run_source('tā("Kia ora")', dictionary)
        assert capsys.readouterr().out == "Kia ora\n"

    def test_runs_loop(self, dictionary, capsys):
        source = "mō i i tūemi(3):\n    tā(i)"
        run_source(source, dictionary)
        assert capsys.readouterr().out == "0\n1\n2\n"

    def test_runs_function_def_and_call(self, dictionary, capsys):
        source = dedent("""\
            tautuhi mihi(ingoa):
                whakahoki f"Kia ora, {ingoa}!"

            tā(mihi("Aotearoa"))
        """)
        run_source(source, dictionary)
        assert capsys.readouterr().out == "Kia ora, Aotearoa!\n"

    def test_syntax_error_includes_pyreo_context(self, dictionary):
        source = "mena x ==:\n    tā(x)"
        with pytest.raises(PyReoError, match="SyntaxError"):
            run_source(source, dictionary)

    def test_runtime_error_includes_pyreo_context(self, dictionary):
        source = "tā(x_undefined)"
        with pytest.raises(PyReoError, match="NameError"):
            run_source(source, dictionary)


class TestRunFile:
    def test_runs_pyreo_file(self, dictionary, fixtures_dir, capsys):
        run_file(fixtures_dir / "kia_ora.pyreo", dictionary)
        assert capsys.readouterr().out == "Kia ora, te ao!\n"

    def test_raises_on_missing_file(self, dictionary, tmp_path):
        with pytest.raises(PyReoError, match="not found"):
            run_file(tmp_path / "nope.pyreo", dictionary)
