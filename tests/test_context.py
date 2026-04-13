"""Tests for csvdiff.context and csvdiff.context_formatter."""
import pytest
from csvdiff.differ import DiffResult, RowDiff, CellChange
from csvdiff.context import ContextConfig, _changed_indices, _context_indices, apply_context
from csvdiff.context_formatter import format_diff_with_context, _contiguous_groups


def _unchanged(row_num: int) -> RowDiff:
    return RowDiff(row_number=row_num, key=str(row_num), added=False, removed=False, modified=False, changes=[])


def _modified(row_num: int) -> RowDiff:
    change = CellChange(column="a", old_value="x", new_value="y")
    return RowDiff(row_number=row_num, key=str(row_num), added=False, removed=False, modified=True, changes=[change])


def _make_result(rows):
    return DiffResult(headers=["a"], rows=rows)


def test_context_config_defaults():
    cfg = ContextConfig()
    assert cfg.lines == 3


def test_context_config_rejects_negative():
    with pytest.raises(ValueError):
        ContextConfig(lines=-1)


def test_context_config_zero_allowed():
    cfg = ContextConfig(lines=0)
    assert cfg.lines == 0


def test_changed_indices_none():
    rows = [_unchanged(i) for i in range(5)]
    assert _changed_indices(rows) == []


def test_changed_indices_some():
    rows = [_unchanged(0), _modified(1), _unchanged(2), _modified(3)]
    assert _changed_indices(rows) == [1, 3]


def test_context_indices_with_context():
    rows = [_unchanged(i) for i in range(10)]
    rows[5] = _modified(5)
    cfg = ContextConfig(lines=2)
    indices = _context_indices(rows, cfg)
    assert indices == [3, 4, 5, 6, 7]


def test_context_indices_clamps_to_bounds():
    rows = [_modified(0)] + [_unchanged(i) for i in range(1, 4)]
    cfg = ContextConfig(lines=3)
    indices = _context_indices(rows, cfg)
    assert 0 in indices
    assert max(indices) <= 3


def test_apply_context_no_changes_returns_empty():
    rows = [_unchanged(i) for i in range(5)]
    result = _make_result(rows)
    out = apply_context(result, ContextConfig(lines=1))
    assert out.rows == []


def test_apply_context_keeps_nearby_rows():
    rows = [_unchanged(i) for i in range(10)]
    rows[7] = _modified(7)
    result = _make_result(rows)
    out = apply_context(result, ContextConfig(lines=1))
    row_nums = [r.row_number for r in out.rows]
    assert 6 in row_nums
    assert 7 in row_nums
    assert 8 in row_nums
    assert 0 not in row_nums


def test_apply_context_empty_result():
    result = _make_result([])
    out = apply_context(result, ContextConfig(lines=2))
    assert out.rows == []


def test_contiguous_groups_single():
    assert _contiguous_groups([1, 2, 3]) == [[1, 2, 3]]


def test_contiguous_groups_split():
    assert _contiguous_groups([1, 2, 5, 6]) == [[1, 2], [5, 6]]


def test_format_diff_with_context_no_changes():
    rows = [_unchanged(i) for i in range(3)]
    result = _make_result(rows)
    out = format_diff_with_context(result, ContextConfig(lines=1), use_color=False)
    assert out == "(no changes)"


def test_format_diff_with_context_separator_between_groups():
    rows = [_unchanged(i) for i in range(20)]
    rows[2] = _modified(2)
    rows[18] = _modified(18)
    result = _make_result(rows)
    out = format_diff_with_context(result, ContextConfig(lines=1), use_color=False)
    assert "@@ ... @@" in out
