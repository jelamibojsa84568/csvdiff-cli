"""Context lines support: include N unchanged rows around each change."""
from dataclasses import dataclass, field
from typing import List
from csvdiff.differ import RowDiff, DiffResult


@dataclass
class ContextConfig:
    """Configuration for context lines around changes."""
    lines: int = 3

    def __post_init__(self) -> None:
        if self.lines < 0:
            raise ValueError("context lines must be >= 0")


def _changed_indices(rows: List[RowDiff]) -> List[int]:
    """Return indices of rows that have any change."""
    return [
        i for i, row in enumerate(rows)
        if row.added or row.removed or row.modified
    ]


def _context_indices(rows: List[RowDiff], config: ContextConfig) -> List[int]:
    """Return sorted unique indices of rows to show (changed + context)."""
    n = len(rows)
    indices: set = set()
    for ci in _changed_indices(rows):
        lo = max(0, ci - config.lines)
        hi = min(n - 1, ci + config.lines)
        for i in range(lo, hi + 1):
            indices.add(i)
    return sorted(indices)


def apply_context(result: DiffResult, config: ContextConfig) -> DiffResult:
    """Filter a DiffResult to only rows within context distance of a change.

    If config.lines is 0 and there are no changes, all rows are dropped.
    If the result has no rows, it is returned unchanged.
    """
    if not result.rows:
        return result

    kept_indices = _context_indices(result.rows, config)

    if not kept_indices:
        # No changes at all — return empty rows
        return DiffResult(headers=result.headers, rows=[])

    kept_rows = [result.rows[i] for i in kept_indices]
    return DiffResult(headers=result.headers, rows=kept_rows)
