from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.services.report_service import ReportService


def _run_scheduled_report_job() -> None:
    settings = get_settings()
    db = SessionLocal()
    try:
        ReportService(db).generate_scheduled_snapshot(
            lookback_days=settings.REPORT_LOOKBACK_DAYS,
            report_name="scheduled_snapshot",
        )
    finally:
        db.close()


def start_report_scheduler() -> BackgroundScheduler | None:
    settings = get_settings()
    if not settings.REPORT_SCHEDULER_ENABLED:
        return None

    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        _run_scheduled_report_job,
        trigger=IntervalTrigger(minutes=settings.REPORT_SCHEDULE_MINUTES),
        id="finance_scheduled_report",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()
    return scheduler


def stop_report_scheduler(scheduler: BackgroundScheduler | None) -> None:
    if scheduler:
        scheduler.shutdown(wait=False)
