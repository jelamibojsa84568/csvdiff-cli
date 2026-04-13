"""Core diffing logic for csvdiff-cli."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CellChange:
    column: str
    old_value: str
    new_value: str


@dataclass
class RowDiff:
    key: str
    change_type: str  # 'added' | 'removed' | 'modified'
    cell_changes: List[CellChange] = field(default_factory=list)


@dataclass
class DiffResult:
    key_column: str
    added: List[RowDiff] = field(default_factory=list)
    removed: List[RowDiff] = field(default_factory=list)
    modified: List[RowDiff] = field(default_factory=list)
    columns_only_in_a: List[str] = field(default_factory=list)
    columns_only_in_b: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.modified)

    @property
    def total_changes(self) -> int:
        return len(self.added) + len(self.removed) + len(self.modified)


def diff_csvs(
    parsed_a: Dict,
    parsed_b: Dict,
    ignore_columns: Optional[List[str]] = None,
) -> DiffResult:
    """
    Compare two parsed CSV structures and return a DiffResult.

    Args:
        parsed_a: Output of parser.load_csv for file A (baseline).
        parsed_b: Output of parser.load_csv for file B (changed).
        ignore_columns: Column names to exclude from comparison.

    Returns:
        A DiffResult describing all row-level and cell-level changes.
    """
    ignore = set(ignore_columns or [])
    key = parsed_a["key"]

    headers_a = set(parsed_a["headers"]) - ignore
    headers_b = set(parsed_b["headers"]) - ignore
    compare_cols = (headers_a & headers_b) - {key}

    result = DiffResult(
        key_column=key,
        columns_only_in_a=sorted(headers_a - headers_b),
        columns_only_in_b=sorted(headers_b - headers_a),
    )

    rows_a: Dict[str, Dict] = parsed_a["rows"]
    rows_b: Dict[str, Dict] = parsed_b["rows"]

    keys_a = set(rows_a.keys())
    keys_b = set(rows_b.keys())

    for k in sorted(keys_a - keys_b):
        result.removed.append(RowDiff(key=k, change_type="removed"))

    for k in sorted(keys_b - keys_a):
        result.added.append(RowDiff(key=k, change_type="added"))

    for k in sorted(keys_a & keys_b):
        changes = []
        for col in sorted(compare_cols):
            val_a = rows_a[k].get(col, "")
            val_b = rows_b[k].get(col, "")
            if val_a != val_b:
                changes.append(CellChange(column=col, old_value=val_a, new_value=val_b))
        if changes:
            result.modified.append(
                RowDiff(key=k, change_type="modified", cell_changes=changes)
            )

    return result
