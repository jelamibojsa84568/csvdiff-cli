"""Convenience wrapper: run the full diff and return highlighted output."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from csvdiff.filter import FilterConfig
from csvdiff.highlight_formatter import format_diff_highlighted
from csvdiff.highlighter import HighlightConfig
from csvdiff.pipeline import run_diff
from csvdiff.sorter import SortKey, sort_diff_result
from csvdiff.truncator import TruncateConfig, truncate_row_values


def run_highlighted_diff(
    file_a: Path,
    file_b: Path,
    *,
    key_column: Optional[str] = None,
    filter_config: Optional[FilterConfig] = None,
    sort_key: SortKey = SortKey.ROW_NUMBER,
    truncate_config: Optional[TruncateConfig] = None,
    highlight_config: Optional[HighlightConfig] = None,
    show_unchanged: bool = False,
) -> str:
    """Run a full diff pipeline and return a highlighted string.

    Parameters
    ----------
    file_a, file_b:
        Paths to the two CSV files to compare.
    key_column:
        Optional column name to use as the row key for matching.
    filter_config:
        Column include/exclude filter to apply before diffing.
    sort_key:
        How to sort the diff output rows.
    truncate_config:
        Value truncation settings applied after diffing.
    highlight_config:
        Inline character-level highlighting settings.
    show_unchanged:
        When True, unchanged rows are included in the output.
    """
    result = run_diff(file_a, file_b, key_column=key_column, filter_config=filter_config)

    if truncate_config is not None:
        for row_diff in result.rows:
            if row_diff.row_a is not None:
                row_diff.row_a = truncate_row_values(row_diff.row_a, truncate_config)
            if row_diff.row_b is not None:
                row_diff.row_b = truncate_row_values(row_diff.row_b, truncate_config)

    result = sort_diff_result(result, sort_key)

    return format_diff_highlighted(
        result,
        config=highlight_config,
        show_unchanged=show_unchanged,
    )
