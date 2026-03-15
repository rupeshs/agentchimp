from loguru import logger
from rich.console import Console

from agent.message import Message, ToolCall
from agent.prompts import get_system_prompt_extension
from config import MAX_PROMPT_TOKENS
from events.event_types import EventType
from events.eventbus import EventBus
from llm.abstract_llm_adapter import AbstractLLMAdapter
from memory.preferences_memory import PreferencesMemory
from memory.short_term_memory import ShortTermMemory
from paths import (
    get_agent_file_path,
    get_soul_file_path,
    get_workspace_path,
)
from skills.skills import Skills
from tools.abstract_tool import AbstractTool


class Agent:
    def __init__(
        self,
        llm_adapter: AbstractLLMAdapter,
        short_term_memory: ShortTermMemory,
        preferences_memory: PreferencesMemory,
        event_bus: EventBus,
        max_iterations: int = 10,
    ):
        self.console = Console()
        self.llm_adapter = llm_adapter
        self.total_tokens = 0
        self.tools = []
        self.tool_map = {}
        self.max_iterations = max_iterations
        self.short_term_memory = short_term_memory
        self.system_prompt = self.get_system_prompt()
        self.preferences_memory = preferences_memory
        self.event_bus = event_bus

    def get_system_prompt(self):
        prompt = self.load_soul_file()
        prompt += self.load_agent_file()
        prompt += self.load_skill_catalog()
        prompt += get_system_prompt_extension()
        return prompt

    def load_soul_file(self):
        with open(get_soul_file_path(), "r", encoding="utf-8") as f:
            content = f.read()
        return content

    def load_agent_file(self):
        with open(get_agent_file_path(), "r", encoding="utf-8") as f:
            content = f.read()
        return content

    def _register_tool(self, name: str, func: AbstractTool):
        self.tool_map[name] = func

    def register_tools(self, tools: list[AbstractTool]):
        for tool in tools:
            self._register_tool(tool.name, tool.execute)
            tool_schema = tool.to_schema()
            self.tools.append(tool_schema)

    async def think(self, user_input: str) -> None:
        if user_input:
            response = self._loop(user_input)
            await self.event_bus.publish(EventType.SEND_MESSAGE, message=response)

    def _get_tokens_usage(self):
        token_usage = self.llm_adapter.get_token_usage()
        percentage = (token_usage.total_tokens / MAX_PROMPT_TOKENS) * 100
        return f"\n\n > Tokens: {token_usage.total_tokens}({int(percentage)}%) "

    def _check_token_limit(self):
        token_usage = self.llm_adapter.get_token_usage()
        if token_usage and token_usage.total_tokens > MAX_PROMPT_TOKENS * 0.75:
            self.console.print(
                "[yellow] Refreshing context window, as token limit reached"
            )
            self.preferences_memory.extract_and_update_preferences(
                self.short_term_memory.get_messages()
            )
            self.short_term_memory.refresh_context_window()

    def get_system_prompt_with_pref(self):
        preferences = self.preferences_memory.build_preference_prompt()
        if preferences:
            return self.system_prompt + preferences
        else:
            return self.system_prompt

    def _loop(self, user_input: str):
        try:
            user_msg = Message(role="user", content=user_input)
            self.short_term_memory.add_message(user_msg)
            is_tool_call = False
            tool_call_id = None

            with self.console.status("[bold green]🧠Thinking...") as status:
                for iteration in range(self.max_iterations):
                    is_tool_call = False
                    tool_call_id = None
                    count = iteration + 1
                    status.update(
                        f"[bold green]{count}/{self.max_iterations} - 🧠Thinking..."
                    )
                    llm_response = self.llm_adapter.generate(
                        [
                            Message(
                                role="system",
                                content=self.get_system_prompt_with_pref(),
                            ),
                        ]
                        + self.short_term_memory.get_messages(),
                        self.tools,
                    )

                    self.short_term_memory.add_message(llm_response)
                    if llm_response.tool_calls:
                        for tool_call in llm_response.tool_calls:
                            is_tool_call = True
                            tool_call_id = tool_call.id
                            status.update(
                                f"[green]> I decided to call tool: {tool_call.name}"
                            )
                            result = self._invoke_tool(tool_call)

                            tool_msg = Message(
                                role="tool",
                                content=result,
                                tool_call_id=tool_call.id,
                            )

                            self.short_term_memory.add_message(tool_msg)

                    elif llm_response.content:
                        self._check_token_limit()
                        return llm_response.content.strip() + self._get_tokens_usage()
                    else:
                        return "NOP"

        except Exception as e:
            if is_tool_call:
                self.short_term_memory.add_message(
                    Message(
                        role="tool",
                        tool_call_id=tool_call_id,
                        content=f"Tool call failed {e}",
                    )
                )
            self.console.print(f"[red]Error: {e}")
            logger.error(f"Error during think loop: {e}")

    def _invoke_tool(self, tool_call: ToolCall) -> str:
        tool_name = tool_call.name
        tool_func = self.tool_map.get(tool_name)
        if not tool_func:
            print(f"Tool '{tool_name}' not found")
            return f"Error: Tool '{tool_name}' not found"

        self.console.print(
            f"> Invoking tool '{tool_name}' with arguments: {tool_call.arguments}"
        )
        result = tool_func(**tool_call.arguments)
        return result

    def load_skill_catalog(self) -> str:
        skills = Skills(get_workspace_path() / "skills")
        catalog = skills.get_skill_catalog()
        for skill_name in skills.get_skills().keys():
            logger.info(f"Loaded skill: {skill_name}")
        logger.info(f"{len(skills.get_skills().keys())} skills available")
        return catalog

    def shutdown(self):
        self.console.print("[bold red]🛑 Starting shutdown sequence...")
        self.preferences_memory.extract_and_update_preferences(
            self.short_term_memory.get_messages()
        )
        self.console.print("[bold green]✅ Shutdown completed")
