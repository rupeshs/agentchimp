import asyncio

from rich.console import Console
from rich.markdown import Markdown

from channels.abstract_channel import AbstractChannel
from constants import AGENT_NAME
from events.event_types import EventType
from events.eventbus import EventBus


class TUIChannel(AbstractChannel):
    def __init__(
        self,
        event_bus: EventBus,
        console: Console,
    ):
        super().__init__()
        self.session_id = "cli"
        self.console = console
        self.event_bus = event_bus

    async def start(self):
        self.console.print("AgentChimp is ready. Type 'bye' to shutdown.\n")
        try:
            while True:
                self.console.print("[cyan]You:[white] ", end="")
                try:
                    user_input = await asyncio.to_thread(input)
                except EOFError:
                    self.console.print("\n[red]Input closed. Exiting.")
                    break

                if user_input.lower() in ["exit", "bye", "quit"]:
                    self.console.print("[yellow4]Goodbye!")
                    await self.event_bus.publish(EventType.SHUTDOWN)
                    break

                if not user_input.strip():
                    continue

                await self.event_bus.publish(
                    EventType.PROCESS_MESSAGE, user_input=user_input
                )

        except KeyboardInterrupt:
            self.console.print("\n[red]Interrupted. Exiting.")

    async def send(self, message: str):
        md = Markdown(message)
        self.console.print(f"[yellow]{AGENT_NAME} :[white] ", end="")
        self.console.print(md)
