# Criterion (AC#3): main and `python -m wordfreq` read from sys.stdin by default
# and return 0 or 2. Verify `python -m wordfreq` run as a subprocess reads stdin,
# prints TSV/JSON, and exits 2 with stderr for a missing file.

import subprocess
import sys

import pytest

from wordfreq.cli import main  # noqa: F401  (import root check for the target)


def _run_module(args=None, stdin_text=""):
    """Run `python -m wordfreq` as a subprocess and return the CompletedProcess."""
    cmd = [sys.executable, "-m", "wordfreq"]
    if args:
        cmd.extend(args)
    return subprocess.run(
        cmd,
        input=stdin_text,
        capture_output=True,
        text=True,
        timeout=30,
    )


@pytest.fixture
def sample_stdin():
    return "the quick brown fox jumps over the lazy dog the end\n"


def test_python_m_wordfreq_reads_stdin_exits_zero(sample_stdin):
    result = _run_module(stdin_text=sample_stdin)
    assert result.returncode == 0


def test_python_m_wordfreq_reads_stdin_prints_output(sample_stdin):
    result = _run_module(stdin_text=sample_stdin)
    assert result.stdout.strip() != ""


def test_python_m_wordfreq_reads_stdin_prints_no_stderr(sample_stdin):
    result = _run_module(stdin_text=sample_stdin)
    assert result.stderr == ""


def test_python_m_wordfreq_missing_file_exits_2(tmp_path):
    missing = tmp_path / "does_not_exist.txt"
    result = _run_module(args=[str(missing)])
    assert result.returncode == 2


def test_python_m_wordfreq_missing_file_writes_stderr(tmp_path):
    missing = tmp_path / "does_not_exist.txt"
    result = _run_module(args=[str(missing)])
    assert result.stderr.strip() != ""
