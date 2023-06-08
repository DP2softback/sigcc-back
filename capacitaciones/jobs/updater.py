from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from capacitaciones.jobs.tasks import task_create_udemy_evaluation


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(task_create_udemy_evaluation, 'interval', seconds=60, start_date=datetime.now())
    scheduler.start()
