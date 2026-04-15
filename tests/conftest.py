from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def keywords_dir():
    return Path(__file__).parent.parent / "keywords"
