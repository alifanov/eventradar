from celery.task import periodic_task
from celery.task import task
from celery.schedules import crontab
from common.utils import del_old_evens

#@periodic_task(ignore_result=True, run_every=crontab(hour=0, minute=0))
@periodic_task(ignore_result=True, run_every=crontab())
def clean_old_events():
    del_old_evens()

@task
def clean_events():
    del_old_evens()