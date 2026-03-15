from events.eventbus import EventBus
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore


class _AppState:
    _instance: Optional["_AppState"] = None
    event_bus: Optional[EventBus] = None
    reminder_scheduler: Optional[AsyncIOScheduler] = None
    cron_scheduler: Optional[AsyncIOScheduler] = None


def get_state() -> _AppState:
    if _AppState._instance is None:
        _AppState._instance = _AppState()
    return _AppState._instance


def get_event_bus() -> EventBus:
    state = get_state()
    if state.event_bus is None:
        state.event_bus = EventBus()
    return state.event_bus


def get_scheduler() -> AsyncIOScheduler:
    state = get_state()
    if state.reminder_scheduler is None:
        state.reminder_scheduler = AsyncIOScheduler()
        state.reminder_scheduler.start()
    return state.reminder_scheduler


def get_cron_scheduler() -> AsyncIOScheduler:
    state = get_state()
    if state.cron_scheduler is None:
        jobstores = {"default": SQLAlchemyJobStore(url="sqlite:///jobs.sqlite")}
        state.cron_scheduler = AsyncIOScheduler(jobstores=jobstores)
        state.cron_scheduler.start()
    return state.cron_scheduler
