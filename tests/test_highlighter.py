"""Tests for csvdiff.highlighter."""
import pytest

from csvdiff.highlighter import HighlightConfig, highlight_change, highlight_cell_label


# ---------------------------------------------------------------------------
# HighlightConfig
# ---------------------------------------------------------------------------

def test_highlight_config_defaults():
    cfg = HighlightConfig()
    assert cfg.enabled is True
    assert cfg.min_length == 3


def test_highlight_config_rejects_zero_min_length():
    with pytest.raises(ValueError):
        HighlightConfig(min_length=0)


def test_highlight_config_accepts_min_length_one():
    cfg = HighlightConfig(min_length=1)
    assert cfg.min_length == 1


# ---------------------------------------------------------------------------
# highlight_change – disabled
# ---------------------------------------------------------------------------

def test_highlight_change_disabled_wraps_plain_colors():
    cfg = HighlightConfig(enabled=False)
    old_out, new_out = highlight_change("foo", "bar", cfg)
    # Should contain the raw text even if wrapped in ANSI codes
    assert "foo" in old_out
    assert "bar" in new_out


# ---------------------------------------------------------------------------
# highlight_change – too short for char diff
# ---------------------------------------------------------------------------

def test_highlight_change_short_values_no_char_diff():
    cfg = HighlightConfig(min_length=5)
    old_out, new_out = highlight_change("ab", "cd", cfg)
    assert "ab" in old_out
    assert "cd" in new_out


# ---------------------------------------------------------------------------
# highlight_change – char-level diff
# ---------------------------------------------------------------------------

def test_highlight_change_identical_values_no_markup():
    cfg = HighlightConfig()
    old_out, new_out = highlight_change("hello", "hello", cfg)
    # Equal segments are not wrapped in colour codes; raw text preserved
    assert "hello" in old_out
    assert "hello" in new_out


def test_highlight_change_returns_tuple_of_two_strings():
    old_out, new_out = highlight_change("abcdef", "abXdef")
    assert isinstance(old_out, str)
    assert isinstance(new_out, str)


def test_highlight_change_inserts_visible_in_new():
    _, new_out = highlight_change("price", "prices")
    assert "prices" in new_out or "s" in new_out


# ---------------------------------------------------------------------------
# highlight_cell_label
# ---------------------------------------------------------------------------

def test_highlight_cell_label_contains_column_name():
    label = highlight_cell_label("amount", "100", "200")
    assert "amount" in label


def test_highlight_cell_label_contains_arrow():
    label = highlight_cell_label("name", "Alice", "Bob")
    assert "→" in label


def test_highlight_cell_label_contains_old_and_new():
    label = highlight_cell_label("qty", "5", "10")
    assert "5" in label
    assert "10" in label
