"""Export diff results to various formats (JSON, CSV)."""

from __future__ import annotations

import csv
import json
import io
from typing import List

from csvdiff.differ import DiffResult, RowDiff


def _row_diff_to_dict(row_diff: RowDiff) -> dict:
    """Convert a RowDiff to a serialisable dictionary."""
    changes = [
        {
            "column": c.column,
            "old_value": c.old_value,
            "new_value": c.new_value,
        }
        for c in row_diff.changes
    ]
    return {
        "row_number": row_diff.row_number,
        "key": row_diff.key,
        "change_type": row_diff.change_type,
        "changes": changes,
    }


def export_json(result: DiffResult, indent: int = 2) -> str:
    """Serialise a DiffResult to a JSON string."""
    payload = {
        "headers": result.headers,
        "rows": [_row_diff_to_dict(r) for r in result.rows],
    }
    return json.dumps(payload, indent=indent, ensure_ascii=False)


def export_csv(result: DiffResult) -> str:
    """Serialise a DiffResult to a flat CSV string.

    Each changed cell becomes its own row with columns:
    row_number, key, change_type, column, old_value, new_value.
    Added/removed rows produce one record per data column.
    """
    fieldnames = ["row_number", "key", "change_type", "column", "old_value", "new_value"]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()

    for row_diff in result.rows:
        base = {
            "row_number": row_diff.row_number,
            "key": row_diff.key,
            "change_type": row_diff.change_type,
        }
        if row_diff.changes:
            for cell in row_diff.changes:
                writer.writerow(
                    {**base, "column": cell.column,
                     "old_value": cell.old_value,
                     "new_value": cell.new_value}
                )
        else:
            writer.writerow({**base, "column": "", "old_value": "", "new_value": ""})

    return buf.getvalue()
