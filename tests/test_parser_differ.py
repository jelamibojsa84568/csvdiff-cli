"""Tests for CSV parser and differ modules."""

import pytest
import tempfile
import os

from csvdiff.parser import load_csv, CSVParseError, get_common_headers
from csvdiff.differ import diff_csvs


def write_csv(content: str) -> str:
    """Write content to a temp file and return its path."""
    fd, path = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)
    return path


CSV_A = "id,name,score\n1,Alice,90\n2,Bob,85\n3,Carol,78\n"
CSV_B = "id,name,score\n1,Alice,95\n3,Carol,78\n4,Dave,88\n"


@pytest.fixture
def path_a(tmp_path):
    p = tmp_path / "a.csv"
    p.write_text(CSV_A)
    return str(p)


@pytest.fixture
def path_b(tmp_path):
    p = tmp_path / "b.csv"
    p.write_text(CSV_B)
    return str(p)


def test_load_csv_basic(path_a):
    result = load_csv(path_a)
    assert result["headers"] == ["id", "name", "score"]
    assert result["key"] == "id"
    assert len(result["rows"]) == 3
    assert result["rows"]["1"]["name"] == "Alice"


def test_load_csv_missing_file():
    with pytest.raises(CSVParseError, match="File not found"):
        load_csv("/nonexistent/path/file.csv")


def test_load_csv_invalid_key(path_a):
    with pytest.raises(CSVParseError, match="Key column"):
        load_csv(path_a, key_column="nonexistent")


def test_load_csv_duplicate_key(tmp_path):
    p = tmp_path / "dup.csv"
    p.write_text("id,name\n1,Alice\n1,Bob\n")
    with pytest.raises(CSVParseError, match="Duplicate key"):
        load_csv(str(p))


def test_get_common_headers(path_a, tmp_path):
    p_extra = tmp_path / "extra.csv"
    p_extra.write_text("id,name,grade\n1,Alice,A\n")
    pa = load_csv(path_a)
    pb = load_csv(str(p_extra))
    common = get_common_headers(pa, pb)
    assert common == ["id", "name"]


def test_diff_added_removed_modified(path_a, path_b):
    pa = load_csv(path_a)
    pb = load_csv(path_b)
    result = diff_csvs(pa, pb)

    assert result.has_changes
    assert len(result.removed) == 1
    assert result.removed[0].key == "2"

    assert len(result.added) == 1
    assert result.added[0].key == "4"

    assert len(result.modified) == 1
    mod = result.modified[0]
    assert mod.key == "1"
    assert len(mod.cell_changes) == 1
    assert mod.cell_changes[0].column == "score"
    assert mod.cell_changes[0].old_value == "90"
    assert mod.cell_changes[0].new_value == "95"


def test_diff_no_changes(path_a):
    pa = load_csv(path_a)
    pb = load_csv(path_a)
    result = diff_csvs(pa, pb)
    assert not result.has_changes
    assert result.total_changes == 0


def test_diff_ignore_column(path_a, path_b):
    pa = load_csv(path_a)
    pb = load_csv(path_b)
    result = diff_csvs(pa, pb, ignore_columns=["score"])
    assert len(result.modified) == 0
