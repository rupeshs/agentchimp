from datetime import datetime, timezone
from tools.abstract_tool import AbstractTool


class CurrentTimeTool(AbstractTool):
    @property
    def name(self) -> str:
        return "current_time"

    @property
    def description(self) -> str:
        return "Returns the current date and time."

    def get_parameters_schema(self):
        return {
            "utc": {
                "type": "boolean",
                "description": "Return time in UTC instead of local time",
            }
        }

    def execute(self, **kwargs):
        utc = kwargs.get("utc", False)
        now = datetime.now(timezone.utc) if utc else datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")
