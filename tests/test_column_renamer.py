"""Tests for csvdiff.column_renamer."""
import pytest
from csvdiff.column_renamer import RenameConfig, rename_rows, rename_headers


# ---------------------------------------------------------------------------
# RenameConfig construction
# ---------------------------------------------------------------------------

def test_rename_config_defaults():
    cfg = RenameConfig()
    assert cfg.rename_map == {}
    assert cfg.is_empty()


def test_rename_config_accepts_valid_map():
    cfg = RenameConfig(rename_map={"old_name": "new_name"})
    assert not cfg.is_empty()


def test_rename_config_rejects_non_dict():
    with pytest.raises(TypeError):
        RenameConfig(rename_map=[("a", "b")])  # type: ignore[arg-type]


def test_rename_config_rejects_empty_source_key():
    with pytest.raises(ValueError):
        RenameConfig(rename_map={"": "target"})


def test_rename_config_rejects_blank_target_value():
    with pytest.raises(ValueError):
        RenameConfig(rename_map={"source": "   "})


# ---------------------------------------------------------------------------
# apply_to_headers
# ---------------------------------------------------------------------------

def test_apply_to_headers_renames_known_column():
    cfg = RenameConfig(rename_map={"fname": "first_name"})
    result = cfg.apply_to_headers(["fname", "lname", "age"])
    assert result == ["first_name", "lname", "age"]


def test_apply_to_headers_leaves_unknown_columns_unchanged():
    cfg = RenameConfig(rename_map={"x": "y"})
    headers = ["a", "b", "c"]
    assert cfg.apply_to_headers(headers) == headers


# ---------------------------------------------------------------------------
# apply_to_row
# ---------------------------------------------------------------------------

def test_apply_to_row_renames_key():
    cfg = RenameConfig(rename_map={"qty": "quantity"})
    row = {"qty": "5", "price": "9.99"}
    assert cfg.apply_to_row(row) == {"quantity": "5", "price": "9.99"}


def test_apply_to_row_preserves_values():
    cfg = RenameConfig(rename_map={"a": "b"})
    row = {"a": "hello"}
    result = cfg.apply_to_row(row)
    assert result["b"] == "hello"


# ---------------------------------------------------------------------------
# reverse
# ---------------------------------------------------------------------------

def test_reverse_swaps_map():
    cfg = RenameConfig(rename_map={"old": "new"})
    rev = cfg.reverse()
    assert rev.rename_map == {"new": "old"}


# ---------------------------------------------------------------------------
# rename_rows helper
# ---------------------------------------------------------------------------

def test_rename_rows_applies_to_all_rows():
    cfg = RenameConfig(rename_map={"col_a": "column_a"})
    rows = [{"col_a": "1"}, {"col_a": "2"}]
    result = rename_rows(rows, cfg)
    assert all("column_a" in r for r in result)
    assert all("col_a" not in r for r in result)


def test_rename_rows_empty_config_returns_same_list():
    cfg = RenameConfig()
    rows = [{"a": "1"}]
    assert rename_rows(rows, cfg) is rows


# ---------------------------------------------------------------------------
# rename_headers helper
# ---------------------------------------------------------------------------

def test_rename_headers_empty_config_returns_same_list():
    cfg = RenameConfig()
    headers = ["a", "b"]
    assert rename_headers(headers, cfg) is headers


def test_rename_headers_applies_map():
    cfg = RenameConfig(rename_map={"id": "identifier"})
    assert rename_headers(["id", "name"], cfg) == ["identifier", "name"]
