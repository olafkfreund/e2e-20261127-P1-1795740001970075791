# AC#1: count_words filters by min_len, truncates by top, and raises
# ValueError('min_len must be >= 1') / ValueError('top must be >= 0').

import re

import pytest

from wordfreq.cli import count_words


TEXT = "a a a bb bb ccc dddd dddd dddd dddd"


def _keys(result):
    if hasattr(result, "items"):
        return {word for word, _ in result.items()}
    return {entry[0] for entry in result}


def _size(result):
    if hasattr(result, "items"):
        return len(result)
    return len(list(result))


def test_count_words_min_len_excludes_shorter_words():
    result = count_words(TEXT, min_len=3)
    assert _keys(result) == {"ccc", "dddd"}


def test_count_words_min_len_keeps_words_equal_to_min_len():
    result = count_words("ab abc abcd", min_len=3)
    assert _keys(result) == {"abc", "abcd"}


def test_count_words_top_truncates_to_requested_count():
    result = count_words(TEXT, top=2)
    assert _size(result) == 2


def test_count_words_top_keeps_most_frequent_words():
    result = count_words(TEXT, top=2)
    assert _keys(result) == {"a", "dddd"}


def test_count_words_top_zero_returns_no_words():
    result = count_words(TEXT, top=0)
    assert _size(result) == 0


@pytest.mark.parametrize(
    "min_len",
    [0, -1, -5],
    ids=["min_len_zero", "min_len_minus_one", "min_len_minus_five"],
)
def test_count_words_min_len_below_one_raises_value_error(min_len):
    with pytest.raises(ValueError, match=re.escape("min_len must be >= 1")):
        count_words(TEXT, min_len=min_len)


@pytest.mark.parametrize(
    "top",
    [-1, -10],
    ids=["top_minus_one", "top_minus_ten"],
)
def test_count_words_top_below_zero_raises_value_error(top):
    with pytest.raises(ValueError, match=re.escape("top must be >= 0")):
        count_words(TEXT, top=top)


def test_count_words_min_len_one_is_accepted():
    result = count_words(TEXT, min_len=1)
    assert _keys(result) == {"a", "bb", "ccc", "dddd"}


def test_count_words_top_zero_is_accepted_without_error():
    assert count_words(TEXT, top=0) is not None
