from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

from .tasks.get_lpr_task_v2 import get_lpr_task


def run_schedulers():
    scheduler = BackgroundScheduler()

    start_ts = datetime.now() - timedelta(minutes=10)
    end_ts = datetime.now()
    scheduler.add_job(get_lpr_task, "interval", [start_ts, end_ts], minutes=5)
    scheduler.start()
