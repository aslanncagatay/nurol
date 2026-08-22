"""Metric rules and the device registry used by the triage nodes.

Both are plain data so they can be swapped out in tests or loaded from the
config-server later on.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Direction = Literal["above", "below"]

DEFAULT_MAX_RETRIES = 3


@dataclass(frozen=True)
class MetricRule:
    """Thresholds for a single metric.

    ``direction`` says which way is bad: a temperature is alarming when it
    climbs *above* the limit, a battery level when it drops *below* it.
    """

    unit: str
    warning: float
    critical: float
    direction: Direction = "above"
    valid_min: float = -1_000_000.0
    valid_max: float = 1_000_000.0

    def in_range(self, value: float) -> bool:
        """Is the value physically plausible for this metric?"""
        return self.valid_min <= value <= self.valid_max

    def breaches(self, value: float, limit: float) -> bool:
        """Has the value crossed the given limit in the alarming direction?"""
        return value >= limit if self.direction == "above" else value <= limit


DEFAULT_RULES: dict[str, MetricRule] = {
    "temperature": MetricRule(
        unit="C", warning=60.0, critical=85.0, valid_min=-50.0, valid_max=200.0
    ),
    "vibration": MetricRule(
        unit="mm/s", warning=7.1, critical=11.2, valid_min=0.0, valid_max=100.0
    ),
    "pressure": MetricRule(
        unit="bar", warning=8.0, critical=10.0, valid_min=0.0, valid_max=25.0
    ),
    "battery": MetricRule(
        unit="%",
        warning=25.0,
        critical=10.0,
        direction="below",
        valid_min=0.0,
        valid_max=100.0,
    ),
}

DEVICE_REGISTRY: dict[str, dict[str, str]] = {
    "pump-01": {
        "site": "Ankara-Plant",
        "line": "assembly-a",
        "owner": "maintenance@nurol.local",
    },
    "press-07": {
        "site": "Ankara-Plant",
        "line": "assembly-b",
        "owner": "maintenance@nurol.local",
    },
    "sensor-12": {
        "site": "Izmir-Depot",
        "line": "storage",
        "owner": "facility@nurol.local",
    },
}
