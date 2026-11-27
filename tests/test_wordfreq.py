"""Unit and CLI tests for the wordfreq package."""

from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

from wordfreq.cli import count_words, format_table, main

REPO_ROOT = Path(__file__).resolve().parents[1]


def _run_module(args: list[str], stdin: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "wordfreq", *args],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
        timeout=60,
    )


def test_count_words_basic_ranking() -> None:
    text = "Apple banana apple, cherry! Banana apple."
    assert count_words(text) == [("apple", 3), ("banana", 2), ("cherry", 1)]


def test_count_words_ties_break_alphabetically() -> None:
    assert count_words("zeta alpha mid mid alpha beta") == [
        ("alpha", 2),
        ("mid", 2),
        ("beta", 1),
        ("zeta", 1),
    ]


def test_count_words_is_independent_of_input_order() -> None:
    results = {tuple(count_words(text)) for text in ["a b c", "c b a", "b c a"]}
    assert results == {(("a", 1), ("b", 1), ("c", 1))}


def test_count_words_lowercases_by_default() -> None:
    assert count_words("Word word WORD") == [("word", 3)]


def test_count_words_case_sensitive_keeps_case_distinct() -> None:
    assert count_words("Word word word", ignore_case=False) == [("word", 2), ("Word", 1)]


def test_count_words_case_sensitive_ties_sort_by_codepoint() -> None:
    assert count_words("word Word WORD", ignore_case=False) == [
        ("WORD", 1),
        ("Word", 1),
        ("word", 1),
    ]


def test_count_words_only_ascii_alphanumeric_tokens() -> None:
    assert count_words("don't rock-n-roll café 42") == [
        ("42", 1),
        ("caf", 1),
        ("don", 1),
        ("n", 1),
        ("rock", 1),
        ("roll", 1),
        ("t", 1),
    ]


def test_count_words_min_len_filters_short_words() -> None:
    assert count_words("a bb ccc bb", min_len=2) == [("bb", 2), ("ccc", 1)]


def test_count_words_top_limits_rows() -> None:
    text = "x x x y y z"
    assert count_words(text, top=1) == [("x", 3)]
    assert count_words(text, top=2) == [("x", 3), ("y", 2)]


def test_count_words_top_zero_returns_empty() -> None:
    assert count_words("a b", top=0) == []


def test_count_words_empty_text_returns_empty() -> None:
    assert count_words("") == []
    assert count_words("!!! ---") == []


def test_count_words_rejects_min_len_below_one() -> None:
    with pytest.raises(ValueError, match="min_len must be >= 1"):
        count_words("a", min_len=0)


def test_count_words_rejects_negative_top() -> None:
    with pytest.raises(ValueError, match="top must be >= 0"):
        count_words("a", top=-1)


def test_format_table_tsv() -> None:
    assert format_table([("apple", 3), ("banana", 2)]) == "apple\t3\nbanana\t2"


def test_format_table_empty_input_returns_empty_string() -> None:
    assert format_table([]) == ""


def test_main_reads_stdin_by_default(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("b a a\n"))
    rc = main([])
    assert rc == 0
    assert capsys.readouterr().out == "a\t2\nb\t1\n"


def test_main_reads_stdin_for_dash_path(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("b a a\n"))
    rc = main(["-"])
    assert rc == 0
    assert capsys.readouterr().out == "a\t2\nb\t1\n"


def test_main_default_lowercases_input(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("Word word WORD", encoding="utf-8")
    rc = main([str(sample)])
    assert rc == 0
    assert capsys.readouterr().out == "word\t3\n"


def test_main_case_sensitive_flag_keeps_case_distinct(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("Word word word\n"))
    rc = main(["--case-sensitive"])
    assert rc == 0
    assert capsys.readouterr().out == "word\t2\nWord\t1\n"


def test_main_top_zero_writes_nothing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("a b\n"))
    rc = main(["--top", "0"])
    assert rc == 0
    assert capsys.readouterr().out == ""


def test_main_empty_tsv_output_writes_nothing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("!!! ---\n"))
    rc = main([])
    assert rc == 0
    assert capsys.readouterr().out == ""


