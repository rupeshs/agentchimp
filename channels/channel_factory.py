from channels.abstract_channel import AbstractChannel
from channels.telegram_channel import TelegramChannel
from channels.tui_channel import TUIChannel
from channels.channel_type import ChannelType
from rich.console import Console
from events.eventbus import EventBus


class ChannelFactory:
    @staticmethod
    def create_channel(
        channel_type: ChannelType,
        event_bus: EventBus,
        console: Console,
    ) -> AbstractChannel:
        if channel_type == ChannelType.TELEGRAM:
            return TelegramChannel(event_bus)
        elif channel_type == ChannelType.TUI:
            return TUIChannel(event_bus, console)
        else:
            supported = [ChannelType.TELEGRAM.value, ChannelType.TUI.value]
            raise ValueError(
                f"Unknown channel type: {channel_type} , supported channels: {supported}"
            )
