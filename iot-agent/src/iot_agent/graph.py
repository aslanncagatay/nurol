"""The triage state machine itself: nodes, transitions and the compiled graph.

    START -> ingest -> validate -> classify -+-> archive              -> END
                |          |                 |
                |          |                 +-> enrich -+-> escalate -> notify -> END
                |          |                     ^   |   |
                |          |                     +---+   +-> notify            -> END
                |          |                  (retry)
                +----------+------------------------------------------> quarantine -> END
"""

from __future__ import annotations

from functools import partial
from typing import Any

from langgraph.graph import END, START, StateGraph

from . import nodes
from .config import DEFAULT_MAX_RETRIES, DEFAULT_RULES, MetricRule
from .nodes import Enricher, Sink
from .state import TriageState, new_state


def route_after_ingest(state: dict[str, Any]) -> str:
    """A message we could not parse never reaches the rest of the machine."""
    return "quarantine" if state.get("errors") else "validate"


def route_after_validate(state: dict[str, Any]) -> str:
    """Same for a message that parsed but does not describe a usable reading."""
    return "quarantine" if state.get("errors") else "classify"


def route_by_severity(state: dict[str, Any]) -> str:
    """Healthy readings are filed away; alarming ones get device context first."""
    return "archive" if state.get("severity") == "normal" else "enrich"


def route_after_enrich(state: dict[str, Any], *, max_retries: int) -> str:
    """Loop back while enrichment keeps failing, then give up.

    Note this branches on ``enrichment`` rather than on ``errors``: the error
    list is append-only, so a failed attempt that later succeeds must not keep
    the message stuck in the retry loop.
    """
    if state.get("enrichment"):
        return "escalate" if state.get("severity") == "critical" else "notify"
    if state.get("retries", 0) >= max_retries:
        return "quarantine"
    return "enrich"


def build_graph(
    *,
    rules: dict[str, MetricRule] | None = None,
    enricher: Enricher | None = None,
    sink: Sink | None = None,
    max_retries: int = DEFAULT_MAX_RETRIES,
    checkpointer: Any | None = None,
):
    """Wire the nodes together and compile the state machine.

    Every dependency has a working default, so ``build_graph()`` on its own
    gives a runnable graph; tests pass their own rules, enricher or sink.
    """
    rules = rules if rules is not None else DEFAULT_RULES
    enricher = enricher or nodes.registry_enricher
    sink = sink or nodes.logging_sink

    builder = StateGraph(TriageState)
    builder.add_node("ingest", nodes.ingest)
    builder.add_node("validate", partial(nodes.validate, rules=rules))
    builder.add_node("classify", partial(nodes.classify, rules=rules))
    builder.add_node("enrich", partial(nodes.enrich, enricher=enricher))
    builder.add_node("escalate", nodes.escalate)
    builder.add_node("notify", partial(nodes.notify, sink=sink))
    builder.add_node("archive", nodes.archive)
    builder.add_node("quarantine", nodes.quarantine)

    builder.add_edge(START, "ingest")
    builder.add_conditional_edges(
        "ingest", route_after_ingest, {"validate": "validate", "quarantine": "quarantine"}
    )
    builder.add_conditional_edges(
        "validate", route_after_validate, {"classify": "classify", "quarantine": "quarantine"}
    )
    builder.add_conditional_edges(
        "classify", route_by_severity, {"archive": "archive", "enrich": "enrich"}
    )
    builder.add_conditional_edges(
        "enrich",
        partial(route_after_enrich, max_retries=max_retries),
        {
            "enrich": "enrich",
            "escalate": "escalate",
            "notify": "notify",
            "quarantine": "quarantine",
        },
    )
    builder.add_edge("escalate", "notify")
    builder.add_edge("notify", END)
    builder.add_edge("archive", END)
    builder.add_edge("quarantine", END)

    return builder.compile(checkpointer=checkpointer)


def triage(
    raw: str,
    *,
    message_id: str = "",
    graph: Any | None = None,
    thread_id: str | None = None,
    **build_kwargs: Any,
) -> dict[str, Any]:
    """Run a single raw message through the machine and return the end state."""
    graph = graph or build_graph(**build_kwargs)
    config = {"configurable": {"thread_id": thread_id}} if thread_id else None
    return graph.invoke(new_state(raw, message_id), config=config)


def mermaid() -> str:
    """Render the compiled graph as a mermaid diagram."""
    return build_graph().get_graph().draw_mermaid()
