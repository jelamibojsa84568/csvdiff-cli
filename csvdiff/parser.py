"""CSV file parsing utilities for csvdiff-cli."""

import csv
from pathlib import Path
from typing import List, Dict, Optional


class CSVParseError(Exception):
    """Raised when a CSV file cannot be parsed."""
    pass


def load_csv(
    filepath: str,
    delimiter: str = ",",
    encoding: str = "utf-8",
    key_column: Optional[str] = None,
) -> Dict:
    """
    Load a CSV file and return a structured representation.

    Args:
        filepath: Path to the CSV file.
        delimiter: Column delimiter character.
        encoding: File encoding.
        key_column: Column to use as row identifier. Defaults to first column.

    Returns:
        A dict with 'headers' (list) and 'rows' (dict keyed by key_column value).
    """
    path = Path(filepath)
    if not path.exists():
        raise CSVParseError(f"File not found: {filepath}")
    if not path.is_file():
        raise CSVParseError(f"Not a file: {filepath}")

    try:
        with open(path, newline="", encoding=encoding) as fh:
            reader = csv.DictReader(fh, delimiter=delimiter)
            headers = reader.fieldnames
            if not headers:
                raise CSVParseError(f"CSV file has no headers: {filepath}")
            headers = list(headers)

            key = key_column if key_column else headers[0]
            if key not in headers:
                raise CSVParseError(
                    f"Key column '{key}' not found in {filepath}. "
                    f"Available columns: {headers}"
                )

            rows: Dict[str, Dict[str, str]] = {}
            for lineno, row in enumerate(reader, start=2):
                row_key = row.get(key)
                if row_key is None:
                    raise CSVParseError(
                        f"Missing key value at line {lineno} in {filepath}"
                    )
                if row_key in rows:
                    raise CSVParseError(
                        f"Duplicate key '{row_key}' at line {lineno} in {filepath}"
                    )
                rows[row_key] = dict(row)

    except (OSError, UnicodeDecodeError) as exc:
        raise CSVParseError(f"Could not read {filepath}: {exc}") from exc

    return {"headers": headers, "key": key, "rows": rows}


def get_common_headers(parsed_a: Dict, parsed_b: Dict) -> List[str]:
    """Return headers present in both CSVs, preserving order from file A."""
    set_b = set(parsed_b["headers"])
    return [h for h in parsed_a["headers"] if h in set_b]
