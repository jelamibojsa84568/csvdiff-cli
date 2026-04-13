"""Tests for csvdiff.pager."""
import pytest

from csvdiff.pager import PageConfig, PageResult, paginate, page_summary


# ---------------------------------------------------------------------------
# PageConfig
# ---------------------------------------------------------------------------

def test_page_config_defaults():
    cfg = PageConfig()
    assert cfg.page_size == 50
    assert cfg.page == 1


def test_page_config_rejects_zero_page_size():
    with pytest.raises(ValueError, match="page_size"):
        PageConfig(page_size=0)


def test_page_config_rejects_zero_page():
    with pytest.raises(ValueError, match="page"):
        PageConfig(page=0)


# ---------------------------------------------------------------------------
# PageResult properties
# ---------------------------------------------------------------------------

def _make_result(items, page=1, page_size=10, total=None):
    return PageResult(
        items=items,
        page=page,
        page_size=page_size,
        total_items=total if total is not None else len(items),
    )


def test_total_pages_empty():
    r = _make_result([], total=0)
    assert r.total_pages == 1


def test_total_pages_exact_multiple():
    r = _make_result(list(range(10)), total=20, page_size=10)
    assert r.total_pages == 2


def test_total_pages_remainder():
    r = _make_result(list(range(5)), total=25, page_size=10)
    assert r.total_pages == 3


def test_has_next_true():
    r = _make_result(list(range(10)), page=1, page_size=10, total=25)
    assert r.has_next is True


def test_has_next_false_on_last_page():
    r = _make_result(list(range(5)), page=3, page_size=10, total=25)
    assert r.has_next is False


def test_has_prev_false_on_first_page():
    r = _make_result(list(range(10)), page=1)
    assert r.has_prev is False


def test_has_prev_true():
    r = _make_result(list(range(10)), page=2, total=20)
    assert r.has_prev is True


# ---------------------------------------------------------------------------
# paginate()
# ---------------------------------------------------------------------------

def test_paginate_first_page():
    items = list(range(25))
    result = paginate(items, PageConfig(page_size=10, page=1))
    assert result.items == list(range(10))
    assert result.total_items == 25


def test_paginate_last_partial_page():
    items = list(range(25))
    result = paginate(items, PageConfig(page_size=10, page=3))
    assert result.items == [20, 21, 22, 23, 24]


def test_paginate_beyond_last_page_returns_empty():
    items = list(range(5))
    result = paginate(items, PageConfig(page_size=10, page=5))
    assert result.items == []


# ---------------------------------------------------------------------------
# page_summary()
# ---------------------------------------------------------------------------

def test_page_summary_format():
    r = _make_result(list(range(10)), page=2, page_size=10, total=25)
    summary = page_summary(r)
    assert "Page 2 of 3" in summary
    assert "25 total item(s)" in summary
