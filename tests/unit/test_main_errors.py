# AC#3: main returns 0 on success, or 2 with non-empty stderr on invalid
# arguments (--top -1, --min-len 0, non-integer values) or missing files.

import pytest

from wordfreq.cli import main


@pytest.fixture
def sample_input(tmp_path):
    path = tmp_path / "input.txt"
    path.write_text("the cat and the dog and the bird\n", encoding="utf-8")
    return path


def test_main_valid_input_returns_zero(sample_input):
    assert main([str(sample_input)]) == 0


@pytest.mark.parametrize(
    "extra_args",
    [
        ["--top", "-1"],
        ["--min-len", "0"],
        ["--top", "abc"],
        ["--min-len", "1.5"],
    ],
    ids=["top-negative", "min-len-zero", "top-non-integer", "min-len-float"],
)
def test_main_invalid_argument_returns_two(sample_input, extra_args):
    assert main([*extra_args, str(sample_input)]) == 2


@pytest.mark.parametrize(
    "extra_args",
    [
        ["--top", "-1"],
        ["--min-len", "0"],
        ["--top", "abc"],
        ["--min-len", "1.5"],
    ],
    ids=["top-negative", "min-len-zero", "top-non-integer", "min-len-float"],
)
def test_main_invalid_argument_writes_stderr(sample_input, capsys, extra_args):
    main([*extra_args, str(sample_input)])
    assert capsys.readouterr().err != ""


def test_main_missing_file_returns_two(tmp_path):
    missing = tmp_path / "does_not_exist.txt"
    assert main([str(missing)]) == 2


def test_main_missing_file_writes_stderr(tmp_path, capsys):
    missing = tmp_path / "does_not_exist.txt"
    main([str(missing)])
    assert capsys.readouterr().err != ""
