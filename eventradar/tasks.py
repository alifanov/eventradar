from celery.task import task, periodic_task
from celery.schedules import crontab
from common.utils import del_old_evens, PostProcess, get_all_uids
from django.contrib.auth.models import User

@periodic_task(ignore_result=True, run_every=crontab(hour=0, minute=0))
def clean_old_events():
    del_old_evens()

@periodic_task(ignore_result=True, run_every=crontab(hour="*/4"))
def get_posts():
    get_all_uids()

@task
def get_new_posts(user):
    pp = PostProcess(user)
    pp.get_posts()

@task
def clean_events():
    del_old_evens()