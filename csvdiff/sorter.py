"""Sorting utilities for CSV diff rows and results."""

from __future__ import annotations

from enum import Enum
from typing import List

from csvdiff.differ import DiffResult, RowDiff


class SortKey(str, Enum):
    ROW_NUMBER = "row"
    KEY = "key"
    CHANGE_TYPE = "type"
    CHANGE_COUNT = "count"


_CHANGE_TYPE_ORDER = {"removed": 0, "added": 1, "modified": 2, "identical": 3}


def _row_sort_key(row_diff: RowDiff, key: SortKey):
    """Return a sortable value for a RowDiff based on the requested key."""
    if key == SortKey.ROW_NUMBER:
        # Use the minimum row number across both sides (None treated as large)
        a = row_diff.row_index_a if row_diff.row_index_a is not None else 10**9
        b = row_diff.row_index_b if row_diff.row_index_b is not None else 10**9
        return min(a, b)
    if key == SortKey.KEY:
        return str(row_diff.key) if row_diff.key is not None else ""
    if key == SortKey.CHANGE_TYPE:
        return _CHANGE_TYPE_ORDER.get(row_diff.change_type, 99)
    if key == SortKey.CHANGE_COUNT:
        return len(row_diff.cell_changes)
    raise ValueError(f"Unknown sort key: {key}")


def sort_rows(
    rows: List[RowDiff],
    key: SortKey = SortKey.ROW_NUMBER,
    reverse: bool = False,
) -> List[RowDiff]:
    """Return a new sorted list of RowDiff objects."""
    return sorted(rows, key=lambda r: _row_sort_key(r, key), reverse=reverse)


def sort_diff_result(
    result: DiffResult,
    key: SortKey = SortKey.ROW_NUMBER,
    reverse: bool = False,
) -> DiffResult:
    """Return a new DiffResult with rows sorted according to *key*."""
    sorted_rows = sort_rows(result.rows, key=key, reverse=reverse)
    return DiffResult(
        headers=result.headers,
        rows=sorted_rows,
        key_column=result.key_column,
    )
