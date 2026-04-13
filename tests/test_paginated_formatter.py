"""Tests for csvdiff.paginated_formatter."""
from typing import Dict, List

import pytest

from csvdiff.differ import CellChange, DiffResult, RowDiff
from csvdiff.paginated_formatter import PaginatedFormatConfig, format_diff_paginated


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _modified_row(row_num: int, col: str, old: str, new: str) -> RowDiff:
    return RowDiff(
        row_number=row_num,
        added=False,
        removed=False,
        cells=[CellChange(column=col, old_value=old, new_value=new)],
        key=str(row_num),
    )


def _unchanged_row(row_num: int) -> RowDiff:
    return RowDiff(row_number=row_num, added=False, removed=False, cells=[], key=str(row_num))


def _make_result(rows: List[RowDiff]) -> DiffResult:
    return DiffResult(rows=rows, headers_a=["id", "name"], headers_b=["id", "name"])


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_format_shows_page_summary():
    rows = [_modified_row(i, "name", "old", "new") for i in range(1, 6)]
    result = _make_result(rows)
    cfg = PaginatedFormatConfig(page_size=10, page=1, color=False)
    output = format_diff_paginated(result, ["id", "name"], cfg)
    assert "Page 1 of 1" in output
    assert "5 total item(s)" in output


def test_format_paginates_correctly():
    rows = [_modified_row(i, "name", "old", "new") for i in range(1, 12)]
    result = _make_result(rows)
    cfg = PaginatedFormatConfig(page_size=5, page=2, color=False)
    output = format_diff_paginated(result, ["id", "name"], cfg)
    assert "Page 2 of 3" in output


def test_unchanged_rows_excluded_from_pages():
    rows = [
        _unchanged_row(1),
        _modified_row(2, "name", "a", "b"),
        _unchanged_row(3),
    ]
    result = _make_result(rows)
    cfg = PaginatedFormatConfig(page_size=10, page=1, color=False)
    output = format_diff_paginated(result, ["id", "name"], cfg)
    # Only 1 changed row counted
    assert "1 total item(s)" in output


def test_empty_diff_returns_page_1_of_1():
    result = _make_result([])
    cfg = PaginatedFormatConfig(page_size=10, page=1, color=False)
    output = format_diff_paginated(result, ["id", "name"], cfg)
    assert "Page 1 of 1" in output
    assert "0 total item(s)" in output
