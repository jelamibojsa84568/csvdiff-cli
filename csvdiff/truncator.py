"""Utilities for truncating long cell values in diff output."""

from dataclasses import dataclass
from typing import Optional

DEFAULT_MAX_LENGTH = 80
ELLIPSIS = "..."


@dataclass
class TruncateConfig:
    """Configuration for cell value truncation."""

    max_length: int = DEFAULT_MAX_LENGTH
    enabled: bool = True

    def __post_init__(self) -> None:
        if self.max_length < len(ELLIPSIS) + 1:
            raise ValueError(
                f"max_length must be at least {len(ELLIPSIS) + 1}, got {self.max_length}"
            )


def truncate_value(value: str, config: Optional[TruncateConfig] = None) -> str:
    """Truncate a single string value according to the given config.

    Args:
        value: The string to potentially truncate.
        config: Truncation settings. Uses defaults if None.

    Returns:
        The original string if within limits, otherwise a truncated version
        ending with an ellipsis marker.
    """
    if config is None:
        config = TruncateConfig()

    if not config.enabled or len(value) <= config.max_length:
        return value

    keep = config.max_length - len(ELLIPSIS)
    return value[:keep] + ELLIPSIS


def truncate_row_values(
    row: dict[str, str], config: Optional[TruncateConfig] = None
) -> dict[str, str]:
    """Apply truncation to every cell in a row dictionary.

    Args:
        row: Mapping of column name to cell value.
        config: Truncation settings. Uses defaults if None.

    Returns:
        A new dict with all values truncated as needed.
    """
    return {col: truncate_value(val, config) for col, val in row.items()}
