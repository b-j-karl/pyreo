from pathlib import Path

import pytest

from pyreo.dictionary import load_dictionary
from pyreo.translator import translate


@pytest.fixture
def dictionary(keywords_dir):
    return load_dictionary(keywords_dir / "mi.json")


class TestTranslate:
    def test_translates_simple_print(self, dictionary):
        source = 'tā("Kia ora")'
        result = translate(source, dictionary)
        assert result == 'print("Kia ora")'

    def test_translates_if_else(self, dictionary):
        source = "mena x > 0:\n    tā(x)\nkē:\n    tā(0)"
        result = translate(source, dictionary)
        assert result == "if x > 0:\n    print(x)\nelse:\n    print(0)"

    def test_translates_for_loop(self, dictionary):
        source = "mō i i tūemi(10):\n    tā(i)"
        result = translate(source, dictionary)
        assert result == "for i in range(10):\n    print(i)"

    def test_translates_while_loop(self, dictionary):
        source = "ia pono:\n    waea"
        result = translate(source, dictionary)
        assert result == "while True:\n    break"

    def test_translates_function_def(self, dictionary):
        source = "tautuhi mihi(ingoa):\n    whakahoki f'Kia ora {ingoa}'"
        result = translate(source, dictionary)
        assert result == "def mihi(ingoa):\n    return f'Kia ora {ingoa}'"

    def test_preserves_strings(self, dictionary):
        source = 'tā("mena this has keywords mō")'
        result = translate(source, dictionary)
        assert result == 'print("mena this has keywords mō")'

    def test_preserves_comments(self, dictionary):
        source = "x = 5  # mena this is mō comment"
        result = translate(source, dictionary)
        assert result == "x = 5  # mena this is mō comment"

    def test_preserves_variable_names_with_macrons(self, dictionary):
        source = "kōrero = 5\ntā(kōrero)"
        result = translate(source, dictionary)
        assert result == "kōrero = 5\nprint(kōrero)"

    def test_does_not_partial_match_keywords(self, dictionary):
        source = "taumena = 5"
        result = translate(source, dictionary)
        assert result == "taumena = 5"

    def test_translates_class_def(self, dictionary):
        source = "momo Tangata:\n    pahika"
        result = translate(source, dictionary)
        assert result == "class Tangata:\n    pass"

    def test_translates_try_except(self, dictionary):
        source = "ngana:\n    tā(x)\nhopu:\n    tā('hapa')"
        result = translate(source, dictionary)
        assert result == "try:\n    print(x)\nexcept:\n    print('hapa')"

    def test_translates_boolean_operators(self, dictionary):
        source = "mena x me ehara y:"
        result = translate(source, dictionary)
        assert result == "if x and not y:"

    def test_fixture_file_kia_ora(self, dictionary, fixtures_dir):
        source = (fixtures_dir / "kia_ora.pyreo").read_text(encoding="utf-8").strip()
        expected = (fixtures_dir / "kia_ora_expected.py").read_text(encoding="utf-8").strip()
        assert translate(source, dictionary) == expected

    def test_fixture_file_loop(self, dictionary, fixtures_dir):
        source = (fixtures_dir / "loop.pyreo").read_text(encoding="utf-8").strip()
        expected = (fixtures_dir / "loop_expected.py").read_text(encoding="utf-8").strip()
        assert translate(source, dictionary) == expected

    def test_translates_import(self, dictionary):
        source = "kawemai math"
        result = translate(source, dictionary)
        assert result == "import math"

    def test_translates_from_import(self, dictionary):
        source = "mai math kawemai sqrt"
        result = translate(source, dictionary)
        assert result == "from math import sqrt"

    def test_translates_builtins_inside_fstrings(self, dictionary):
        source = 'tā(f"Whakaroto: {tapeke(nama)}")'
        result = translate(source, dictionary)
        assert result == 'print(f"Whakaroto: {sum(nama)}")'

    def test_translates_keywords_inside_fstrings(self, dictionary):
        source = 'f"{roa(x)}"'
        result = translate(source, dictionary)
        assert result == 'f"{len(x)}"'

    def test_fstring_preserves_literal_text(self, dictionary):
        source = 'tā(f"mena is a keyword but this is literal {x}")'
        result = translate(source, dictionary)
        assert result == 'print(f"mena is a keyword but this is literal {x}")'
