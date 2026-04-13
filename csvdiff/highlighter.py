"""Inline diff highlighting for changed cell values."""
from __future__ import annotations

import difflib
from dataclasses import dataclass
from typing import Optional

from csvdiff.formatter import _green, _red, _yellow


@dataclass
class HighlightConfig:
    """Configuration for inline value highlighting."""
    enabled: bool = True
    min_length: int = 3  # minimum value length to attempt char-level diff
    context_chars: int = 0  # unused; reserved for future context windows

    def __post_init__(self) -> None:
        if self.min_length < 1:
            raise ValueError("min_length must be at least 1")


def _char_diff(old: str, new: str) -> tuple[str, str]:
    """Return (highlighted_old, highlighted_new) with character-level markup."""
    matcher = difflib.SequenceMatcher(None, old, new, autojunk=False)
    old_parts: list[str] = []
    new_parts: list[str] = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        old_chunk = old[i1:i2]
        new_chunk = new[j1:j2]
        if tag == "equal":
            old_parts.append(old_chunk)
            new_parts.append(new_chunk)
        elif tag == "replace":
            old_parts.append(_red(old_chunk))
            new_parts.append(_green(new_chunk))
        elif tag == "delete":
            old_parts.append(_red(old_chunk))
        elif tag == "insert":
            new_parts.append(_green(new_chunk))

    return "".join(old_parts), "".join(new_parts)


def highlight_change(
    old: str,
    new: str,
    config: Optional[HighlightConfig] = None,
) -> tuple[str, str]:
    """Return (old_display, new_display) with optional inline highlighting.

    Falls back to plain _red / _green colouring when the values are too
    short or highlighting is disabled.
    """
    if config is None:
        config = HighlightConfig()

    if not config.enabled:
        return _red(old), _green(new)

    if len(old) < config.min_length or len(new) < config.min_length:
        return _red(old), _green(new)

    return _char_diff(old, new)


def highlight_cell_label(column: str, old: str, new: str, config: Optional[HighlightConfig] = None) -> str:
    """Format a single cell change as a one-line string with inline highlighting."""
    old_display, new_display = highlight_change(old, new, config)
    return f"  {_yellow(column)}: {old_display} → {new_display}"
