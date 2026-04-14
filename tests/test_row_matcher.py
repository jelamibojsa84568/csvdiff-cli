"""Tests for csvdiff.row_matcher."""
import pytest
from csvdiff.row_matcher import (
    MatchConfig,
    MatchError,
    build_key_index,
    match_rows,
)


# ---------------------------------------------------------------------------
# MatchConfig
# ---------------------------------------------------------------------------

def test_match_config_defaults():
    cfg = MatchConfig()
    assert cfg.key_columns == []
    assert cfg.ignore_case is False
    assert cfg.has_keys is False


def test_match_config_accepts_valid_keys():
    cfg = MatchConfig(key_columns=["id", "name"])
    assert cfg.has_keys is True


def test_match_config_rejects_non_list():
    with pytest.raises(MatchError):
        MatchConfig(key_columns="id")  # type: ignore[arg-type]


def test_match_config_rejects_blank_key():
    with pytest.raises(MatchError):
        MatchConfig(key_columns=[""])


def test_match_config_rejects_whitespace_key():
    with pytest.raises(MatchError):
        MatchConfig(key_columns=["   "])


# ---------------------------------------------------------------------------
# build_key_index
# ---------------------------------------------------------------------------

def test_build_key_index_basic():
    rows = [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]
    cfg = MatchConfig(key_columns=["id"])
    index = build_key_index(rows, cfg)
    assert index[("1",)] == 0
    assert index[("2",)] == 1


def test_build_key_index_duplicate_key_last_wins():
    rows = [{"id": "1", "val": "a"}, {"id": "1", "val": "b"}]
    cfg = MatchConfig(key_columns=["id"])
    index = build_key_index(rows, cfg)
    assert index[("1",)] == 1


def test_build_key_index_ignore_case():
    rows = [{"id": "ABC"}, {"id": "def"}]
    cfg = MatchConfig(key_columns=["id"], ignore_case=True)
    index = build_key_index(rows, cfg)
    assert ("abc",) in index
    assert ("def",) in index


# ---------------------------------------------------------------------------
# match_rows — positional fallback
# ---------------------------------------------------------------------------

def test_match_rows_positional_equal_length():
    rows_a = [{"v": "1"}, {"v": "2"}]
    rows_b = [{"v": "1"}, {"v": "2"}]
    cfg = MatchConfig()
    pairs = match_rows(rows_a, rows_b, cfg)
    assert pairs == [(0, 0), (1, 1)]


def test_match_rows_positional_a_longer():
    rows_a = [{"v": "1"}, {"v": "2"}, {"v": "3"}]
    rows_b = [{"v": "1"}]
    cfg = MatchConfig()
    pairs = match_rows(rows_a, rows_b, cfg)
    assert (1, None) in pairs
    assert (2, None) in pairs


def test_match_rows_positional_b_longer():
    rows_a = [{"v": "1"}]
    rows_b = [{"v": "1"}, {"v": "2"}]
    cfg = MatchConfig()
    pairs = match_rows(rows_a, rows_b, cfg)
    assert (None, 1) in pairs


# ---------------------------------------------------------------------------
# match_rows — key-based
# ---------------------------------------------------------------------------

def test_match_rows_by_key_all_match():
    rows_a = [{"id": "1", "x": "a"}, {"id": "2", "x": "b"}]
    rows_b = [{"id": "2", "x": "B"}, {"id": "1", "x": "A"}]
    cfg = MatchConfig(key_columns=["id"])
    pairs = match_rows(rows_a, rows_b, cfg)
    matched = {a: b for a, b in pairs if a is not None and b is not None}
    assert matched[0] == 1  # id=1 is at index 1 in rows_b
    assert matched[1] == 0  # id=2 is at index 0 in rows_b


def test_match_rows_by_key_unmatched_a():
    rows_a = [{"id": "1"}, {"id": "99"}]
    rows_b = [{"id": "1"}]
    cfg = MatchConfig(key_columns=["id"])
    pairs = match_rows(rows_a, rows_b, cfg)
    assert (1, None) in pairs


def test_match_rows_by_key_unmatched_b():
    rows_a = [{"id": "1"}]
    rows_b = [{"id": "1"}, {"id": "42"}]
    cfg = MatchConfig(key_columns=["id"])
    pairs = match_rows(rows_a, rows_b, cfg)
    assert (None, 1) in pairs


def test_match_rows_ignore_case_matches():
    rows_a = [{"id": "Alice"}]
    rows_b = [{"id": "alice"}]
    cfg = MatchConfig(key_columns=["id"], ignore_case=True)
    pairs = match_rows(rows_a, rows_b, cfg)
    assert (0, 0) in pairs
