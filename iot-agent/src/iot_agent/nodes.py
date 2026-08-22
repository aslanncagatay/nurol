"""Node implementations for the IoT triage state machine.

Each node is a plain function: it takes the current state plus its injected
dependencies and returns only the fields it wants to change. Nothing here
touches the graph, so every node can be unit tested on its own.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Callable

from .config import DEVICE_REGISTRY, MetricRule

logger = logging.getLogger(__name__)

Enricher = Callable[[str], dict[str, Any]]
Sink = Callable[[dict[str, Any]], None]

REQUIRED_FIELDS = ("device_id", "metric", "value")


class TransientEnrichmentError(RuntimeError):
    """Raised by an enricher when the lookup may succeed if retried."""


def ingest(state: dict[str, Any]) -> dict[str, Any]:
    """Parse the incoming body into a telemetry reading.

    Accepts either a bare reading or the ``CustomMessage`` envelope that
    sender-service publishes, where the reading sits in ``message`` as either
    a nested object or an embedded JSON string.
    """
    raw = state.get("raw", "")
    payload: Any = raw
    if isinstance(raw, (str, bytes)):
        try:
            payload = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            return {"errors": [f"ingest: body is not valid JSON ({exc})"], "trail": ["ingest"]}

    if not isinstance(payload, dict):
        return {"errors": ["ingest: body is not a JSON object"], "trail": ["ingest"]}

    message_id = (
        payload.get("messageId")
        or payload.get("message_id")
        or state.get("message_id")
        or ""
    )

    body: Any = payload.get("message", payload)
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError as exc:
            return {
                "message_id": message_id,
                "errors": [f"ingest: envelope 'message' is not valid JSON ({exc})"],
                "trail": ["ingest"],
            }

    if not isinstance(body, dict):
        return {
            "message_id": message_id,
            "errors": ["ingest: reading is not a JSON object"],
            "trail": ["ingest"],
        }

    return {"reading": body, "message_id": message_id, "trail": ["ingest"]}


def validate(state: dict[str, Any], *, rules: dict[str, MetricRule]) -> dict[str, Any]:
    """Check the reading against the schema and the metric's plausible range."""
    reading = state.get("reading") or {}
    errors = [f"validate: missing field '{f}'" for f in REQUIRED_FIELDS if not reading.get(f)]
    if errors:
        return {"errors": errors, "trail": ["validate"]}

    metric = str(reading["metric"])
    rule = rules.get(metric)
    if rule is None:
        return {"errors": [f"validate: unknown metric '{metric}'"], "trail": ["validate"]}

    try:
        value = float(reading["value"])
    except (TypeError, ValueError):
        return {
            "errors": [f"validate: value '{reading['value']}' is not numeric"],
            "trail": ["validate"],
        }

    if not rule.in_range(value):
        return {
            "errors": [
                f"validate: {metric} value {value} outside plausible range "
                f"[{rule.valid_min}, {rule.valid_max}]"
            ],
            "trail": ["validate"],
        }

    normalised = {
        **reading,
        "device_id": str(reading["device_id"]),
        "metric": metric,
        "value": value,
        "unit": reading.get("unit") or rule.unit,
    }
    return {"reading": normalised, "trail": ["validate"]}


def classify(state: dict[str, Any], *, rules: dict[str, MetricRule]) -> dict[str, Any]:
    """Turn the reading into a severity by comparing it to the thresholds."""
    reading = state["reading"]
    rule = rules[reading["metric"]]
    value = reading["value"]

    if rule.breaches(value, rule.critical):
        severity = "critical"
    elif rule.breaches(value, rule.warning):
        severity = "warning"
    else:
        severity = "normal"

    logger.debug("classified %s=%s as %s", reading["metric"], value, severity)
    return {"severity": severity, "trail": ["classify"]}


def enrich(state: dict[str, Any], *, enricher: Enricher) -> dict[str, Any]:
    """Attach device context to an alarming reading.

    A transient failure bumps the retry counter and leaves ``enrichment``
    empty, which is what the router uses to send us back around the loop.
    """
    device_id = state["reading"]["device_id"]
    try:
        context = enricher(device_id)
    except TransientEnrichmentError as exc:
        attempt = state.get("retries", 0) + 1
        logger.warning("enrichment attempt %s failed for %s: %s", attempt, device_id, exc)
        return {
            "retries": attempt,
            "errors": [f"enrich: attempt {attempt} failed ({exc})"],
            "trail": ["enrich"],
        }

    return {"enrichment": dict(context), "trail": ["enrich"]}


def escalate(state: dict[str, Any]) -> dict[str, Any]:
    """Raise a P1 alert for a critical reading and mark it as escalated."""
    alert = _build_alert(state, priority="P1", channel="pager")
    alert["ack_deadline_minutes"] = 15
    return {"alert": alert, "status": "escalated", "trail": ["escalate"]}


def notify(state: dict[str, Any], *, sink: Sink) -> dict[str, Any]:
    """Hand the alert to the outbound sink.

    Warnings arrive here without an alert, so one is built on the spot. A
    critical reading keeps the ``escalated`` status it already earned.
    """
    alert = state.get("alert") or _build_alert(state, priority="P2", channel="email")
    sink(alert)
    status = "escalated" if state.get("status") == "escalated" else "notified"
    return {"alert": alert, "status": status, "trail": ["notify"]}


def archive(state: dict[str, Any]) -> dict[str, Any]:
    """Terminal state for healthy readings: nothing to do but record them."""
    reading = state["reading"]
    logger.info(
        "archiving %s %s=%s%s",
        reading["device_id"],
        reading["metric"],
        reading["value"],
        reading["unit"],
    )
    return {"status": "archived", "trail": ["archive"]}


def quarantine(state: dict[str, Any]) -> dict[str, Any]:
    """Terminal state for anything we could not process."""
    errors = state.get("errors") or ["unknown failure"]
    logger.warning("quarantined message %s: %s", state.get("message_id", "?"), errors[-1])
    return {"status": "quarantined", "trail": ["quarantine"]}


def registry_enricher(device_id: str) -> dict[str, Any]:
    """Default enricher: an in-memory lookup with a fallback for new devices."""
    return DEVICE_REGISTRY.get(
        device_id, {"site": "unknown", "line": "unknown", "owner": "ops@nurol.local"}
    )


def logging_sink(alert: dict[str, Any]) -> None:
    """Default sink: log the alert instead of paging anybody."""
    logger.info("ALERT %s", json.dumps(alert, sort_keys=True))


def _build_alert(state: dict[str, Any], *, priority: str, channel: str) -> dict[str, Any]:
    reading = state["reading"]
    context = state.get("enrichment") or {}
    return {
        "message_id": state.get("message_id", ""),
        "device_id": reading["device_id"],
        "metric": reading["metric"],
        "value": reading["value"],
        "unit": reading["unit"],
        "severity": state["severity"],
        "priority": priority,
        "channel": channel,
        "site": context.get("site", "unknown"),
        "owner": context.get("owner", "ops@nurol.local"),
        "raised_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "summary": (
            f"{reading['device_id']} {reading['metric']} at "
            f"{reading['value']}{reading['unit']} ({state['severity']})"
        ),
    }
