"""Formatter that renders diffs with context-line separators."""
from typing import List
from csvdiff.differ import RowDiff, DiffResult
from csvdiff.context import ContextConfig, _context_indices
from csvdiff.formatter import format_diff

_SEPARATOR = "@@ ... @@"


def _contiguous_groups(indices: List[int]) -> List[List[int]]:
    """Split a sorted list of indices into contiguous runs."""
    if not indices:
        return []
    groups: List[List[int]] = []
    current = [indices[0]]
    for idx in indices[1:]:
        if idx == current[-1] + 1:
            current.append(idx)
        else:
            groups.append(current)
            current = [idx]
    groups.append(current)
    return groups


def format_diff_with_context(
    result: DiffResult,
    config: ContextConfig,
    use_color: bool = True,
) -> str:
    """Format a DiffResult, grouping context blocks with @@ separators.

    Unchanged rows outside the context window are replaced with a
    separator line so the reader can see where content was omitted.
    """
    if not result.rows:
        return format_diff(result, use_color=use_color)

    kept_indices = _context_indices(result.rows, config)
    if not kept_indices:
        return "(no changes)"

    groups = _contiguous_groups(kept_indices)
    parts: List[str] = []

    for group_num, group in enumerate(groups):
        if group_num > 0:
            parts.append(_SEPARATOR)
        group_rows = [result.rows[i] for i in group]
        sub_result = DiffResult(headers=result.headers, rows=group_rows)
        parts.append(format_diff(sub_result, use_color=use_color))

    return "\n".join(parts)
