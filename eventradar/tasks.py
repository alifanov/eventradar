from celery.task import task, periodic_task
from celery.schedules import crontab
from common.utils import del_old_evens, PostProcess
from django.contrib.auth.models import User

@periodic_task(ignore_result=True, run_every=crontab(hour=0, minute=0))
def clean_old_events():
    del_old_evens()

@periodic_task(ignore_result=True, run_every=crontab(minute=0))
def get_posts():
    for u in User.objects.all():
        pp = PostProcess(u)
        pp.get_posts()

@task
def get_new_posts(user):
    pp = PostProcess(user)
    pp.get_posts()

@task
def clean_events():
    del_old_evens()