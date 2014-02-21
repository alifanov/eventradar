__author__ = 'vampire'
from django.contrib import admin
from common.models import Feedback, Event, Source

admin.site.register(Feedback)
admin.site.register(Event)
admin.site.register(Source)
