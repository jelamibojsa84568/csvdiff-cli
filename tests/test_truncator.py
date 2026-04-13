"""Tests for csvdiff.truncator."""

import pytest

from csvdiff.truncator import (
    DEFAULT_MAX_LENGTH,
    TruncateConfig,
    truncate_value,
    truncate_row_values,
)


# ---------------------------------------------------------------------------
# TruncateConfig
# ---------------------------------------------------------------------------


def test_truncate_config_defaults():
    cfg = TruncateConfig()
    assert cfg.max_length == DEFAULT_MAX_LENGTH
    assert cfg.enabled is True


def test_truncate_config_rejects_tiny_max_length():
    with pytest.raises(ValueError, match="max_length must be at least"):
        TruncateConfig(max_length=2)


def test_truncate_config_accepts_minimum_valid_length():
    cfg = TruncateConfig(max_length=4)  # len("...") + 1
    assert cfg.max_length == 4


# ---------------------------------------------------------------------------
# truncate_value
# ---------------------------------------------------------------------------


def test_short_value_unchanged():
    assert truncate_value("hello") == "hello"


def test_value_at_exact_limit_unchanged():
    value = "x" * DEFAULT_MAX_LENGTH
    assert truncate_value(value) == value


def test_value_over_limit_is_truncated():
    value = "a" * (DEFAULT_MAX_LENGTH + 10)
    result = truncate_value(value)
    assert len(result) == DEFAULT_MAX_LENGTH
    assert result.endswith("...")


def test_truncation_disabled_leaves_long_value():
    cfg = TruncateConfig(max_length=10, enabled=False)
    value = "x" * 100
    assert truncate_value(value, cfg) == value


def test_custom_max_length():
    cfg = TruncateConfig(max_length=10)
    value = "hello world!"  # 12 chars
    result = truncate_value(value, cfg)
    assert len(result) == 10
    assert result.endswith("...")


def test_none_config_uses_defaults():
    short = "short"
    assert truncate_value(short, None) == short


# ---------------------------------------------------------------------------
# truncate_row_values
# ---------------------------------------------------------------------------


def test_truncate_row_values_short_values_unchanged():
    row = {"name": "Alice", "city": "Berlin"}
    assert truncate_row_values(row) == row


def test_truncate_row_values_long_values_truncated():
    cfg = TruncateConfig(max_length=10)
    row = {"col_a": "short", "col_b": "a very long value that exceeds limit"}
    result = truncate_row_values(row, cfg)
    assert result["col_a"] == "short"
    assert len(result["col_b"]) == 10
    assert result["col_b"].endswith("...")


def test_truncate_row_values_returns_new_dict():
    row = {"k": "v"}
    result = truncate_row_values(row)
    assert result is not row


def test_truncate_row_values_empty_row():
    assert truncate_row_values({}) == {}
