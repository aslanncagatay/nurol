"""End-to-end tests for the triage state machine: one per path through the graph."""

from __future__ import annotations

import json

import pytest
from langgraph.checkpoint.memory import InMemorySaver

from iot_agent import TransientEnrichmentError, build_graph, new_state
from iot_agent.config import DEFAULT_MAX_RETRIES


@pytest.fixture
def sink():
    """A sink that records every alert it is handed."""
    alerts: list[dict] = []
    return alerts, alerts.append


def run(raw, sink=None, **kwargs):
    graph = build_graph(sink=sink, **kwargs)
    return graph.invoke(new_state(raw if isinstance(raw, str) else json.dumps(raw)))


def test_normal_reading_is_archived(sink):
    alerts, record = sink
    result = run({"device_id": "pump-01", "metric": "temperature", "value": 41.2}, record)

    assert result["severity"] == "normal"
    assert result["status"] == "archived"
    assert result["trail"] == ["ingest", "validate", "classify", "archive"]
    assert alerts == []


def test_warning_reading_is_notified_without_escalating(sink):
    alerts, record = sink
    result = run({"device_id": "press-07", "metric": "vibration", "value": 8.4}, record)

    assert result["severity"] == "warning"
    assert result["status"] == "notified"
    assert result["trail"] == ["ingest", "validate", "classify", "enrich", "notify"]
    assert [a["priority"] for a in alerts] == ["P2"]
    assert alerts[0]["site"] == "Ankara-Plant"


def test_critical_reading_is_escalated_then_notified(sink):
    alerts, record = sink
    result = run({"device_id": "pump-01", "metric": "temperature", "value": 91.0}, record)

    assert result["severity"] == "critical"
    assert result["status"] == "escalated"
    assert result["trail"] == ["ingest", "validate", "classify", "enrich", "escalate", "notify"]
    assert alerts[0]["priority"] == "P1"
    assert alerts[0]["channel"] == "pager"
    assert alerts[0]["ack_deadline_minutes"] == 15


def test_battery_thresholds_trigger_below_the_limit(sink):
    alerts, record = sink
    result = run({"device_id": "sensor-12", "metric": "battery", "value": 8.0}, record)

    assert result["severity"] == "critical"
    assert result["status"] == "escalated"


def test_custom_message_envelope_is_unwrapped(sink):
    """sender-service wraps the reading in CustomMessage, with a JSON string body."""
    _, record = sink
    envelope = {
        "messageId": "abc-123",
        "message": json.dumps({"device_id": "pump-01", "metric": "temperature", "value": 91.0}),
        "messageDate": "2026-08-22T09:00:00Z",
    }
    result = run(envelope, record)

    assert result["message_id"] == "abc-123"
    assert result["status"] == "escalated"


def test_malformed_json_is_quarantined(sink):
    alerts, record = sink
    result = run("{not json", record)

    assert result["status"] == "quarantined"
    assert result["trail"] == ["ingest", "quarantine"]
    assert "not valid JSON" in result["errors"][0]
    assert alerts == []


def test_missing_field_is_quarantined():
    result = run({"device_id": "pump-01", "metric": "temperature"})

    assert result["status"] == "quarantined"
    assert result["trail"] == ["ingest", "validate", "quarantine"]
    assert result["errors"] == ["validate: missing field 'value'"]


def test_unknown_metric_is_quarantined():
    result = run({"device_id": "press-07", "metric": "humidity", "value": 12.0})

    assert result["status"] == "quarantined"
    assert result["errors"] == ["validate: unknown metric 'humidity'"]


def test_implausible_value_is_quarantined():
    result = run({"device_id": "pump-01", "metric": "temperature", "value": 5000})

    assert result["status"] == "quarantined"
    assert "outside plausible range" in result["errors"][0]


def test_enrichment_retries_then_succeeds(sink):
    """A transient failure loops back into enrich instead of failing the message."""
    alerts, record = sink
    attempts = {"n": 0}

    def flaky(device_id: str) -> dict:
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise TransientEnrichmentError("registry timeout")
        return {"site": "Ankara-Plant", "owner": "maintenance@nurol.local"}

    result = run(
        {"device_id": "pump-01", "metric": "temperature", "value": 91.0}, record, enricher=flaky
    )

    assert attempts["n"] == 3
    assert result["retries"] == 2
    assert result["status"] == "escalated"
    assert result["trail"].count("enrich") == 3
    assert len(result["errors"]) == 2
    assert len(alerts) == 1


def test_enrichment_gives_up_after_max_retries(sink):
    alerts, record = sink

    def always_fails(device_id: str) -> dict:
        raise TransientEnrichmentError("registry down")

    result = run(
        {"device_id": "pump-01", "metric": "temperature", "value": 91.0}, record, enricher=always_fails
    )

    assert result["retries"] == DEFAULT_MAX_RETRIES
    assert result["status"] == "quarantined"
    assert result["trail"].count("enrich") == DEFAULT_MAX_RETRIES
    assert result["trail"][-1] == "quarantine"
    assert alerts == []


def test_checkpointer_keeps_state_per_thread():
    """With a checkpointer each message gets its own resumable thread."""
    graph = build_graph(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "device-pump-01"}}

    result = graph.invoke(
        new_state(json.dumps({"device_id": "pump-01", "metric": "temperature", "value": 91.0})),
        config=config,
    )

    assert result["status"] == "escalated"
    snapshot = graph.get_state(config)
    assert snapshot.values["status"] == "escalated"
    assert snapshot.values["trail"][-1] == "notify"


def test_graph_topology_is_stable():
    """Guards the diagram in the README against silent drift."""
    graph = build_graph().get_graph()
    nodes = set(graph.nodes) - {"__start__", "__end__"}

    assert nodes == {
        "ingest",
        "validate",
        "classify",
        "enrich",
        "escalate",
        "notify",
        "archive",
        "quarantine",
    }
    assert "graph TD;" in graph.draw_mermaid()
