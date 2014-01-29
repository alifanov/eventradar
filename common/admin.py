__author__ = 'vampire'
from django.contrib import admin
from common.models import Feedback, Event

admin.site.register(Feedback)
admin.site.register(Event)
