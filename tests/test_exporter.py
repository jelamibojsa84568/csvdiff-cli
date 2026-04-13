"""Tests for csvdiff.exporter (JSON and CSV export)."""

from __future__ import annotations

import json
import csv
import io

import pytest

from csvdiff.differ import CellChange, RowDiff, DiffResult
from csvdiff.exporter import export_json, export_csv


HEADERS = ["id", "name", "score"]


def _modified_row() -> RowDiff:
    return RowDiff(
        row_number=2,
        key="2",
        change_type="modified",
        changes=[
            CellChange(column="name", old_value="Alice", new_value="Alicia"),
            CellChange(column="score", old_value="80", new_value="95"),
        ],
    )


def _added_row() -> RowDiff:
    return RowDiff(
        row_number=5,
        key="5",
        change_type="added",
        changes=[CellChange(column="id", old_value="", new_value="5")],
    )


def _removed_row() -> RowDiff:
    return RowDiff(
        row_number=3,
        key="3",
        change_type="removed",
        changes=[CellChange(column="id", old_value="3", new_value="")],
    )


@pytest.fixture()
def sample_result() -> DiffResult:
    return DiffResult(
        headers=HEADERS,
        rows=[_modified_row(), _added_row(), _removed_row()],
    )


# --- JSON export ---

def test_export_json_structure(sample_result):
    raw = export_json(sample_result)
    data = json.loads(raw)
    assert data["headers"] == HEADERS
    assert len(data["rows"]) == 3


def test_export_json_modified_row(sample_result):
    data = json.loads(export_json(sample_result))
    modified = next(r for r in data["rows"] if r["change_type"] == "modified")
    assert modified["key"] == "2"
    assert len(modified["changes"]) == 2
    col_names = [c["column"] for c in modified["changes"]]
    assert "name" in col_names and "score" in col_names


def test_export_json_added_row(sample_result):
    data = json.loads(export_json(sample_result))
    added = next(r for r in data["rows"] if r["change_type"] == "added")
    assert added["key"] == "5"


def test_export_json_is_valid_json(sample_result):
    raw = export_json(sample_result)
    # Should not raise
    json.loads(raw)


# --- CSV export ---

def _parse_csv(text: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(text)))


def test_export_csv_has_header(sample_result):
    text = export_csv(sample_result)
    assert text.startswith("row_number,key,change_type,column,old_value,new_value")


def test_export_csv_modified_produces_multiple_rows(sample_result):
    rows = _parse_csv(export_csv(sample_result))
    modified = [r for r in rows if r["change_type"] == "modified"]
    assert len(modified) == 2  # two cell changes


def test_export_csv_added_row_present(sample_result):
    rows = _parse_csv(export_csv(sample_result))
    added = [r for r in rows if r["change_type"] == "added"]
    assert len(added) == 1
    assert added[0]["key"] == "5"


def test_export_csv_removed_row_present(sample_result):
    rows = _parse_csv(export_csv(sample_result))
    removed = [r for r in rows if r["change_type"] == "removed"]
    assert len(removed) == 1
    assert removed[0]["key"] == "3"
