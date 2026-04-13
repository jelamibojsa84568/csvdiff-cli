"""Pagination support for large diff outputs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, TypeVar, Generic

T = TypeVar("T")


@dataclass
class PageConfig:
    page_size: int = 50
    page: int = 1

    def __post_init__(self) -> None:
        if self.page_size < 1:
            raise ValueError("page_size must be at least 1")
        if self.page < 1:
            raise ValueError("page must be at least 1")


@dataclass
class PageResult(Generic[T]):
    items: List[T]
    page: int
    page_size: int
    total_items: int

    @property
    def total_pages(self) -> int:
        if self.total_items == 0:
            return 1
        return (self.total_items + self.page_size - 1) // self.page_size

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1


def paginate(items: List[T], config: PageConfig) -> PageResult[T]:
    """Return a slice of *items* for the requested page."""
    total = len(items)
    start = (config.page - 1) * config.page_size
    end = start + config.page_size
    return PageResult(
        items=items[start:end],
        page=config.page,
        page_size=config.page_size,
        total_items=total,
    )


def page_summary(result: PageResult) -> str:  # type: ignore[type-arg]
    """Return a human-readable summary line for a page result."""
    return (
        f"Page {result.page} of {result.total_pages} "
        f"({result.total_items} total item(s))"
    )
