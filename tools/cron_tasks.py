from datetime import datetime

from loguru import logger

from state import get_event_bus

event_bus = get_event_bus()


async def do_task(message):
    logger.info(f"[CRON] {message} @ {datetime.now()}")
    await event_bus.publish("process_message", user_input=message)
