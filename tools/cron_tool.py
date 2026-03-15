from loguru import logger
from tzlocal import get_localzone

from state import get_cron_scheduler
from tools.abstract_tool import AbstractTool
from tools.cron_tasks import do_task

scheduler = get_cron_scheduler()


class CronTool(AbstractTool):
    @property
    def name(self) -> str:
        return "schedule_cron"

    @property
    def description(self) -> str:
        return "Schedule a recurring task using a cron expression."

    def execute(self, **kwargs) -> str:
        """
        Schedule a recurring task using a cron expression.
        Args:
            cron: str, cron expression 'minute hour day month weekday'
            instruction: str, instruction or message to pass to the task
        Returns:
            str, confirmation or error message
        """
        try:
            cron_expr = kwargs.get("cron")
            message = kwargs.get("instruction")

            # Validate cron expression
            parts = cron_expr.split()
            if len(parts) != 5:
                return f"Invalid cron expression: {cron_expr}"

            minute, hour, day, month, weekday = parts

            # Add the job
            job = scheduler.add_job(
                do_task,  # your task path
                trigger="cron",
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=weekday,
                args=[message],
                timezone=get_localzone(),  # local system timezone
            )

            logger.info(f"Cron job scheduled ({cron_expr}) job_id={job.id}")
            print(f"Cron job scheduled ({cron_expr}) job_id={job.id}")
            return f"Cron job scheduled ({cron_expr}) job_id={job.id}"

        except Exception as e:
            logger.error(f"Cron scheduling error: {str(e)}")
            return f"Cron scheduling error: {str(e)}"

    def get_parameters_schema(self):
        return {
            "instruction": {
                "type": "string",
                "description": "Instruction or message for the cron task",
            },
            "cron": {
                "type": "string",
                "description": "Cron expression: minute hour day month weekday (example: '29 20 * * *')",
            },
        }
