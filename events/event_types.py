from enum import Enum


class EventType(str, Enum):
    PROCESS_MESSAGE = "process_message"
    SEND_MESSAGE = "send_message"
    SHUTDOWN = "shutdown"
