"""Formatter that integrates inline highlighting into the full diff output."""
from __future__ import annotations

from typing import Optional

from csvdiff.differ import DiffResult, RowDiff
from csvdiff.formatter import _green, _red, _yellow
from csvdiff.highlighter import HighlightConfig, highlight_cell_label


def _format_row_highlighted(
    row_diff: RowDiff,
    config: Optional[HighlightConfig] = None,
) -> list[str]:
    """Render a single RowDiff with inline character-level highlighting."""
    lines: list[str] = []

    if row_diff.status == "added":
        lines.append(_green(f"+ row {row_diff.row_number}"))
        for col, val in (row_diff.row_b or {}).items():
            lines.append(f"  {_green(col)}: {_green(val)}")

    elif row_diff.status == "removed":
        lines.append(_red(f"- row {row_diff.row_number}"))
        for col, val in (row_diff.row_a or {}).items():
            lines.append(f"  {_red(col)}: {_red(val)}")

    elif row_diff.status == "modified":
        lines.append(_yellow(f"~ row {row_diff.row_number}"))
        for change in row_diff.changes:
            lines.append(
                highlight_cell_label(change.column, change.old_value, change.new_value, config)
            )

    return lines


def format_diff_highlighted(
    result: DiffResult,
    config: Optional[HighlightConfig] = None,
    show_unchanged: bool = False,
) -> str:
    """Return the full diff as a string with inline highlighting applied."""
    if config is None:
        config = HighlightConfig()

    lines: list[str] = []

    for row_diff in result.rows:
        if row_diff.status == "unchanged" and not show_unchanged:
            continue
        row_lines = _format_row_highlighted(row_diff, config)
        lines.extend(row_lines)

    if not lines:
        return "No differences found."

    return "\n".join(lines)
