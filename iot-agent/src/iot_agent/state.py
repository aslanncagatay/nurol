"""Shared state for the IoT triage state machine.

Every node receives the whole state and returns a partial update. Fields
annotated with a reducer (``errors``, ``trail``) are appended to instead of
overwritten, so the audit trail survives branching and retries.
"""

from __future__ import annotations

from operator import add
from typing import Annotated, Any, Literal, TypedDict

Severity = Literal["unknown", "normal", "warning", "critical"]
Status = Literal["pending", "archived", "notified", "escalated", "quarantined"]


class TriageState(TypedDict):
    """State carried through the graph for a single telemetry message."""

    # Input
    raw: str
    message_id: str

    # Filled in by the nodes
    reading: dict[str, Any] | None
    severity: Severity
    status: Status
    retries: int
    enrichment: dict[str, Any]
    alert: dict[str, Any] | None

    # Reduced (append-only) fields
    errors: Annotated[list[str], add]
    trail: Annotated[list[str], add]


def new_state(raw: str, message_id: str = "") -> TriageState:
    """Build the initial state for a raw message body."""
    return TriageState(
        raw=raw,
        message_id=message_id,
        reading=None,
        severity="unknown",
        status="pending",
        retries=0,
        enrichment={},
        alert=None,
        errors=[],
        trail=[],
    )
