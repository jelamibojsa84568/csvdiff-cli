"""High-level output orchestration: format diff + print summary."""

from typing import TextIO
import sys

from csvdiff.differ import DiffResult
from csvdiff.formatter import format_diff
from csvdiff.reporter import print_summary, exit_code


def write_output(
    result: DiffResult,
    stream: TextIO = sys.stdout,
    *,
    show_summary: bool = True,
    color: bool = True,
) -> int:
    """Write formatted diff and optional summary to *stream*.

    Returns an exit code (0 = identical, 1 = differences found).
    """
    diff_text = format_diff(result, color=color)
    if diff_text:
        stream.write(diff_text)
        if not diff_text.endswith("\n"):
            stream.write("\n")

    if show_summary:
        print_summary(result, stream=stream)

    return exit_code(result)


def write_output_to_file(
    result: DiffResult,
    filepath: str,
    *,
    show_summary: bool = True,
) -> int:
    """Write diff output to a file at *filepath* (no color codes).

    Returns an exit code (0 = identical, 1 = differences found).
    """
    with open(filepath, "w", encoding="utf-8") as fh:
        return write_output(
            result,
            stream=fh,
            show_summary=show_summary,
            color=False,
        )
