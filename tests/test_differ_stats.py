"""Tests for differ_stats and stats_formatter."""
from __future__ import annotations

import pytest

from csvdiff.differ import CellChange, RowDiff, DiffResult
from csvdiff.differ_stats import ColumnStats, DiffStats, compute_stats
from csvdiff.stats_formatter import format_stats


HEADERS = ["id", "name", "score"]


def _unchanged(row_num: int) -> RowDiff:
    return RowDiff(row_number=row_num, is_added=False, is_removed=False, changes=[])


def _added(row_num: int) -> RowDiff:
    return RowDiff(row_number=row_num, is_added=True, is_removed=False, changes=[])


def _removed(row_num: int) -> RowDiff:
    return RowDiff(row_number=row_num, is_added=False, is_removed=True, changes=[])


def _modified(row_num: int, *cols: str) -> RowDiff:
    changes = [CellChange(column=c, old_value="a", new_value="b") for c in cols]
    return RowDiff(row_number=row_num, is_added=False, is_removed=False, changes=changes)


def _make_result(*rows: RowDiff) -> DiffResult:
    return DiffResult(headers=HEADERS, rows=list(rows))


# --- compute_stats ---

def test_empty_result():
    stats = compute_stats(_make_result())
    assert stats.total_rows_compared == 0
    assert stats.rows_with_changes == 0
    assert stats.column_stats == {}


def test_all_unchanged():
    stats = compute_stats(_make_result(_unchanged(1), _unchanged(2)))
    assert stats.rows_unchanged == 2
    assert stats.rows_modified == 0
    assert stats.rows_added == 0
    assert stats.rows_removed == 0


def test_added_rows_count():
    stats = compute_stats(_make_result(_added(1), _added(2)))
    assert stats.rows_added == 2
    assert stats.total_rows_compared == 2


def test_removed_rows_count():
    stats = compute_stats(_make_result(_removed(1)))
    assert stats.rows_removed == 1


def test_modified_rows_count():
    stats = compute_stats(_make_result(_modified(1, "name"), _modified(2, "score")))
    assert stats.rows_modified == 2


def test_column_stats_modified():
    stats = compute_stats(
        _make_result(
            _modified(1, "name", "score"),
            _modified(2, "name"),
        )
    )
    assert stats.column_stats["name"].changed == 2
    assert stats.column_stats["score"].changed == 1


def test_column_stats_added_covers_all_headers():
    stats = compute_stats(_make_result(_added(1)))
    for col in HEADERS:
        assert col in stats.column_stats
        assert stats.column_stats[col].added == 1


def test_column_stats_removed_covers_all_headers():
    stats = compute_stats(_make_result(_removed(1)))
    for col in HEADERS:
        assert stats.column_stats[col].removed == 1


def test_rows_with_changes_property():
    stats = compute_stats(
        _make_result(_added(1), _removed(2), _modified(3, "id"), _unchanged(4))
    )
    assert stats.rows_with_changes == 3


# --- ColumnStats helpers ---

def test_column_stats_total():
    cs = ColumnStats(column="x", changed=3, added=1, removed=2)
    assert cs.total == 6


# --- format_stats ---

def test_format_stats_contains_header():
    stats = compute_stats(_make_result())
    output = format_stats(stats, color=False)
    assert "Diff Statistics" in output


def test_format_stats_shows_counts():
    stats = compute_stats(_make_result(_added(1), _removed(2), _modified(3, "name")))
    output = format_stats(stats, color=False)
    assert "added    : 1" in output
    assert "removed  : 1" in output
    assert "modified : 1" in output


def test_format_stats_column_section():
    stats = compute_stats(_make_result(_modified(1, "score")))
    output = format_stats(stats, color=False)
    assert "score" in output
    assert "modified=1" in output


def test_format_stats_no_color_no_escape_codes():
    stats = compute_stats(_make_result(_added(1)))
    output = format_stats(stats, color=False)
    assert "\033[" not in output
