from abc import ABC, abstractmethod
from llm.token_usage import TokenUsage
from agent.message import Message


class AbstractLLMAdapter(ABC):
    @abstractmethod
    def generate(
        self,
        messages: list[Message],
        tools: list[dict] = None,
    ) -> Message:
        pass

    @abstractmethod
    def get_token_usage(self) -> TokenUsage:
        pass
