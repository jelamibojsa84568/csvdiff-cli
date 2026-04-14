"""Pipeline integration: run schema validation as part of the diff workflow."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csvdiff.schema_validator import (
    SchemaConfig,
    SchemaValidationResult,
    validate_schema,
)


@dataclass
class SchemaPipelineConfig:
    """Configuration for schema-aware diff runs."""

    schema: Optional[SchemaConfig] = None
    strict: bool = False
    # When True, abort the diff if schema validation fails.
    abort_on_failure: bool = False


@dataclass
class SchemaPipelineResult:
    file_a_result: Optional[SchemaValidationResult] = None
    file_b_result: Optional[SchemaValidationResult] = None

    def both_passed(self) -> bool:
        a_ok = self.file_a_result is None or self.file_a_result.passed()
        b_ok = self.file_b_result is None or self.file_b_result.passed()
        return a_ok and b_ok

    def summary_lines(self) -> List[str]:
        lines: List[str] = []
        if self.file_a_result is not None:
            lines.append(f"File A schema: {self.file_a_result}")
        if self.file_b_result is not None:
            lines.append(f"File B schema: {self.file_b_result}")
        return lines


def run_schema_validation(
    headers_a: List[str],
    rows_a: List[Dict[str, str]],
    headers_b: List[str],
    rows_b: List[Dict[str, str]],
    config: SchemaPipelineConfig,
) -> SchemaPipelineResult:
    """Validate both CSV datasets against the configured schema.

    Returns a :class:`SchemaPipelineResult`.  Raises ``ValueError`` when
    ``config.abort_on_failure`` is *True* and any validation fails.
    """
    if config.schema is None:
        return SchemaPipelineResult()

    result_a = validate_schema(
        headers=headers_a,
        rows=rows_a,
        schema=config.schema,
        strict=config.strict,
    )
    result_b = validate_schema(
        headers=headers_b,
        rows=rows_b,
        schema=config.schema,
        strict=config.strict,
    )

    pipeline_result = SchemaPipelineResult(
        file_a_result=result_a,
        file_b_result=result_b,
    )

    if config.abort_on_failure and not pipeline_result.both_passed():
        messages = "\n".join(pipeline_result.summary_lines())
        raise ValueError(
            f"Schema validation failed; aborting diff.\n{messages}"
        )

    return pipeline_result
