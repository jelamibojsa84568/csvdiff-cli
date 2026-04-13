"""Summary reporter for CSV diff results."""

from dataclasses import dataclass
from typing import TextIO
import sys

from csvdiff.differ import DiffResult, total_changes


@dataclass
class DiffSummary:
    rows_added: int
    rows_removed: int
    rows_modified: int
    total_cell_changes: int
    files_identical: bool

    def __str__(self) -> str:
        if self.files_identical:
            return "Files are identical."
        parts = []
        if self.rows_added:
            parts.append(f"{self.rows_added} row(s) added")
        if self.rows_removed:
            parts.append(f"{self.rows_removed} row(s) removed")
        if self.rows_modified:
            parts.append(
                f"{self.rows_modified} row(s) modified "
                f"({self.total_cell_changes} cell change(s))"
            )
        return ", ".join(parts) + "."


def build_summary(result: DiffResult) -> DiffSummary:
    """Compute a DiffSummary from a DiffResult."""
    rows_added = sum(1 for r in result.rows if r.status == "added")
    rows_removed = sum(1 for r in result.rows if r.status == "removed")
    rows_modified = sum(1 for r in result.rows if r.status == "modified")
    cell_changes = total_changes(result)
    identical = (rows_added + rows_removed + rows_modified) == 0
    return DiffSummary(
        rows_added=rows_added,
        rows_removed=rows_removed,
        rows_modified=rows_modified,
        total_cell_changes=cell_changes,
        files_identical=identical,
    )


def print_summary(result: DiffResult, stream: TextIO = sys.stdout) -> None:
    """Print a human-readable summary of the diff to *stream*."""
    summary = build_summary(result)
    stream.write(str(summary) + "\n")


def exit_code(result: DiffResult) -> int:
    """Return 0 if files are identical, 1 if they differ."""
    summary = build_summary(result)
    return 0 if summary.files_identical else 1
