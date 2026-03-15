from loguru import logger
import inspect
from events.event_types import EventType
from typing import Callable, Dict, List


class EventBus:
    def __init__(self):
        self.handlers: Dict[str, List[Callable]] = {}

    def subscribe(self, event: EventType, handler: Callable):
        if event not in self.handlers:
            self.handlers[event] = []

        self.handlers[event].append(handler)
        logger.info(
            f"Subscribed to {event}. Total handlers: {len(self.handlers[event])}"
        )

    async def publish(self, event: EventType, **data):
        logger.info(f"Publishing event: {event}")
        if event not in self.handlers:
            logger.warning(f"No handlers for event: {event}")
            return

        for handler in self.handlers[event]:
            result = handler(**data)

            if inspect.isawaitable(result):
                await result