def test_main_tsv_output_ends_with_single_newline(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("a b"))
    rc = main([])
    assert rc == 0
    out = capsys.readouterr().out
    assert out == "a\t1\nb\t1\n"
    assert out.endswith("\n")
    assert not out.endswith("\n\n")


def test_main_json_output_is_list_of_objects_with_trailing_newline(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("b a a"))
    rc = main(["--json"])
    assert rc == 0
    out = capsys.readouterr().out
    assert out == '[{"word": "a", "count": 2}, {"word": "b", "count": 1}]\n'
    assert json.loads(out) == [{"word": "a", "count": 2}, {"word": "b", "count": 1}]


def test_main_json_empty_input_emits_empty_list(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO(""))
    rc = main(["--json"])
    assert rc == 0
    assert capsys.readouterr().out == "[]\n"


def test_main_json_honors_case_sensitive_and_top(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("Word word word"))
    rc = main(["--json", "--case-sensitive", "--top", "1"])
    assert rc == 0
    assert json.loads(capsys.readouterr().out) == [{"word": "word", "count": 2}]


def test_cli_top_and_min_len(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("to be or not to be that is the question", encoding="utf-8")
    rc = main([str(sample), "--min-len", "3", "--top", "2"])
    assert rc == 0
    out = capsys.readouterr().out
    assert out.strip().splitlines() == ["not\t1", "question\t1"]


@pytest.mark.parametrize(
    "argv",
    [
        ["--top=-1"],
        ["--top", "many"],
        ["--min-len=0"],
        ["--min-len", "abc"],
        ["--bogus"],
    ],
)
def test_main_rejects_invalid_arguments_with_exit_2(
    argv: list[str],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("a b"))
    rc = main(argv)
    captured = capsys.readouterr()
    assert rc == 2
    assert captured.out == ""
    assert captured.err != ""


def test_main_missing_file_exits_2_with_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rc = main([str(tmp_path / "does-not-exist.txt")])
    captured = capsys.readouterr()
    assert rc == 2
    assert captured.out == ""
    assert "cannot read" in captured.err


def test_main_directory_path_exits_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = main([str(tmp_path)])
    captured = capsys.readouterr()
    assert rc == 2
    assert captured.err != ""


def test_main_invalid_utf8_exits_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    sample = tmp_path / "binary.txt"
    sample.write_bytes(b"\xff\xfe\xfd")
    rc = main([str(sample)])
    captured = capsys.readouterr()
    assert rc == 2
    assert "cannot decode" in captured.err


def test_python_m_wordfreq_reads_file_path(tmp_path: Path) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("b a a\n", encoding="utf-8")
    result = _run_module([str(sample)])
    assert result.returncode == 0
    assert result.stdout == "a\t2\nb\t1\n"
    assert result.stderr == ""


def test_python_m_wordfreq_reads_stdin_by_default() -> None:
    result = _run_module([], stdin="b a a\n")
    assert result.returncode == 0
    assert result.stdout == "a\t2\nb\t1\n"
    assert result.stderr == ""


def test_python_m_wordfreq_dash_reads_stdin() -> None:
    result = _run_module(["-", "--case-sensitive"], stdin="Word word word\n")
    assert result.returncode == 0
    assert result.stdout == "word\t2\nWord\t1\n"


def test_python_m_wordfreq_empty_tsv_writes_nothing() -> None:
    result = _run_module([], stdin="!!!\n")
    assert result.returncode == 0
    assert result.stdout == ""


def test_python_m_wordfreq_json_ends_with_newline() -> None:
    result = _run_module(["--json", "--top", "1"], stdin="b a a\n")
    assert result.returncode == 0
    assert result.stdout == '[{"word": "a", "count": 2}]\n'


def test_python_m_wordfreq_missing_file_exits_2(tmp_path: Path) -> None:
    result = _run_module([str(tmp_path / "missing.txt")])
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr != ""


def test_python_m_wordfreq_invalid_argument_exits_2() -> None:
    result = _run_module(["--min-len=0"], stdin="a b\n")
    assert result.returncode == 2
    assert result.stderr != ""
