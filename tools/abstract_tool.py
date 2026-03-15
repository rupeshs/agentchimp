from abc import ABC, abstractmethod
from events.eventbus import EventBus


class AbstractTool(ABC):
    """Abstract base class for tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name used in function calls."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the tool does."""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> str:
        pass

    def set_eventbus(self, event_bus: EventBus):
        self.event_bus = event_bus

    def to_schema(self) -> dict:
        """Convert to OpenAI function calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.get_parameters_schema(),
                    "required": list(self.get_parameters_schema().keys()),
                },
            },
        }

    @abstractmethod
    def get_parameters_schema(self) -> dict:
        """Return a JSON schema dict describing the tool's parameters.
        Example:
        {
            "city": {"type": "string", "description": "City name"},
            "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
        }
        """
        pass
