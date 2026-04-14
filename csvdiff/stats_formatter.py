"""Format DiffStats as a human-readable summary table."""
from __future__ import annotations

from csvdiff.differ_stats import DiffStats
from csvdiff.formatter import _green, _red, _yellow


def format_stats(stats: DiffStats, *, color: bool = True) -> str:
    """Return a formatted string summarising diff statistics."""
    lines: list[str] = []

    def _c(text: str, fn) -> str:  # noqa: ANN001
        return fn(text) if color else text

    lines.append("=== Diff Statistics ===")
    lines.append(f"  Rows compared : {stats.total_rows_compared}")
    lines.append(
        f"  Rows added    : {_c(str(stats.rows_added), _green)}"
    )
    lines.append(
        f"  Rows removed  : {_c(str(stats.rows_removed), _red)}"
    )
    lines.append(
        f"  Rows modified : {_c(str(stats.rows_modified), _yellow)}"
    )
    lines.append(f"  Rows unchanged: {stats.rows_unchanged}")

    if stats.column_stats:
        lines.append("")
        lines.append("  Column-level changes:")
        # Sort by total changes descending for readability
        sorted_cols = sorted(
            stats.column_stats.values(),
            key=lambda cs: cs.total,
            reverse=True,
        )
        for cs in sorted_cols:
            if cs.total == 0:
                continue
            parts = []
            if cs.changed:
                parts.append(_c(f"modified={cs.changed}", _yellow))
            if cs.added:
                parts.append(_c(f"added={cs.added}", _green))
            if cs.removed:
                parts.append(_c(f"removed={cs.removed}", _red))
            lines.append(f"    {cs.column}: {', '.join(parts)}")

    return "\n".join(lines)
