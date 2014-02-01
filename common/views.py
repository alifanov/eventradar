# coding: utf-8
# Create your views here.
import re, datetime
from django.views.generic import TemplateView, ListView, View
from social_auth.db.django_models import UserSocialAuth
from django.http import HttpResponse, HttpResponseRedirect
from common.utils import call_api
from common.forms import FeedbackForm
from common.models import Event

months = {
    u'января': 1,
    u'февраля': 2,
    u'марта': 3,
    u'апреля': 4,
    u'мая': 5,
    u'июня': 6,
    u'июля': 7,
    u'августа': 8,
    u'сентября': 9,
    u'октября': 10,
    u'ноября': 11,
    u'декабря': 12
}

class ProcessView(View):
    """
    Производит сканирование по друзям и группам пользователя и выдает результат, когда все готово
    """
    regexp = re.compile(u'.*(^|\s)([1-9]\d?\s(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря))',
        re.I)
    pattern_day = re.compile(u'.*(сегодня|завтра)')

    def get_token(self):
        if UserSocialAuth.objects.filter(user=self.request.user, provider='vk-oauth').exists():
            token_dict = UserSocialAuth.objects.get(user=self.request.user, provider='vk-oauth').tokens
            return token_dict['access_token']
        return None

    def call_api(self, method, params):
        return call_api(method, params, self.get_token())

    def get_friends(self):
        friends = self.call_api('friends.get', [('fields', 'uid, first_name, last_name')])
        return friends

    def get_groups(self):
        groups = self.call_api('groups.get',[('extended', '1')])
        if len(groups) <= 1: return []
        return groups[1:]

    def get_date_from_string(self, date_str):
        date = None
        if u'сегодня' in date_str:
            date = datetime.date.today()
        if u'завтра' in date_str:
            date = datetime.date.today() + datetime.timedelta(days=1)
        if u' ' in date_str:
            day,month = date_str.split(u' ')
            now = datetime.datetime.now()
            if day.isdigit():
                day = int(day)
                date = datetime.date(day = day, month=months[month.lower()], year=now.year)
        return date

    def process_posts(self, posts, source):
        if posts:
            for post in posts[1:]:
                if post['text'] and (self.regexp.match(post['text']) or self.pattern_day.match(post['text'])):
                    date_str = None
                    if self.regexp.match(post['text']):
                        f = self.regexp.findall(post['text'])
                        if f and len(f[0]) > 0:
                            date_str = f[0][1]
                    if self.pattern_day.match(post['text']):
                        f = self.pattern_day.findall(post['text'])
                        if f and len(f[0]) > 0:
                            date_str = f[0]
                    link = u'https://vk.com/wall{}_{}'.format(post['to_id'], post['id'])
                    if not Event.objects.filter(link = link).exists():
                        event_date = self.get_date_from_string(date_str).strftime(u'%Y-%m-%d')
                        if datetime.datetime.strptime(event_date, u'%Y-%m-%d').date() > datetime.date.today() + datetime.timedelta(days=-1):
                            event = Event.objects.create(
                                text = post['text'],
                                source = source,
                                link = link,
                                post_date = datetime.datetime.fromtimestamp(int(post['date'])).strftime('%Y-%m-%d %H:%M:%S'),
                                event_date = event_date
                            )
                            event.users.add(self.request.user)
                            event.save()
                    else:
                        if not self.request.user.events.filter(link=link).exists():
                            e = Event.objects.get(link=link)
                            e.users.add(self.request.user)
                            e.save()

    def get_posts(self):
        if self.request.user.is_authenticated():
            friends = self.get_friends()
            if friends is None: return None
            for friend in friends:
                try:
                    newposts = self.call_api('wall.get', [('owner_id', friend['uid']), ('count', 10)])
                    self.process_posts(newposts, u'{} {}'.format(friend['first_name'], friend['last_name']))
                except KeyError:
                    pass

            groups = self.get_groups()
            for group in groups:
                try:
                    newposts = self.call_api('wall.get', [('owner_id', u'-{}'.format(group['gid'])), ('count', 10)])
                    self.process_posts(newposts, group['name'])
                except KeyError:
                    pass
            return len(friends)+len(groups)
        return None

    def get(self, request, *args, **kwargs):
        if self.get_posts() is None:
            return HttpResponseRedirect('/auth-expired/')
        return HttpResponse('Done')

class TodayEventsView(ListView):
    template_name = 'home.html'
    context_object_name = 'posts'
    active = 'today'

    def get_queryset(self):
        return self.request.user.filter(event_date=datetime.date.today())

    def get_context_data(self, **kwargs):
        ctx = super(TodayEventsView, self).get_context_data(**kwargs)
        ctx['active_btn'] = self.active
        return ctx

class TomorrowEventsView(TodayEventsView):
    active = 'tomorrow'

    def get_queryset(self):
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        return self.request.user.filter(event_date=tomorrow)

class WeekEventsView(TodayEventsView):
    active = 'week'

    def get_queryset(self):
        week = datetime.date.today() + datetime.timedelta(days=7)
        return self.request.user.filter(event_date__lte=week)

class MonthEventsView(TodayEventsView):
    active = 'month'

    def get_queryset(self):
        month = datetime.date.today() + datetime.timedelta(days=30)
        return self.request.user.filter(event_date__lte=month)

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
            return self.request.user.events.all()
        return Event.objects.none()