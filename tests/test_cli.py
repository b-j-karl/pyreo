import subprocess
import sys
from pathlib import Path

import pytest


PYREO = [sys.executable, "-m", "pyreo"]
PROJECT_ROOT = Path(__file__).parent.parent


class TestCLIRun:
    def test_runs_pyreo_file(self, fixtures_dir):
        result = subprocess.run(
            [*PYREO, "run", str(fixtures_dir / "kia_ora.pyreo")],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0
        assert "Kia ora, te ao!" in result.stdout

    def test_error_on_missing_file(self):
        result = subprocess.run(
            [*PYREO, "run", "nonexistent.pyreo"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode != 0
        assert "not found" in result.stderr.lower() or "error" in result.stderr.lower()


class TestCLITranslate:
    def test_outputs_translated_python(self, fixtures_dir):
        result = subprocess.run(
            [*PYREO, "translate", str(fixtures_dir / "kia_ora.pyreo")],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0
        assert 'print("Kia ora, te ao!")' in result.stdout


class TestCLIVersion:
    def test_shows_version(self):
        result = subprocess.run(
            [*PYREO, "--version"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0
        assert "0.1.0" in result.stdout


class TestCLIHelp:
    def test_shows_help(self):
        result = subprocess.run(
            [*PYREO, "--help"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0
        assert "pyreo" in result.stdout.lower() or "usage" in result.stdout.lower()
