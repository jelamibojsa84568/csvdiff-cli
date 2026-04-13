"""Tests for csvdiff.deduplicator."""
import pytest

from csvdiff.differ import CellChange, DiffResult, RowDiff
from csvdiff.deduplicator import DeduplicateConfig, deduplicate_rows, deduplicate_diff


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _row(row_number: int, key_value: str = "k") -> RowDiff:
    cell = CellChange(column="id", old_value=key_value, new_value=key_value)
    return RowDiff(row_number=row_number, change_type="modified", cells=[cell])


def _make_result(rows):
    return DiffResult(
        rows=rows,
        headers=["id", "name"],
        file_a="a.csv",
        file_b="b.csv",
    )


# ---------------------------------------------------------------------------
# DeduplicateConfig
# ---------------------------------------------------------------------------

def test_config_defaults():
    cfg = DeduplicateConfig()
    assert cfg.key_column is None
    assert cfg.keep == "first"


def test_config_rejects_invalid_keep():
    with pytest.raises(ValueError, match="keep must be"):
        DeduplicateConfig(keep="middle")


def test_config_accepts_last():
    cfg = DeduplicateConfig(keep="last")
    assert cfg.keep == "last"


# ---------------------------------------------------------------------------
# deduplicate_rows — no key column (row_number used)
# ---------------------------------------------------------------------------

def test_no_duplicates_unchanged():
    rows = [_row(1), _row(2), _row(3)]
    cfg = DeduplicateConfig()
    result = deduplicate_rows(rows, cfg)
    assert [r.row_number for r in result] == [1, 2, 3]


def test_empty_rows():
    cfg = DeduplicateConfig()
    assert deduplicate_rows([], cfg) == []


# ---------------------------------------------------------------------------
# deduplicate_rows — with key_column
# ---------------------------------------------------------------------------

def test_keep_first_removes_later_duplicates():
    rows = [_row(1, "A"), _row(2, "A"), _row(3, "B")]
    cfg = DeduplicateConfig(key_column="id", keep="first")
    result = deduplicate_rows(rows, cfg)
    assert len(result) == 2
    assert result[0].row_number == 1
    assert result[1].row_number == 3


def test_keep_last_removes_earlier_duplicates():
    rows = [_row(1, "A"), _row(2, "A"), _row(3, "B")]
    cfg = DeduplicateConfig(key_column="id", keep="last")
    result = deduplicate_rows(rows, cfg)
    assert len(result) == 2
    assert result[0].row_number == 2
    assert result[1].row_number == 3


def test_order_preserved_keep_first():
    rows = [_row(3, "X"), _row(1, "Y"), _row(2, "X")]
    cfg = DeduplicateConfig(key_column="id", keep="first")
    result = deduplicate_rows(rows, cfg)
    assert [r.row_number for r in result] == [3, 1]


def test_order_preserved_keep_last():
    rows = [_row(3, "X"), _row(1, "Y"), _row(2, "X")]
    cfg = DeduplicateConfig(key_column="id", keep="last")
    result = deduplicate_rows(rows, cfg)
    assert [r.row_number for r in result] == [2, 1]


# ---------------------------------------------------------------------------
# deduplicate_diff
# ---------------------------------------------------------------------------

def test_deduplicate_diff_returns_diff_result():
    rows = [_row(1, "A"), _row(2, "A")]
    original = _make_result(rows)
    cfg = DeduplicateConfig(key_column="id", keep="first")
    result = deduplicate_diff(original, cfg)
    assert isinstance(result, DiffResult)
    assert len(result.rows) == 1
    assert result.headers == original.headers
    assert result.file_a == original.file_a
    assert result.file_b == original.file_b
