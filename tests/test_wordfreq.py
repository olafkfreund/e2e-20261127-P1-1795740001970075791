# AC#4: pytest -q passes across tests/test_wordfreq.py
#
# Subject: wordfreq/cli.py::_build_parser (parser validation and CLI behavior).
# Determinism of parser results across repeated builds stands in for the
# tie-breaking check; the criterion gives no concrete tie-breaking values.
import argparse

import pytest

from wordfreq.cli import _build_parser


@pytest.fixture
def parser():
    return _build_parser()


def test_build_parser_returns_argument_parser(parser):
    assert isinstance(parser, argparse.ArgumentParser)


def test_build_parser_help_flag_exits_zero(parser):
    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(["--help"])
    assert excinfo.value.code == 0


def test_build_parser_help_output_contains_usage(parser, capsys):
    with pytest.raises(SystemExit):
        parser.parse_args(["--help"])
    assert "usage:" in capsys.readouterr().out


def test_build_parser_unknown_option_exits_two(parser):
    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(["--definitely-not-an-option"])
    assert excinfo.value.code == 2


@pytest.mark.parametrize(
    "argv",
    [["--definitely-not-an-option"], ["--help"]],
    ids=["unknown-option", "help"],
)
def test_build_parser_repeated_builds_same_exit_code(argv):
    codes = []
    for _ in range(2):
        with pytest.raises(SystemExit) as excinfo:
            _build_parser().parse_args(argv)
        codes.append(excinfo.value.code)
    assert codes[0] == codes[1]
