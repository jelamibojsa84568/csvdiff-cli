"""Tests for csvdiff.validator module."""

from __future__ import annotations

import os
import pytest

from csvdiff.validator import (
    ValidationResult,
    validate_file_path,
    validate_key_columns,
    validate_inputs,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture()
def csv_file(tmp_path):
    """Create a temporary CSV file and return its path."""
    p = tmp_path / "data.csv"
    p.write_text("id,name\n1,Alice\n")
    return str(p)


# ---------------------------------------------------------------------------
# ValidationResult
# ---------------------------------------------------------------------------


def test_validation_result_bool_true():
    result = ValidationResult(valid=True, errors=[])
    assert bool(result) is True


def test_validation_result_bool_false():
    result = ValidationResult(valid=False, errors=["some error"])
    assert bool(result) is False


def test_validation_result_str_passed():
    result = ValidationResult(valid=True, errors=[])
    assert "passed" in str(result)


def test_validation_result_str_failed():
    result = ValidationResult(valid=False, errors=["bad thing"])
    assert "failed" in str(result)
    assert "bad thing" in str(result)


# ---------------------------------------------------------------------------
# validate_file_path
# ---------------------------------------------------------------------------


def test_validate_file_path_ok(csv_file):
    assert validate_file_path(csv_file) == []


def test_validate_file_path_empty_string():
    errors = validate_file_path("", label="File A")
    assert any("empty" in e for e in errors)


def test_validate_file_path_missing(tmp_path):
    missing = str(tmp_path / "ghost.csv")
    errors = validate_file_path(missing, label="File B")
    assert any("not found" in e for e in errors)


def test_validate_file_path_directory(tmp_path):
    errors = validate_file_path(str(tmp_path), label="File A")
    assert any("regular file" in e for e in errors)


# ---------------------------------------------------------------------------
# validate_key_columns
# ---------------------------------------------------------------------------


def test_validate_key_columns_all_present():
    assert validate_key_columns(["id", "name"], ["id", "name", "age"]) == []


def test_validate_key_columns_missing():
    errors = validate_key_columns(["id", "missing_col"], ["id", "name"])
    assert len(errors) == 1
    assert "missing_col" in errors[0]


def test_validate_key_columns_empty_key():
    assert validate_key_columns([], ["id", "name"]) == []


def test_validate_key_columns_none_key():
    assert validate_key_columns(None, ["id", "name"]) == []


# ---------------------------------------------------------------------------
# validate_inputs
# ---------------------------------------------------------------------------


def test_validate_inputs_both_valid(csv_file):
    result = validate_inputs(csv_file, csv_file)
    assert result.valid


def test_validate_inputs_one_missing(csv_file, tmp_path):
    result = validate_inputs(csv_file, str(tmp_path / "nope.csv"))
    assert not result.valid
    assert len(result.errors) == 1


def test_validate_inputs_with_valid_key(csv_file):
    result = validate_inputs(csv_file, csv_file, key=["id"], headers=["id", "name"])
    assert result.valid


def test_validate_inputs_with_bad_key(csv_file):
    result = validate_inputs(csv_file, csv_file, key=["zzz"], headers=["id", "name"])
    assert not result.valid
    assert any("zzz" in e for e in result.errors)
