"""Command line entry point: ``python -m iot_agent``."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from typing import Any

from .graph import build_graph, mermaid
from .nodes import TransientEnrichmentError
from .state import new_state

DEMO_MESSAGES: list[dict[str, Any]] = [
    {"device_id": "pump-01", "metric": "temperature", "value": 41.2, "unit": "C"},
    {"device_id": "press-07", "metric": "vibration", "value": 8.4, "unit": "mm/s"},
    {"device_id": "pump-01", "metric": "temperature", "value": 91.0, "unit": "C"},
    {"device_id": "sensor-12", "metric": "battery", "value": 8.0, "unit": "%"},
    {"device_id": "press-07", "metric": "humidity", "value": 12.0},
    {"device_id": "pump-01", "metric": "temperature"},
]


def flaky_enricher(fail_times: int):
    """An enricher that fails the first N calls, to show the retry loop working."""
    state = {"remaining": fail_times}

    def _enrich(device_id: str) -> dict[str, Any]:
        if state["remaining"] > 0:
            state["remaining"] -= 1
            raise TransientEnrichmentError("device registry timed out")
        from .nodes import registry_enricher

        return registry_enricher(device_id)

    return _enrich


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="iot_agent", description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--message", help="a single JSON message to triage")
    group.add_argument("--demo", action="store_true", help="run the built-in sample messages")
    group.add_argument("--mermaid", action="store_true", help="print the graph as mermaid")
    group.add_argument("--consume", action="store_true", help="consume the RabbitMQ queue")
    parser.add_argument(
        "--flaky",
        type=int,
        default=0,
        metavar="N",
        help="make the first N enrichment calls fail, exercising the retry loop",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="log node activity")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)-8s %(name)s: %(message)s",
    )

    if args.mermaid:
        print(mermaid())
        return 0

    graph = build_graph(enricher=flaky_enricher(args.flaky) if args.flaky else None)

    if args.consume:
        from .consumer import consume

        consume(graph)
        return 0

    messages = [json.dumps(m) for m in DEMO_MESSAGES] if args.demo else [args.message]
    for raw in messages:
        _report(graph.invoke(new_state(raw)))
    return 0


def _report(result: dict[str, Any]) -> None:
    reading = result.get("reading") or {}
    label = f"{reading.get('device_id', '?')} {reading.get('metric', '?')}={reading.get('value', '?')}"
    print(f"{label:<38} {result.get('status', '?'):<12} {' > '.join(result.get('trail', []))}")
    for error in result.get("errors", []):
        print(f"{'':<38} ! {error}")
    alert = result.get("alert")
    if alert:
        print(f"{'':<38} -> {alert['priority']} via {alert['channel']} to {alert['owner']}")


if __name__ == "__main__":
    sys.exit(main())
