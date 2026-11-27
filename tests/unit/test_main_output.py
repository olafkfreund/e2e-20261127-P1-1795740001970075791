# AC#3: main reads stdin by default or '-', honors --case-sensitive/--top/--min-len/--json,
# terminates TSV/--json output with a final newline, and writes nothing for empty TSV.
import io
import json
import sys

import pytest

from wordfreq.cli import main


def _feed_stdin(monkeypatch, text):
    monkeypatch.setattr(sys, "stdin", io.StringIO(text))


def _tsv_lines(out):
    return [line for line in out.split("\n") if line]


def test_main_reads_stdin_by_default_when_no_argument_given(monkeypatch, capsys):
    _feed_stdin(monkeypatch, "apple banana apple\n")
    main([])
    out = capsys.readouterr().out
    assert "apple" in out


def test_main_reads_stdin_when_dash_argument_given(monkeypatch, capsys):
    _feed_stdin(monkeypatch, "apple banana apple\n")
    main(["-"])
    out = capsys.readouterr().out
    assert "banana" in out


def test_main_case_sensitive_flag_keeps_case_variants_distinct(monkeypatch, capsys):
    _feed_stdin(monkeypatch, "Apple apple\n")
    main(["--case-sensitive"])
    lines = _tsv_lines(capsys.readouterr().out)
    words = {line.split("\t")[0] for line in lines}
    assert words == {"Apple", "apple"}


def test_main_top_flag_limits_output_rows(monkeypatch, capsys):
    _feed_stdin(monkeypatch, "alpha beta gamma delta epsilon\n")
    main(["--top", "2"])
    lines = _tsv_lines(capsys.readouterr().out)
    assert len(lines) == 2


def test_main_min_len_flag_excludes_shorter_words(monkeypatch, capsys):
    _feed_stdin(monkeypatch, "a bb ccc\n")
    main(["--min-len", "3"])
    lines = _tsv_lines(capsys.readouterr().out)
    words = {line.split("\t")[0] for line in lines}
    assert words == {"ccc"}


def test_main_json_flag_emits_parseable_json(monkeypatch, capsys):
    _feed_stdin(monkeypatch, "apple banana apple\n")
    main(["--json"])
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert parsed is not None


@pytest.mark.parametrize(
    "argv",
    [[], ["--json"]],
    ids=["tsv-default", "json-flag"],
)
def test_main_output_ends_with_final_newline(monkeypatch, capsys, argv):
    _feed_stdin(monkeypatch, "apple banana apple\n")
    main(argv)
    out = capsys.readouterr().out
    assert out.endswith("\n")


def test_main_empty_stdin_tsv_writes_nothing(monkeypatch, capsys):
    _feed_stdin(monkeypatch, "")
    main([])
    out = capsys.readouterr().out
    assert out == ""
