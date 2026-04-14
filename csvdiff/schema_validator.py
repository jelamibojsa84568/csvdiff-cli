"""Schema validation: check that CSV files conform to expected column definitions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class ColumnSchema:
    name: str
    required: bool = True
    allowed_values: Optional[List[str]] = None


@dataclass
class SchemaConfig:
    columns: List[ColumnSchema] = field(default_factory=list)

    def column_names(self) -> List[str]:
        return [c.name for c in self.columns]

    def required_columns(self) -> List[str]:
        return [c.name for c in self.columns if c.required]


@dataclass
class SchemaViolation:
    kind: str          # 'missing_column' | 'unexpected_value' | 'extra_column'
    column: str
    detail: str = ""

    def __str__(self) -> str:
        return f"[{self.kind}] column={self.column!r}: {self.detail}"


@dataclass
class SchemaValidationResult:
    violations: List[SchemaViolation] = field(default_factory=list)

    def passed(self) -> bool:
        return len(self.violations) == 0

    def __bool__(self) -> bool:
        return self.passed()

    def __str__(self) -> str:
        if self.passed():
            return "Schema validation passed."
        lines = ["Schema validation failed:"]
        for v in self.violations:
            lines.append(f"  - {v}")
        return "\n".join(lines)


def validate_schema(
    headers: List[str],
    rows: List[Dict[str, str]],
    schema: SchemaConfig,
    strict: bool = False,
) -> SchemaValidationResult:
    """Validate *headers* and *rows* against *schema*.

    Parameters
    ----------
    headers:  Actual column names from the CSV.
    rows:     Parsed CSV rows (list of dicts).
    schema:   Expected schema definition.
    strict:   If True, extra columns not in the schema are also violations.
    """
    violations: List[SchemaViolation] = []
    header_set = set(headers)

    # Check required columns are present
    for col in schema.required_columns():
        if col not in header_set:
            violations.append(
                SchemaViolation(
                    kind="missing_column",
                    column=col,
                    detail=f"Required column '{col}' not found in file.",
                )
            )

    # Optionally flag extra columns
    if strict:
        schema_set = set(schema.column_names())
        for col in headers:
            if col not in schema_set:
                violations.append(
                    SchemaViolation(
                        kind="extra_column",
                        column=col,
                        detail=f"Column '{col}' is not defined in schema.",
                    )
                )

    # Check allowed_values constraints
    for col_schema in schema.columns:
        if col_schema.allowed_values is None:
            continue
        if col_schema.name not in header_set:
            continue  # already reported as missing
        allowed = set(col_schema.allowed_values)
        for i, row in enumerate(rows, start=1):
            val = row.get(col_schema.name, "")
            if val not in allowed:
                violations.append(
                    SchemaViolation(
                        kind="unexpected_value",
                        column=col_schema.name,
                        detail=(
                            f"Row {i}: value {val!r} not in "
                            f"allowed set {sorted(allowed)}."
                        ),
                    )
                )

    return SchemaValidationResult(violations=violations)
