from celery import app
#from celery.task import task, periodic_task
from celery import crontab, periodic_task
from common.utils import del_old_evens, process_for_user, get_all_uids

@periodic_task(ignore_result=True, run_every=crontab(hour=0, minute=0))
def clean_old_events():
    del_old_evens()

@periodic_task(ignore_result=True, run_every=crontab(hour="*/4"))
def get_posts():
    get_all_uids()

@app.task
def get_new_posts(user):
    process_for_user(user)