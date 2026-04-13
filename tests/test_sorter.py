"""Tests for csvdiff.sorter."""

from __future__ import annotations

import pytest

from csvdiff.differ import CellChange, DiffResult, RowDiff
from csvdiff.sorter import SortKey, sort_diff_result, sort_rows


HEADERS = ["id", "name", "score"]


def _make_row(
    key,
    change_type: str,
    n_changes: int = 0,
    row_index_a: int | None = None,
    row_index_b: int | None = None,
) -> RowDiff:
    changes = [
        CellChange(column=f"col{i}", old_value="x", new_value="y")
        for i in range(n_changes)
    ]
    return RowDiff(
        key=key,
        change_type=change_type,
        cell_changes=changes,
        row_index_a=row_index_a,
        row_index_b=row_index_b,
    )


@pytest.fixture()
def sample_rows() -> list[RowDiff]:
    return [
        _make_row("c", "modified", n_changes=3, row_index_a=2, row_index_b=2),
        _make_row("a", "removed", row_index_a=0),
        _make_row("b", "added", row_index_b=1),
        _make_row("d", "identical", row_index_a=3, row_index_b=3),
    ]


def test_sort_by_row_number(sample_rows):
    result = sort_rows(sample_rows, key=SortKey.ROW_NUMBER)
    indices = [min(r.row_index_a or 10**9, r.row_index_b or 10**9) for r in result]
    assert indices == sorted(indices)


def test_sort_by_key(sample_rows):
    result = sort_rows(sample_rows, key=SortKey.KEY)
    keys = [r.key for r in result]
    assert keys == ["a", "b", "c", "d"]


def test_sort_by_change_type(sample_rows):
    result = sort_rows(sample_rows, key=SortKey.CHANGE_TYPE)
    types = [r.change_type for r in result]
    assert types == ["removed", "added", "modified", "identical"]


def test_sort_by_change_count(sample_rows):
    result = sort_rows(sample_rows, key=SortKey.CHANGE_COUNT)
    counts = [len(r.cell_changes) for r in result]
    assert counts == sorted(counts)


def test_sort_reverse(sample_rows):
    asc = sort_rows(sample_rows, key=SortKey.KEY)
    desc = sort_rows(sample_rows, key=SortKey.KEY, reverse=True)
    assert [r.key for r in desc] == [r.key for r in reversed(asc)]


def test_sort_diff_result_returns_new_object(sample_rows):
    diff = DiffResult(headers=HEADERS, rows=sample_rows, key_column="id")
    sorted_diff = sort_diff_result(diff, key=SortKey.KEY)
    assert sorted_diff is not diff
    assert sorted_diff.headers == HEADERS
    assert sorted_diff.key_column == "id"
    assert [r.key for r in sorted_diff.rows] == ["a", "b", "c", "d"]


def test_sort_empty_rows():
    diff = DiffResult(headers=HEADERS, rows=[], key_column="id")
    sorted_diff = sort_diff_result(diff)
    assert sorted_diff.rows == []


def test_invalid_sort_key_raises():
    row = _make_row("x", "identical", row_index_a=0, row_index_b=0)
    with pytest.raises((ValueError, AttributeError)):
        sort_rows([row], key="invalid")  # type: ignore[arg-type]
