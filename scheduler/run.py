from apscheduler.schedulers.background import BackgroundScheduler

from .tasks.get_lpr_task_v2 import get_lpr_task


def run_schedulers():
    scheduler = BackgroundScheduler()
    scheduler.add_job(get_lpr_task, "interval", minutes=5)
    scheduler.start()
