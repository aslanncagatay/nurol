"""RabbitMQ bridge: feed messages from the platform queue into the graph.

sender-service publishes ``CustomMessage`` payloads to the ``message_exchange``
topic exchange. Rather than sharing receiver-service's queue -- which would make
the two services compete for messages -- this consumer binds its own queue to
the same exchange and routing key, so both see every message.

``pika`` is imported lazily so the graph and its tests stay dependency free.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from .graph import build_graph

logger = logging.getLogger(__name__)

EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "message_exchange")
ROUTING_KEY = os.getenv("RABBITMQ_ROUTING_KEY", "message_routingKey")
QUEUE = os.getenv("RABBITMQ_QUEUE", "iot_agent_queue")
HOST = os.getenv("RABBITMQ_HOST", "rabbitmq-svc")
PORT = int(os.getenv("RABBITMQ_PORT", "80"))
USER = os.getenv("RABBITMQ_USERNAME", "guest")
PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")


def consume(graph: Any | None = None) -> None:  # pragma: no cover - needs a broker
    """Consume the platform queue forever, running each message through the graph."""
    import pika  # imported here so the module stays optional

    graph = graph or build_graph()
    credentials = pika.PlainCredentials(USER, PASSWORD)
    parameters = pika.ConnectionParameters(host=HOST, port=PORT, credentials=credentials)

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
    channel.queue_declare(queue=QUEUE, durable=True)
    channel.queue_bind(exchange=EXCHANGE, queue=QUEUE, routing_key=ROUTING_KEY)

    def on_message(channel_, method, _properties, body: bytes) -> None:
        result = handle_body(body, graph)
        logger.info(
            "message %s -> %s (%s)",
            result.get("message_id") or "?",
            result.get("status"),
            " > ".join(result.get("trail", [])),
        )
        channel_.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE, on_message_callback=on_message)
    logger.info("consuming %s on %s:%s", QUEUE, HOST, PORT)
    channel.start_consuming()


def handle_body(body: bytes | str, graph: Any) -> dict[str, Any]:
    """Run one broker message through the graph, never raising back at the broker."""
    from .state import new_state

    raw = body.decode("utf-8", errors="replace") if isinstance(body, bytes) else body
    try:
        return graph.invoke(new_state(raw))
    except Exception:  # a poison message must not kill the consumer
        logger.exception("triage failed for message %s", _peek_id(raw))
        return {"status": "quarantined", "trail": ["consumer"], "errors": ["consumer: crashed"]}


def _peek_id(raw: str) -> str:
    try:
        return str(json.loads(raw).get("messageId", "?"))
    except Exception:
        return "?"
