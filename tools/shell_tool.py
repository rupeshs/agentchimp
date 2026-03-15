from tools.abstract_tool import AbstractTool
from config import ALLOWED_COMMANDS


class ShellTool(AbstractTool):
    """Tool to run shell commands."""

    def __init__(self):
        self.allowed_commands = list(map(str.lower, ALLOWED_COMMANDS.split(",")))

    @property
    def name(self) -> str:
        return "run_command"

    @property
    def description(self) -> str:
        return "Run a shell command"

    def get_parameters_schema(self) -> dict:
        return {
            "cmd": {
                "type": "string",
                "description": "Command to run",
            },
        }

    def execute(self, **kwargs) -> str:
        cmd = kwargs.get("cmd")
        if not cmd:
            return "Error: 'cmd' parameter is required."

        if cmd.lower().split()[0] not in self.allowed_commands:
            print(f"You are not allowed to run the command: {cmd}")
            return "You are not allowed to run the command"

        import subprocess

        try:
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                return f"Error:\n{result.stderr}"
            return result.stdout.strip()

        except Exception as e:
            return f"Exception: {str(e)}"
