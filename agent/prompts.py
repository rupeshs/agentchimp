from platform import system

from tzlocal import get_localzone


def get_system_prompt_extension():
    prompt = f"""

## Additional guidelines
- You are running on a {system()} system, so you can only use tools that are compatible with this OS
- Do not infer or guess timezone yourself,you are in timezone {get_localzone()}

"""
    return prompt
