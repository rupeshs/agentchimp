from tools.abstract_tool import AbstractTool
from state import get_cron_scheduler

scheduler = get_cron_scheduler()


class DeleteCronJobTool(AbstractTool):
    @property
    def name(self) -> str:
        return "delete_cron_job"

    @property
    def description(self) -> str:
        return "Delete a scheduled cron job using its job_id."

    def execute(self, job_id: str) -> str:
        try:
            job = scheduler.get_job(job_id)

            if not job:
                return f"❌ No cron job found with id: {job_id}"

            scheduler.remove_job(job_id)

            return f"🗑️ Cron job {job_id} deleted successfully."

        except Exception as e:
            return f"Error deleting cron job: {str(e)}"

    def get_parameters_schema(self):
        return {
            "job_id": {
                "type": "string",
                "description": "The job ID of the cron job to delete",
            }
        }
