"""Deduplication utilities for CSV diff rows."""
from dataclasses import dataclass
from typing import List, Optional

from csvdiff.differ import DiffResult, RowDiff


@dataclass
class DeduplicateConfig:
    """Configuration for deduplication behaviour."""
    key_column: Optional[str] = None
    keep: str = "first"  # "first" or "last"

    def __post_init__(self) -> None:
        if self.keep not in ("first", "last"):
            raise ValueError(f"keep must be 'first' or 'last', got {self.keep!r}")


def _row_key(row: RowDiff, key_column: Optional[str]) -> object:
    """Return a hashable key for a RowDiff.

    When *key_column* is given the key is the cell value for that column in the
    'after' snapshot (falling back to 'before').  When no column is specified
    the row number is used so every row is considered unique.
    """
    if key_column is None:
        return row.row_number

    # Prefer the 'after' value; fall back to 'before' for removed rows.
    for cell in row.cells:
        if cell.column == key_column:
            value = cell.new_value if cell.new_value is not None else cell.old_value
            return value

    # Column not present in this row — fall back to row number.
    return row.row_number


def deduplicate_rows(
    rows: List[RowDiff],
    config: DeduplicateConfig,
) -> List[RowDiff]:
    """Remove duplicate RowDiff entries according to *config*.

    Rows that share the same key (as determined by :func:`_row_key`) are
    collapsed to a single entry.  The *keep* setting controls whether the
    first or last occurrence is retained.  Order of the surviving rows
    follows the original sequence.
    """
    seen: dict = {}
    for row in rows:
        key = _row_key(row, config.key_column)
        if config.keep == "first":
            if key not in seen:
                seen[key] = row
        else:  # "last"
            seen[key] = row

    # Preserve original ordering.
    if config.keep == "first":
        return list(seen.values())

    # For "last", re-order by first appearance of each key.
    order: List[object] = []
    for row in rows:
        key = _row_key(row, config.key_column)
        if key not in order:
            order.append(key)
    return [seen[k] for k in order]


def deduplicate_diff(result: DiffResult, config: DeduplicateConfig) -> DiffResult:
    """Return a new :class:`DiffResult` with duplicate rows removed."""
    deduped = deduplicate_rows(result.rows, config)
    return DiffResult(
        rows=deduped,
        headers=result.headers,
        file_a=result.file_a,
        file_b=result.file_b,
    )
