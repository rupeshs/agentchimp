import argparse
import asyncio
from os import getenv
from sys import stderr

from loguru import logger
from rich.console import Console
from tzlocal import get_localzone

from agent.agent import Agent
from agent.tools import load_tools
from channels.channel_factory import ChannelFactory
from config import (
    LLM_API_KEY,
    LLM_BASE_URL,
    LLM_MODEL,
    LLM_TEMPERATURE,
    MAX_PROMPT_TOKENS,
    MAX_RECENT_MESSAGES_TO_KEEP,
    AGENT_MAX_ITERATIONS,
)
from events.event_types import EventType
from events.eventbus import EventBus
from llm.openai_adapter import OpenAIAdapter
from memory.preferences_memory import PreferencesMemory
from memory.short_term_memory import ShortTermMemory
from paths import get_short_term_memory_file_path, get_workspace_path
from state import get_event_bus
from sys import exit
from os import path


parser = argparse.ArgumentParser()
parser.add_argument("--channel", type=str, help="Channel to use default=tui")
args = parser.parse_args()
channel_name = args.channel or getenv("CHANNEL", "tui")

logger.remove()
logger.add(
    stderr,
    format="<green>{time:YYYY-MM-DD hh:mm:ss.SSS A}</green> [{level}] {message}",
)
banner = r"""[bold green]
        █████╗  ██████╗ ███████╗███╗   ██╗████████╗
        ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝
        ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   
        ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   
        ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   
        ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   

                    C H I M P 🐵
            A simple autonomous personal AI Agent
        """


def load_agent_tools(event_bus: EventBus):
    tools_dict = load_tools()
    tools = list(tools_dict.values())
    for tool in tools:
        tool.set_eventbus(event_bus)
        logger.info(f"Loaded tool: {tool.name}")
    logger.info(f"{len(tools)} tools available")
    return tools


async def main() -> None:
    console = Console()
    console.print(banner)

    if not path.exists(".env"):
        logger.error("❌ .env config file not found, please refer .env.sample file")
        exit(1)
    if not LLM_BASE_URL or not LLM_MODEL:
        logger.error("❌ LLM_BASE_URL and LLM_MODEL must be set.")
        exit(1)
    if not LLM_API_KEY:
        logger.error("❌ LLM_API_KEY is missing, please set it in .env file")
        exit(1)
    logger.info("Starting AgentChimp")
    logger.info(f"Channel: {channel_name}")
    local_tz = get_localzone()
    logger.info(f"Local timezone: {local_tz}")
    logger.info(f"Workspace: {get_workspace_path()}")
    logger.info(f"LLM Base URL: {LLM_BASE_URL}")
    logger.info(f"LLM Model: {LLM_MODEL}")
    logger.info(f"Max Tokens: {MAX_PROMPT_TOKENS}")

    llm = OpenAIAdapter(
        LLM_MODEL,
        LLM_BASE_URL,
        LLM_API_KEY,
        LLM_TEMPERATURE,
    )

    llm_mem = OpenAIAdapter(
        LLM_MODEL,
        LLM_BASE_URL,
        LLM_API_KEY,
        LLM_TEMPERATURE,
    )
    event_bus = get_event_bus()
    preferences_memory = PreferencesMemory(llm_mem)
    short_term_memory = ShortTermMemory(
        max_size=MAX_RECENT_MESSAGES_TO_KEEP,
        file_path=get_short_term_memory_file_path(),
    )
    agent = Agent(
        llm_adapter=llm,
        short_term_memory=short_term_memory,
        preferences_memory=preferences_memory,
        event_bus=event_bus,
        max_iterations=AGENT_MAX_ITERATIONS,
    )

    agent.register_tools(tools=load_agent_tools(event_bus))
    event_bus.subscribe(EventType.PROCESS_MESSAGE, agent.think)
    event_bus.subscribe(EventType.SHUTDOWN, agent.shutdown)

    try:
        channel = ChannelFactory.create_channel(
            channel_name,
            event_bus,
            console,
        )
        event_bus.subscribe(EventType.SEND_MESSAGE, channel.send)
        await channel.start()
    except Exception as e:
        logger.error(f"Error starting channel: {e}")
        await event_bus.publish(EventType.SHUTDOWN)


async def cleanup():
    await get_event_bus().publish(EventType.SHUTDOWN)


if __name__ == "__main__":
    with asyncio.Runner() as runner:
        try:
            runner.run(main())
        except KeyboardInterrupt:
            asyncio.run(cleanup())
