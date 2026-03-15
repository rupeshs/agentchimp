from platform import system

from agent.utils import get_current_datetime


def get_system_prompt_extension():
    prompt = f"""

## Additional guidelines
- You are running on a {system()} system, so you can only use tools that are compatible with this OS
- Current datetime with timezone: {get_current_datetime()}
"""
    return prompt
