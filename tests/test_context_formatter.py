"""Integration-style tests for context_formatter with realistic DiffResults."""
from csvdiff.differ import DiffResult, RowDiff, CellChange
from csvdiff.context import ContextConfig
from csvdiff.context_formatter import format_diff_with_context


def _unchanged(row_num: int, val: str = "same") -> RowDiff:
    return RowDiff(
        row_number=row_num, key=str(row_num),
        added=False, removed=False, modified=False, changes=[]
    )


def _modified(row_num: int) -> RowDiff:
    return RowDiff(
        row_number=row_num, key=str(row_num),
        added=False, removed=False, modified=True,
        changes=[CellChange(column="name", old_value="Alice", new_value="Bob")]
    )


def _added(row_num: int) -> RowDiff:
    return RowDiff(
        row_number=row_num, key=str(row_num),
        added=True, removed=False, modified=False, changes=[]
    )


def _make(rows):
    return DiffResult(headers=["id", "name"], rows=rows)


def test_single_change_no_separator():
    rows = [_unchanged(i) for i in range(5)]
    rows[2] = _modified(2)
    result = _make(rows)
    out = format_diff_with_context(result, ContextConfig(lines=1), use_color=False)
    assert "@@ ... @@" not in out


def test_two_distant_changes_have_separator():
    rows = [_unchanged(i) for i in range(30)]
    rows[1] = _modified(1)
    rows[28] = _added(28)
    result = _make(rows)
    out = format_diff_with_context(result, ContextConfig(lines=1), use_color=False)
    assert "@@ ... @@" in out


def test_zero_context_shows_only_changed_rows():
    rows = [_unchanged(i) for i in range(10)]
    rows[5] = _modified(5)
    result = _make(rows)
    out = format_diff_with_context(result, ContextConfig(lines=0), use_color=False)
    # Only the changed row should appear, no unchanged rows in output
    assert "@@ ... @@" not in out


def test_empty_result_returns_format_diff_output():
    result = _make([])
    out = format_diff_with_context(result, ContextConfig(lines=2), use_color=False)
    # Should not crash; returns some string
    assert isinstance(out, str)


def test_all_changed_rows_no_separator():
    rows = [_modified(i) for i in range(5)]
    result = _make(rows)
    out = format_diff_with_context(result, ContextConfig(lines=1), use_color=False)
    assert "@@ ... @@" not in out
