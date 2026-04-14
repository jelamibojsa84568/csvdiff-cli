"""Compute per-column statistics from a DiffResult."""
from __future__ import annotations

from dataclasses import dataclass, field
from collections import defaultdict
from typing import Dict

from csvdiff.differ import DiffResult, RowDiff


@dataclass
class ColumnStats:
    """Statistics for a single column across all diffed rows."""
    column: str
    changed: int = 0
    added: int = 0
    removed: int = 0

    @property
    def total(self) -> int:
        return self.changed + self.added + self.removed

    def __str__(self) -> str:  # pragma: no cover
        return (
            f"{self.column}: changed={self.changed}, "
            f"added={self.added}, removed={self.removed}"
        )


@dataclass
class DiffStats:
    """Aggregated statistics for an entire diff."""
    total_rows_compared: int = 0
    rows_added: int = 0
    rows_removed: int = 0
    rows_modified: int = 0
    rows_unchanged: int = 0
    column_stats: Dict[str, ColumnStats] = field(default_factory=dict)

    @property
    def rows_with_changes(self) -> int:
        return self.rows_added + self.rows_removed + self.rows_modified


def compute_stats(result: DiffResult) -> DiffStats:
    """Compute statistics from a DiffResult."""
    stats = DiffStats()
    col_counts: Dict[str, ColumnStats] = defaultdict(
        lambda: ColumnStats(column="")
    )

    for row in result.rows:
        stats.total_rows_compared += 1

        if row.is_added:
            stats.rows_added += 1
            for col in result.headers:
                col_counts[col].column = col
                col_counts[col].added += 1

        elif row.is_removed:
            stats.rows_removed += 1
            for col in result.headers:
                col_counts[col].column = col
                col_counts[col].removed += 1

        elif row.changes:
            stats.rows_modified += 1
            for change in row.changes:
                col_counts[change.column].column = change.column
                col_counts[change.column].changed += 1

        else:
            stats.rows_unchanged += 1

    stats.column_stats = dict(col_counts)
    return stats
