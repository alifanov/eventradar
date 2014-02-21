# coding: utf-8
# Create your views here.
import re, datetime
from django.views.generic import TemplateView, ListView
from common.forms import FeedbackForm
from common.models import Event
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponseRedirect, HttpResponse
from eventradar.tasks import get_new_posts
from celery.result import AsyncResult

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/')

def process(request):
    data = 'Fail'
    if 'task_id' in request.session:
        r = AsyncResult(request.session['task_id'])
        data = r.state
    else:
        if request.user.is_authenticated():
            job = get_new_posts.delay(request.user)
            request.session['task_id'] = job.id
            data = job.id
        else:
            data = u'401 Authorization required'
    return HttpResponse(data, mimetype='application/json')

class TodayEventsView(ListView):
    template_name = 'home.html'
    context_object_name = 'posts'
    active = 'today'

    def get_queryset(self):
        sources_ids = self.request.user.sources.values_list('uid', flat=True)
        return Event.objects.filter(owner_id__in=sources_ids, event_date=datetime.date.today()).order_by('event_date')

    def get_context_data(self, **kwargs):
        ctx = super(TodayEventsView, self).get_context_data(**kwargs)
        ctx['active_btn'] = self.active
        return ctx

class TomorrowEventsView(TodayEventsView):
    active = 'tomorrow'

    def get_queryset(self):
        sources_ids = self.request.user.sources.values_list('uid', flat=True)
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        return Event.objects.filter(owner_id__in=sources_ids, event_date=tomorrow).order_by('event_date')

class WeekEventsView(TodayEventsView):
    active = 'week'

    def get_queryset(self):
        sources_ids = self.request.user.sources.values_list('uid', flat=True)
        week = datetime.date.today() + datetime.timedelta(days=7)
        return Event.objects.filter(owner_id__in=sources_ids, event_date__lte=week).order_by('event_date')

class MonthEventsView(TodayEventsView):
    active = 'month'

    def get_queryset(self):
        sources_ids = self.request.user.sources.values_list('uid', flat=True)
        month = datetime.date.today() + datetime.timedelta(days=30)
        return Event.objects.filter(owner_id__in=sources_ids, event_date__lte=month).order_by('event_date')

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

class HomeView(TemplateView):
    template_name = 'home.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect('/today/')
        super(HomeView, self).dispatch(request, *args, **kwargs)