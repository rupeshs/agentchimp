from json import dumps, loads

from openai import OpenAI

from agent.message import Message, ToolCall
from llm.token_usage import TokenUsage
from loguru import logger


class OpenAIAdapter:
    def __init__(
        self,
        model: str,
        base_url: str,
        api_key: str,
        temperature: float = 0.0,
    ):
        self.model = model
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        self.token_usage = None
        self.temperature = temperature

    def _to_messages(self, messages: list[Message]) -> list[dict]:
        provider_msgs = []
        for message in messages:
            if message.role == "tool":
                msg = {
                    "role": message.role,
                    "content": message.content or "",
                    "tool_call_id": message.tool_call_id,
                }
            else:
                msg = {"role": message.role, "content": message.content or ""}

            if message.tool_calls:
                msg["tool_calls"] = [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.name,
                            "arguments": dumps(tool_call.arguments),
                        },
                    }
                    for tool_call in message.tool_calls
                ]

            provider_msgs.append(msg)
        return provider_msgs

    def _from_response(self, response) -> Message:
        msg = response.choices[0].message
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            tool_calls = [
                ToolCall(
                    id=tool_call.id,
                    name=tool_call.function.name,
                    arguments=loads(tool_call.function.arguments),
                )
                for tool_call in msg.tool_calls
            ]
            return Message(role="assistant", tool_calls=tool_calls)
        return Message(role="assistant", content=msg.content)

    def generate(
        self,
        messages: list[Message],
        tools: list[dict] = None,
    ) -> Message:
        try:
            messages = self._to_messages(messages)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False,
                temperature=self.temperature,
                tools=tools,
            )
            msg = self._from_response(response)
            if hasattr(response, "usage") and response.usage:
                self.token_usage = TokenUsage(
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                )

            return msg
        except AttributeError as e:
            logger.error(f"[Error] Attribute error: {e}")
            return Message(
                role="assistant",
                content=f"An AttributeError occurred while generating the response.{e}",
            )

        except TypeError as e:
            logger.error(f"[Error] Type error: {e}")
            return Message(
                role="assistant",
                content=f"An TypeError occurred while generating the response.{e}",
            )

        except Exception as e:
            logger.error(f"[Error] Unexpected error during generation: {e}")
            return Message(
                role="assistant",
                content=f"An error occurred while generating the response.{e}",
            )

    def get_token_usage(self) -> TokenUsage:
        return self.token_usage
