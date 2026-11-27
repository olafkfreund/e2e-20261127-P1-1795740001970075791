# Criterion (AC#1): count_words extracts tokens, lowercases by default,
# preserves case when ignore_case=False, and sorts by (-count, word).
# Tokens are runs of [A-Za-z0-9]+. Result is a list of (word, count) tuples
# ordered by descending count, then ascending word.

import pytest

from wordfreq.cli import count_words


def test_count_words_extracts_alnum_tokens_only():
    text = "hello, world! foo_bar 42"

    result = count_words(text)

    assert result == [
        ("42", 1),
        ("bar", 1),
        ("foo", 1),
        ("hello", 1),
        ("world", 1),
    ]


def test_count_words_lowercases_by_default():
    text = "Hello HELLO hello"

    result = count_words(text)

    assert result == [("hello", 3)]


def test_count_words_preserves_case_when_ignore_case_false():
    text = "Hello HELLO hello"

    result = count_words(text, ignore_case=False)

    assert result == [
        ("HELLO", 1),
        ("Hello", 1),
        ("hello", 1),
    ]


@pytest.mark.parametrize(
    "text,expected",
    [
        (
            "b a b c a b",
            [("b", 3), ("a", 2), ("c", 1)],
        ),
        (
            "zeta alpha beta alpha beta",
            [("alpha", 2), ("beta", 2), ("zeta", 1)],
        ),
    ],
    ids=["count_desc_primary", "ties_broken_by_word_asc"],
)
def test_count_words_sorts_by_count_desc_then_word_asc(text, expected):
    result = count_words(text)

    assert result == expected
