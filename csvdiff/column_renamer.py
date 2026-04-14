"""Column renaming support for CSV diff comparisons.

Allows mapping column names from file A to equivalent column names in file B
so that semantically equivalent columns with different headers can be compared.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RenameConfig:
    """Configuration for column renaming between two CSV files."""

    # Maps column name in file A -> column name in file B
    rename_map: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.rename_map, dict):
            raise TypeError("rename_map must be a dict")
        for k, v in self.rename_map.items():
            if not isinstance(k, str) or not k.strip():
                raise ValueError(f"Invalid source column name: {k!r}")
            if not isinstance(v, str) or not v.strip():
                raise ValueError(f"Invalid target column name: {v!r}")

    def is_empty(self) -> bool:
        return len(self.rename_map) == 0

    def apply_to_headers(self, headers: List[str]) -> List[str]:
        """Return headers with source names replaced by their target names."""
        return [self.rename_map.get(h, h) for h in headers]

    def apply_to_row(self, row: Dict[str, str]) -> Dict[str, str]:
        """Return a new row dict with source column keys replaced by target keys."""
        return {self.rename_map.get(k, k): v for k, v in row.items()}

    def reverse(self) -> "RenameConfig":
        """Return a new RenameConfig with source and target swapped."""
        return RenameConfig(rename_map={v: k for k, v in self.rename_map.items()})


def rename_rows(
    rows: List[Dict[str, str]],
    config: RenameConfig,
) -> List[Dict[str, str]]:
    """Apply rename_map to every row in a list, returning new row dicts."""
    if config.is_empty():
        return rows
    return [config.apply_to_row(row) for row in rows]


def rename_headers(
    headers: List[str],
    config: RenameConfig,
) -> List[str]:
    """Apply rename_map to a list of header strings."""
    if config.is_empty():
        return headers
    return config.apply_to_headers(headers)
