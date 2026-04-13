"""Formatter that applies pagination before rendering a diff."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from csvdiff.differ import DiffResult, RowDiff
from csvdiff.formatter import format_diff
from csvdiff.pager import PageConfig, PageResult, paginate, page_summary


@dataclass
class PaginatedFormatConfig:
    page_size: int = 50
    page: int = 1
    color: bool = True


def _collect_changed_rows(result: DiffResult) -> List[RowDiff]:
    """Return only rows that carry at least one change."""
    changed: List[RowDiff] = []
    for row in result.rows:
        if row.added or row.removed or row.cells:
            changed.append(row)
    return changed


def format_diff_paginated(
    result: DiffResult,
    headers: List[str],
    config: PaginatedFormatConfig,
) -> str:
    """Format *result* showing only the rows on the requested page."""
    changed = _collect_changed_rows(result)
    page_cfg = PageConfig(page_size=config.page_size, page=config.page)
    paged: PageResult[RowDiff] = paginate(changed, page_cfg)

    # Build a lightweight DiffResult containing only the paged rows.
    paged_result = DiffResult(
        rows=paged.items,
        headers_a=result.headers_a,
        headers_b=result.headers_b,
    )

    body = format_diff(paged_result, headers, color=config.color)
    summary_line = page_summary(paged)
    separator = "-" * len(summary_line)
    return f"{summary_line}\n{separator}\n{body}"
