# coding: utf-8
# Create your views here.
import re, datetime
from django.views.generic import TemplateView, ListView
from common.forms import FeedbackForm
from common.models import Event

class TodayEventsView(ListView):
    template_name = 'home.html'
    context_object_name = 'posts'
    active = 'today'

    def get_queryset(self):
        return self.request.user.events.filter(event_date=datetime.date.today()).order_by('event_date')

    def get_context_data(self, **kwargs):
        ctx = super(TodayEventsView, self).get_context_data(**kwargs)
        ctx['active_btn'] = self.active
        return ctx

class TomorrowEventsView(TodayEventsView):
    active = 'tomorrow'

    def get_queryset(self):
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        return self.request.user.events.filter(event_date=tomorrow).order_by('event_date')

class WeekEventsView(TodayEventsView):
    active = 'week'

    def get_queryset(self):
        week = datetime.date.today() + datetime.timedelta(days=7)
        return self.request.user.events.filter(event_date__lte=week).order_by('event_date')

class MonthEventsView(TodayEventsView):
    active = 'month'

    def get_queryset(self):
        month = datetime.date.today() + datetime.timedelta(days=30)
        return self.request.user.events.filter(event_date__lte=month).order_by('event_date')

class FeedbackView(TemplateView):
    template_name = 'feedback.html'
    saved = False

    def post(self, request, *args, **kwargs):
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            self.saved = True
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(FeedbackView, self).get_context_data(**kwargs)
        ctx['form'] = FeedbackForm()
        ctx['saved'] = self.saved
        return ctx

class HomeView(ListView):
    template_name = 'home.html'
    context_object_name = 'posts'

    def get_queryset(self):
        if self.request.user.is_authenticated():
            return self.request.user.events.order_by('event_date')
        return Event.objects.none()