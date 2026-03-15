from agent.message import Message


class ShortTermMemory:
    def __init__(
        self,
        max_size: int = 6,
        file_path: str = "short_term_memory.jsonl",
    ):
        self.messages = []
        self.max_size = max_size
        self.file_path = file_path
        self.prv_summary = ""

    def add_message(self, message: Message):
        self.messages.append(message)
        # self._persist_to_file(self.file_path)

    def get_messages(self) -> list[Message]:
        return self.messages.copy()

    def get_size(self) -> int:
        return len(self.messages)

    def _persist_to_file(self, filename: str):
        with open(filename, "w", encoding="utf-8") as f:
            for msg in self.messages:
                f.write(msg.model_dump_json(exclude_none=True) + "\n")

    def clear(self):
        self.messages = []
        self._persist_to_file(self.file_path)

    def get_recent_messages(
        self,
        messages: list[Message],
        max_recent: int = 6,
    ):
        if not messages:
            return []

        recent = []
        i = len(messages) - 1

        while i >= 0 and len(recent) < max_recent:
            msg = messages[i]
            recent.append(msg)

            if msg.role == "tool" and i > 0:
                prev = messages[i - 1]
                if prev.role == "assistant":
                    recent.append(prev)
                    i -= 1

            i -= 1

        recent.reverse()
        return recent

    def refresh_context_window(self):
        recent_msgs = self.get_recent_messages(self.messages, self.max_size)
        self.messages.clear()
        self.messages = recent_msgs
