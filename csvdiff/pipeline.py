"""High-level pipeline that wires parser, filter, and differ together."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from csvdiff.parser import load_csv, get_common_headers
from csvdiff.filter import FilterConfig, apply_column_filter, filter_rows
from csvdiff.differ import DiffResult, diff_csv


def run_diff(
    path_a: Path,
    path_b: Path,
    key: str,
    encoding: str = "utf-8",
    filter_config: Optional[FilterConfig] = None,
) -> DiffResult:
    """Load, optionally filter, then diff two CSV files.

    Parameters
    ----------
    path_a:
        Path to the *original* CSV file.
    path_b:
        Path to the *new* CSV file.
    key:
        Column name used to match rows between files.
    encoding:
        File encoding for both CSVs.
    filter_config:
        Optional :class:`FilterConfig` that restricts which columns are
        included in the diff.  When *None* all common columns are used.

    Returns
    -------
    DiffResult
        Structured diff ready for formatting or reporting.
    """
    rows_a = load_csv(path_a, encoding=encoding)
    rows_b = load_csv(path_b, encoding=encoding)

    headers_a = list(rows_a[0].keys()) if rows_a else []
    headers_b = list(rows_b[0].keys()) if rows_b else []
    common = get_common_headers(headers_a, headers_b)

    if filter_config is not None:
        common = apply_column_filter(common, filter_config)
        rows_a = filter_rows(rows_a, common)
        rows_b = filter_rows(rows_b, common)

    return diff_csv(rows_a, rows_b, key=key, headers=common)
