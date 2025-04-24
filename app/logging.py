import logging
import queue
from logging.handlers import QueueHandler, QueueListener
from asgi_correlation_id import CorrelationIdFilter


log_queue = queue.Queue()
queue_handler = QueueHandler(log_queue)
console_handler = logging.StreamHandler()

correlation_id_filter = CorrelationIdFilter(uuid_length=32, default_value="-")
queue_handler.addFilter(correlation_id_filter)

listener = QueueListener(log_queue, console_handler)


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s #%(correlation_id)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        handlers=[queue_handler],
    )

    listener.start()
