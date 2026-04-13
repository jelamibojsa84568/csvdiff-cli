"""Tests for csvdiff.reporter."""

import io
import pytest

from csvdiff.differ import CellChange, RowDiff, DiffResult
from csvdiff.reporter import build_summary, print_summary, exit_code, DiffSummary


def _make_result(rows):
    return DiffResult(rows=rows, headers=["id", "name", "age"])


def _modified_row(key, changes):
    return RowDiff(
        key=key,
        status="modified",
        changes=changes,
        old_row={},
        new_row={},
    )


def _added_row(key):
    return RowDiff(key=key, status="added", changes=[], old_row={}, new_row={})


def _removed_row(key):
    return RowDiff(key=key, status="removed", changes=[], old_row={}, new_row={})


def test_summary_identical():
    result = _make_result([])
    summary = build_summary(result)
    assert summary.files_identical is True
    assert str(summary) == "Files are identical."


def test_summary_added_rows():
    result = _make_result([_added_row("1"), _added_row("2")])
    summary = build_summary(result)
    assert summary.rows_added == 2
    assert summary.rows_removed == 0
    assert summary.rows_modified == 0
    assert summary.files_identical is False
    assert "2 row(s) added" in str(summary)


def test_summary_removed_rows():
    result = _make_result([_removed_row("3")])
    summary = build_summary(result)
    assert summary.rows_removed == 1
    assert "1 row(s) removed" in str(summary)


def test_summary_modified_rows():
    changes = [CellChange(column="name", old_value="Alice", new_value="Bob")]
    result = _make_result([_modified_row("1", changes)])
    summary = build_summary(result)
    assert summary.rows_modified == 1
    assert summary.total_cell_changes == 1
    assert "1 row(s) modified" in str(summary)
    assert "1 cell change(s)" in str(summary)


def test_print_summary_writes_to_stream():
    result = _make_result([_added_row("5")])
    buf = io.StringIO()
    print_summary(result, stream=buf)
    output = buf.getvalue()
    assert "added" in output
    assert output.endswith("\n")


def test_exit_code_identical():
    result = _make_result([])
    assert exit_code(result) == 0


def test_exit_code_differs():
    result = _make_result([_added_row("1")])
    assert exit_code(result) == 1
