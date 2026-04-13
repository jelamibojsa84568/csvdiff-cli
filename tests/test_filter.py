"""Tests for csvdiff.filter module."""

import pytest

from csvdiff.filter import (
    FilterConfig,
    apply_column_filter,
    filter_row,
    filter_rows,
)


HEADERS = ["id", "name", "email", "age"]


# ---------------------------------------------------------------------------
# FilterConfig
# ---------------------------------------------------------------------------

def test_filter_config_defaults():
    cfg = FilterConfig()
    assert cfg.include_columns == []
    assert cfg.exclude_columns == []
    assert cfg.key_column is None


def test_filter_config_rejects_both_include_and_exclude():
    with pytest.raises(ValueError, match="Cannot specify both"):
        FilterConfig(include_columns=["id"], exclude_columns=["age"])


# ---------------------------------------------------------------------------
# apply_column_filter
# ---------------------------------------------------------------------------

def test_apply_no_filter_returns_all_headers():
    cfg = FilterConfig()
    assert apply_column_filter(HEADERS, cfg) == HEADERS


def test_apply_include_columns():
    cfg = FilterConfig(include_columns=["id", "name"])
    result = apply_column_filter(HEADERS, cfg)
    assert result == ["id", "name"]


def test_apply_exclude_columns():
    cfg = FilterConfig(exclude_columns=["email", "age"])
    result = apply_column_filter(HEADERS, cfg)
    assert result == ["id", "name"]


def test_key_column_preserved_when_excluded():
    """Key column must survive even if it appears in exclude_columns."""
    cfg = FilterConfig(exclude_columns=["id", "age"], key_column="id")
    result = apply_column_filter(HEADERS, cfg)
    assert "id" in result


def test_key_column_added_when_missing_from_include():
    cfg = FilterConfig(include_columns=["name"], key_column="id")
    result = apply_column_filter(HEADERS, cfg)
    assert result[0] == "id"
    assert "name" in result


def test_unknown_key_column_not_added():
    """A key_column not present in headers should be silently ignored."""
    cfg = FilterConfig(key_column="nonexistent")
    result = apply_column_filter(HEADERS, cfg)
    assert "nonexistent" not in result


# ---------------------------------------------------------------------------
# filter_row / filter_rows
# ---------------------------------------------------------------------------

def test_filter_row_keeps_allowed_columns():
    row = {"id": "1", "name": "Alice", "email": "a@b.com", "age": "30"}
    result = filter_row(row, ["id", "name"])
    assert result == {"id": "1", "name": "Alice"}


def test_filter_row_empty_allowed():
    row = {"id": "1", "name": "Alice"}
    assert filter_row(row, []) == {}


def test_filter_rows_applies_to_all():
    rows = [
        {"id": "1", "name": "Alice", "age": "30"},
        {"id": "2", "name": "Bob", "age": "25"},
    ]
    result = filter_rows(rows, ["id", "name"])
    assert all("age" not in r for r in result)
    assert len(result) == 2
