from datetime import datetime

from loguru import logger

from events.event_types import EventType
from state import get_scheduler
from tools.abstract_tool import AbstractTool

reminder_scheduler = get_scheduler()


class SchedulerTool(AbstractTool):
    @property
    def name(self) -> str:
        return "schedule_task"

    @property
    def description(self) -> str:
        return "Add a one-time reminder using date trigger,useful for set reminders"

    def execute(
        self,
        message: str,
        mode: str,
        run_at: str = None,
    ) -> str:
        try:

            async def reminder(msg):
                print(f"[REMINDER] {msg} @ {datetime.now()}")
                new_msg = f"[REMINDER]⏰ {msg} "
                await self.event_bus.publish(EventType.SEND_MESSAGE, message=new_msg)

            # ONE-TIME
            if mode == "once":
                run_time = datetime.fromisoformat(run_at)

                job = reminder_scheduler.add_job(
                    reminder,
                    "date",
                    run_date=run_time,
                    args=[message],
                )

                return f"One-time reminder scheduled at {run_time} (job_id={job.id})"

            else:
                return "Invalid mode. Use 'once' for one-time reminders."

        except Exception as e:
            logger.error(f"Reminder scheduler error: {str(e)}")
            return f"Scheduler error: {str(e)}"

    def get_parameters_schema(self):
        return {
            "message": {
                "type": "string",
                "description": "Reminder message",
            },
            "mode": {
                "type": "string",
                "enum": ["once"],
                "description": "Scheduling mode",
            },
            "run_at": {
                "type": "string",
                "description": "Datetime for one-time reminder (YYYY-MM-DDTHH:MM:SS)",
            },
        }

    def to_schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.get_parameters_schema(),
                    "required": ["message", "mode"],
                },
            },
        }
