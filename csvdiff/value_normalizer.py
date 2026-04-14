"""Normalize cell values before comparison to reduce cosmetic diffs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class NormalizeConfig:
    """Configuration for value normalization."""

    strip_whitespace: bool = True
    lowercase: bool = False
    normalize_empty: bool = True  # treat None / whitespace-only as empty string
    decimal_places: Optional[int] = None  # round numeric strings to N places

    def __post_init__(self) -> None:
        if self.decimal_places is not None and self.decimal_places < 0:
            raise ValueError("decimal_places must be >= 0")


def _try_round(value: str, places: int) -> str:
    """Attempt to parse *value* as a float and round it; return original on failure."""
    try:
        rounded = round(float(value), places)
        # Preserve integer appearance when places == 0
        if places == 0:
            return str(int(rounded))
        return f"{rounded:.{places}f}"
    except (ValueError, OverflowError):
        return value


def normalize_value(value: str, config: NormalizeConfig) -> str:
    """Apply normalization rules to a single cell *value*."""
    if config.normalize_empty and (value is None or value.strip() == ""):
        return ""

    result: str = value if value is not None else ""

    if config.strip_whitespace:
        result = result.strip()

    if config.lowercase:
        result = result.lower()

    if config.decimal_places is not None:
        result = _try_round(result, config.decimal_places)

    return result


def normalize_row(row: dict[str, str], config: NormalizeConfig) -> dict[str, str]:
    """Return a new row dict with every value normalized according to *config*."""
    return {col: normalize_value(val, config) for col, val in row.items()}
