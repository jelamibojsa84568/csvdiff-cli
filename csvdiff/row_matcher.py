"""Row matching strategies for aligning rows between two CSV files."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


class MatchError(Exception):
    """Raised when a match configuration is invalid."""


@dataclass
class MatchConfig:
    """Configuration for row matching strategy."""
    key_columns: List[str] = field(default_factory=list)
    ignore_case: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.key_columns, list):
            raise MatchError("key_columns must be a list")
        for col in self.key_columns:
            if not isinstance(col, str) or not col.strip():
                raise MatchError("Each key column must be a non-empty string")

    @property
    def has_keys(self) -> bool:
        return len(self.key_columns) > 0


def _row_key(row: Dict[str, str], key_columns: List[str], ignore_case: bool) -> Tuple[str, ...]:
    """Extract a composite key tuple from a row."""
    parts = []
    for col in key_columns:
        val = row.get(col, "")
        if ignore_case:
            val = val.lower()
        parts.append(val)
    return tuple(parts)


def build_key_index(
    rows: List[Dict[str, str]],
    config: MatchConfig,
) -> Dict[Tuple[str, ...], int]:
    """Build a mapping from key tuple to row index for fast lookup.

    If duplicate keys exist, the last occurrence wins.
    """
    index: Dict[Tuple[str, ...], int] = {}
    for i, row in enumerate(rows):
        key = _row_key(row, config.key_columns, config.ignore_case)
        index[key] = i
    return index


def match_rows(
    rows_a: List[Dict[str, str]],
    rows_b: List[Dict[str, str]],
    config: MatchConfig,
) -> List[Tuple[Optional[int], Optional[int]]]:
    """Match rows from file A to file B using key columns.

    Returns a list of (index_a, index_b) pairs where None indicates
    a row present in only one file.
    """
    if not config.has_keys:
        # Fall back to positional matching
        length = max(len(rows_a), len(rows_b))
        return [
            (i if i < len(rows_a) else None, i if i < len(rows_b) else None)
            for i in range(length)
        ]

    index_b = build_key_index(rows_b, config)
    matched_b: set = set()
    pairs: List[Tuple[Optional[int], Optional[int]]] = []

    for i, row in enumerate(rows_a):
        key = _row_key(row, config.key_columns, config.ignore_case)
        j = index_b.get(key)
        if j is not None:
            pairs.append((i, j))
            matched_b.add(j)
        else:
            pairs.append((i, None))

    for j, row in enumerate(rows_b):
        if j not in matched_b:
            pairs.append((None, j))

    return pairs
