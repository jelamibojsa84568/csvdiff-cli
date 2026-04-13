"""Tests for csvdiff.highlight_formatter."""
from csvdiff.differ import CellChange, DiffResult, RowDiff
from csvdiff.highlight_formatter import format_diff_highlighted
from csvdiff.highlighter import HighlightConfig


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _modified_row(row_num: int, col: str, old: str, new: str) -> RowDiff:
    return RowDiff(
        row_number=row_num,
        status="modified",
        row_a={col: old},
        row_b={col: new},
        changes=[CellChange(column=col, old_value=old, new_value=new)],
    )


def _added_row(row_num: int) -> RowDiff:
    return RowDiff(
        row_number=row_num,
        status="added",
        row_a=None,
        row_b={"name": "Eve"},
        changes=[],
    )


def _removed_row(row_num: int) -> RowDiff:
    return RowDiff(
        row_number=row_num,
        status="removed",
        row_a={"name": "Bob"},
        row_b=None,
        changes=[],
    )


def _unchanged_row(row_num: int) -> RowDiff:
    return RowDiff(
        row_number=row_num,
        status="unchanged",
        row_a={"name": "Carol"},
        row_b={"name": "Carol"},
        changes=[],
    )


def _make_result(*rows: RowDiff) -> DiffResult:
    return DiffResult(rows=list(rows), headers=["name"])


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_no_differences_returns_message():
    result = _make_result(_unchanged_row(1))
    output = format_diff_highlighted(result)
    assert output == "No differences found."


def test_added_row_present_in_output():
    result = _make_result(_added_row(2))
    output = format_diff_highlighted(result)
    assert "row 2" in output
    assert "Eve" in output


def test_removed_row_present_in_output():
    result = _make_result(_removed_row(3))
    output = format_diff_highlighted(result)
    assert "row 3" in output
    assert "Bob" in output


def test_modified_row_contains_column_and_values():
    result = _make_result(_modified_row(1, "price", "100", "200"))
    output = format_diff_highlighted(result)
    assert "price" in output
    assert "100" in output
    assert "200" in output


def test_unchanged_rows_hidden_by_default():
    result = _make_result(_unchanged_row(1), _modified_row(2, "x", "a", "b"))
    output = format_diff_highlighted(result)
    assert "Carol" not in output


def test_show_unchanged_includes_unchanged_rows():
    result = _make_result(_unchanged_row(1))
    output = format_diff_highlighted(result, show_unchanged=True)
    assert "Carol" in output


def test_highlighting_disabled_still_shows_diff():
    cfg = HighlightConfig(enabled=False)
    result = _make_result(_modified_row(1, "col", "old_value", "new_value"))
    output = format_diff_highlighted(result, config=cfg)
    assert "old_value" in output
    assert "new_value" in output
