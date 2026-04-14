"""Tests for csvdiff.value_normalizer."""
import pytest

from csvdiff.value_normalizer import (
    NormalizeConfig,
    normalize_value,
    normalize_row,
)


# ---------------------------------------------------------------------------
# NormalizeConfig
# ---------------------------------------------------------------------------

def test_normalize_config_defaults():
    cfg = NormalizeConfig()
    assert cfg.strip_whitespace is True
    assert cfg.lowercase is False
    assert cfg.normalize_empty is True
    assert cfg.decimal_places is None


def test_normalize_config_rejects_negative_decimal_places():
    with pytest.raises(ValueError, match="decimal_places"):
        NormalizeConfig(decimal_places=-1)


def test_normalize_config_accepts_zero_decimal_places():
    cfg = NormalizeConfig(decimal_places=0)
    assert cfg.decimal_places == 0


# ---------------------------------------------------------------------------
# normalize_value — strip_whitespace
# ---------------------------------------------------------------------------

def test_strip_whitespace_removes_leading_trailing():
    cfg = NormalizeConfig(strip_whitespace=True)
    assert normalize_value("  hello  ", cfg) == "hello"


def test_strip_whitespace_disabled_preserves_spaces():
    cfg = NormalizeConfig(strip_whitespace=False, normalize_empty=False)
    assert normalize_value("  hello  ", cfg) == "  hello  "


# ---------------------------------------------------------------------------
# normalize_value — lowercase
# ---------------------------------------------------------------------------

def test_lowercase_converts_to_lower():
    cfg = NormalizeConfig(lowercase=True)
    assert normalize_value("Hello World", cfg) == "hello world"


def test_lowercase_disabled_preserves_case():
    cfg = NormalizeConfig(lowercase=False)
    assert normalize_value("Hello World", cfg) == "Hello World"


# ---------------------------------------------------------------------------
# normalize_value — normalize_empty
# ---------------------------------------------------------------------------

def test_normalize_empty_none_becomes_empty_string():
    cfg = NormalizeConfig(normalize_empty=True)
    assert normalize_value(None, cfg) == ""


def test_normalize_empty_whitespace_only_becomes_empty_string():
    cfg = NormalizeConfig(normalize_empty=True)
    assert normalize_value("   ", cfg) == ""


def test_normalize_empty_disabled_preserves_whitespace_only():
    cfg = NormalizeConfig(normalize_empty=False, strip_whitespace=False)
    assert normalize_value("   ", cfg) == "   "


# ---------------------------------------------------------------------------
# normalize_value — decimal_places
# ---------------------------------------------------------------------------

def test_decimal_places_rounds_numeric_string():
    cfg = NormalizeConfig(decimal_places=2)
    assert normalize_value("3.14159", cfg) == "3.14"


def test_decimal_places_zero_returns_integer_string():
    cfg = NormalizeConfig(decimal_places=0)
    assert normalize_value("2.9", cfg) == "3"


def test_decimal_places_non_numeric_unchanged():
    cfg = NormalizeConfig(decimal_places=2)
    assert normalize_value("N/A", cfg) == "N/A"


# ---------------------------------------------------------------------------
# normalize_row
# ---------------------------------------------------------------------------

def test_normalize_row_applies_to_all_columns():
    cfg = NormalizeConfig(strip_whitespace=True, lowercase=True)
    row = {"Name": "  Alice  ", "City": "NEW YORK"}
    result = normalize_row(row, cfg)
    assert result == {"Name": "alice", "City": "new york"}


def test_normalize_row_returns_new_dict():
    cfg = NormalizeConfig()
    row = {"a": "1"}
    result = normalize_row(row, cfg)
    assert result is not row
