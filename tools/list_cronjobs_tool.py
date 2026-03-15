from tools.abstract_tool import AbstractTool
from state import get_cron_scheduler

scheduler = get_cron_scheduler()


class ListCronJobsTool(AbstractTool):
    @property
    def name(self) -> str:
        return "list_cron_jobs"

    @property
    def description(self) -> str:
        return "List all scheduled cron jobs with their schedule and next run time."

    def execute(self, **kwargs) -> str:
        try:
            jobs = scheduler.get_jobs()

            if not jobs:
                return "No cron jobs scheduled."

            lines = []
            lines.append("⏰ **Scheduled Cron Jobs**\n")

            for job in jobs:
                instruction = job.args[0] if job.args else "No instruction"

                lines.append(f"• Job ID: {job.id}\n  Description: {instruction}\n")

            return "\n".join(lines)

        except Exception as e:
            return f"Error listing cron jobs: {str(e)}"

    def get_parameters_schema(self):
        return {}
