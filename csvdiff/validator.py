"""Validation utilities for CSV diff inputs and configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional


class ValidationError(Exception):
    """Raised when input validation fails."""


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str]

    def __bool__(self) -> bool:
        return self.valid

    def __str__(self) -> str:
        if self.valid:
            return "Validation passed."
        return "Validation failed:\n" + "\n".join(f"  - {e}" for e in self.errors)


def validate_file_path(path: str, label: str = "File") -> List[str]:
    """Return a list of error messages for the given file path."""
    errors: List[str] = []
    if not path:
        errors.append(f"{label} path must not be empty.")
        return errors
    if not os.path.exists(path):
        errors.append(f"{label} not found: '{path}'.")
    elif not os.path.isfile(path):
        errors.append(f"{label} is not a regular file: '{path}'.")
    elif not os.access(path, os.R_OK):
        errors.append(f"{label} is not readable: '{path}'.")
    return errors


def validate_key_columns(key: Optional[List[str]], headers: List[str]) -> List[str]:
    """Validate that all key columns exist in the provided headers."""
    errors: List[str] = []
    if not key:
        return errors
    missing = [col for col in key if col not in headers]
    if missing:
        errors.append(
            f"Key column(s) not found in CSV headers: {', '.join(missing)}."
        )
    return errors


def validate_inputs(
    file_a: str,
    file_b: str,
    key: Optional[List[str]] = None,
    headers: Optional[List[str]] = None,
) -> ValidationResult:
    """Run all validations and return a consolidated ValidationResult."""
    errors: List[str] = []
    errors.extend(validate_file_path(file_a, label="File A"))
    errors.extend(validate_file_path(file_b, label="File B"))
    if key and headers is not None:
        errors.extend(validate_key_columns(key, headers))
    return ValidationResult(valid=len(errors) == 0, errors=errors)
