"""Column and row filtering utilities for csvdiff."""

from __future__ import annotations

from typing import List, Optional


class FilterConfig:
    """Holds filtering options for a diff operation."""

    def __init__(
        self,
        include_columns: Optional[List[str]] = None,
        exclude_columns: Optional[List[str]] = None,
        key_column: Optional[str] = None,
    ) -> None:
        if include_columns and exclude_columns:
            raise ValueError(
                "Cannot specify both include_columns and exclude_columns."
            )
        self.include_columns = include_columns or []
        self.exclude_columns = exclude_columns or []
        self.key_column = key_column


def apply_column_filter(
    headers: List[str], config: FilterConfig
) -> List[str]:
    """Return headers after applying include/exclude rules.

    The key column is always preserved when set.
    """
    if config.include_columns:
        filtered = [h for h in headers if h in config.include_columns]
    elif config.exclude_columns:
        filtered = [h for h in headers if h not in config.exclude_columns]
    else:
        filtered = list(headers)

    # Ensure key column is always present
    if config.key_column and config.key_column not in filtered:
        if config.key_column in headers:
            filtered.insert(0, config.key_column)

    return filtered


def filter_row(row: dict, allowed_columns: List[str]) -> dict:
    """Return a new dict containing only the allowed columns."""
    return {k: v for k, v in row.items() if k in allowed_columns}


def filter_rows(
    rows: List[dict], allowed_columns: List[str]
) -> List[dict]:
    """Apply column filtering to every row in a list."""
    return [filter_row(row, allowed_columns) for row in rows]
