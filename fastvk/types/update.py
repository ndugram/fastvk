from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Update:
    """
    A single event received from VK Long Poll.

    Corresponds to one item in the ``updates`` array
    returned by the VK Long Poll server.
    """

    type: str
    """Event type (e.g. ``message_new``, ``group_join``, ``wall_post_new``)."""

    object: dict
    """Event payload — structure depends on ``type``."""

    group_id: int
    """ID of the group that received this event."""

    event_id: str
    """Unique event identifier assigned by VK."""
