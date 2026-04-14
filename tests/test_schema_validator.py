"""Tests for csvdiff.schema_validator."""
import pytest
from csvdiff.schema_validator import (
    ColumnSchema,
    SchemaConfig,
    SchemaViolation,
    SchemaValidationResult,
    validate_schema,
)


# ---------------------------------------------------------------------------
# SchemaValidationResult helpers
# ---------------------------------------------------------------------------

def test_result_passes_when_no_violations():
    result = SchemaValidationResult(violations=[])
    assert result.passed() is True
    assert bool(result) is True


def test_result_fails_when_violations_present():
    v = SchemaViolation(kind="missing_column", column="id", detail="oops")
    result = SchemaValidationResult(violations=[v])
    assert result.passed() is False
    assert bool(result) is False


def test_result_str_passed():
    result = SchemaValidationResult(violations=[])
    assert str(result) == "Schema validation passed."


def test_result_str_failed_contains_violation():
    v = SchemaViolation(kind="missing_column", column="age", detail="Required column 'age' not found in file.")
    result = SchemaValidationResult(violations=[v])
    text = str(result)
    assert "Schema validation failed" in text
    assert "age" in text


# ---------------------------------------------------------------------------
# validate_schema – missing required columns
# ---------------------------------------------------------------------------

def test_missing_required_column():
    schema = SchemaConfig(columns=[ColumnSchema(name="id"), ColumnSchema(name="name")])
    result = validate_schema(headers=["name"], rows=[], schema=schema)
    assert not result.passed()
    kinds = [v.kind for v in result.violations]
    assert "missing_column" in kinds
    cols = [v.column for v in result.violations]
    assert "id" in cols


def test_optional_column_not_missing():
    schema = SchemaConfig(
        columns=[ColumnSchema(name="id"), ColumnSchema(name="note", required=False)]
    )
    result = validate_schema(headers=["id"], rows=[], schema=schema)
    assert result.passed()


# ---------------------------------------------------------------------------
# validate_schema – allowed values
# ---------------------------------------------------------------------------

def test_allowed_values_passes():
    schema = SchemaConfig(
        columns=[ColumnSchema(name="status", allowed_values=["active", "inactive"])]
    )
    rows = [{"status": "active"}, {"status": "inactive"}]
    result = validate_schema(headers=["status"], rows=rows, schema=schema)
    assert result.passed()


def test_allowed_values_violation():
    schema = SchemaConfig(
        columns=[ColumnSchema(name="status", allowed_values=["active", "inactive"])]
    )
    rows = [{"status": "pending"}]
    result = validate_schema(headers=["status"], rows=rows, schema=schema)
    assert not result.passed()
    assert result.violations[0].kind == "unexpected_value"
    assert "pending" in result.violations[0].detail


# ---------------------------------------------------------------------------
# validate_schema – strict mode (extra columns)
# ---------------------------------------------------------------------------

def test_strict_mode_flags_extra_column():
    schema = SchemaConfig(columns=[ColumnSchema(name="id")])
    result = validate_schema(headers=["id", "extra"], rows=[], schema=schema, strict=True)
    assert not result.passed()
    assert any(v.kind == "extra_column" and v.column == "extra" for v in result.violations)


def test_non_strict_mode_ignores_extra_column():
    schema = SchemaConfig(columns=[ColumnSchema(name="id")])
    result = validate_schema(headers=["id", "extra"], rows=[], schema=schema, strict=False)
    assert result.passed()


# ---------------------------------------------------------------------------
# SchemaConfig helpers
# ---------------------------------------------------------------------------

def test_schema_config_column_names():
    schema = SchemaConfig(
        columns=[ColumnSchema(name="a"), ColumnSchema(name="b", required=False)]
    )
    assert schema.column_names() == ["a", "b"]


def test_schema_config_required_columns():
    schema = SchemaConfig(
        columns=[ColumnSchema(name="a"), ColumnSchema(name="b", required=False)]
    )
    assert schema.required_columns() == ["a"]
