"""Compatibility wrappers for the queue API."""

from src.queue.api import (
    dequeue,
    enqueue,
    init_db,
    is_paused,
    list_items,
    mark_done,
    mark_failed,
    purge_completed,
    retry_item,
    set_paused,
)

__all__ = [
    "enqueue",
    "dequeue",
    "init_db",
    "list_items",
    "mark_done",
    "mark_failed",
    "retry_item",
    "purge_completed",
    "set_paused",
    "is_paused",
]
