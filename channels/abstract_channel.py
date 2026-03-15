from abc import ABC, abstractmethod


class AbstractChannel(ABC):
    """Abstract base class for message channels."""

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def send(self, message: str):
        pass
