"""Human-readable output formatting for diff results."""

from typing import Optional
from csvdiff.differ import DiffResult, RowDiff

TRY_COLORS = True
try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
except ImportError:
    TRY_COLORS = False


def _green(text: str, use_color: bool) -> str:
    if use_color and TRY_COLORS:
        return f"{Fore.GREEN}{text}{Style.RESET_ALL}"
    return text


def _red(text: str, use_color: bool) -> str:
    if use_color and TRY_COLORS:
        return f"{Fore.RED}{text}{Style.RESET_ALL}"
    return text


def _yellow(text: str, use_color: bool) -> str:
    if use_color and TRY_COLORS:
        return f"{Fore.YELLOW}{text}{Style.RESET_ALL}"
    return text


def format_diff(result: DiffResult, use_color: bool = True) -> str:
    """Render a DiffResult as a human-readable string."""
    lines = []

    if result.columns_only_in_a:
        lines.append(
            _yellow(f"Columns only in A: {', '.join(result.columns_only_in_a)}", use_color)
        )
    if result.columns_only_in_b:
        lines.append(
            _yellow(f"Columns only in B: {', '.join(result.columns_only_in_b)}", use_color)
        )
    if result.columns_only_in_a or result.columns_only_in_b:
        lines.append("")

    for row in result.removed:
        lines.append(_red(f"- [{result.key_column}={row.key}] REMOVED", use_color))

    for row in result.added:
        lines.append(_green(f"+ [{result.key_column}={row.key}] ADDED", use_color))

    for row in result.modified:
        lines.append(
            _yellow(f"~ [{result.key_column}={row.key}] MODIFIED", use_color)
        )
        for change in row.cell_changes:
            old = _red(repr(change.old_value), use_color)
            new = _green(repr(change.new_value), use_color)
            lines.append(f"    {change.column}: {old} -> {new}")

    if not result.has_changes:
        lines.append("No differences found.")
    else:
        summary = (
            f"\nSummary: {len(result.added)} added, "
            f"{len(result.removed)} removed, "
            f"{len(result.modified)} modified."
        )
        lines.append(summary)

    return "\n".join(lines)
