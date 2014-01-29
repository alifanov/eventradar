# coding: utf-8
# Create your views here.
import re, datetime
from django.views.generic import TemplateView
from social_auth.db.django_models import UserSocialAuth
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
            date = datetime.date(day = day, month=months[month.lower()], year=now.year)
        return date

    def get_posts(self):
        posts = []
        if self.request.user.is_authenticated():
            regexp = re.compile(u'.*(^|\s)(\d+\s(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря))',
            re.I)
            pattern_day = re.compile(u'.*(сегодня|завтра)')
            for friend in self.get_friends():
                try:
                    newposts = self.call_api('wall.get', [('owner_id', friend['uid']), ('count', 10)])
                    for post in newposts[1:]:
                        if post['text'] and (regexp.match(post['text']) or pattern_day.match(post['text'])):
                            date_str = None
                            if regexp.match(post['text']):
                                f = regexp.findall(post['text'])
                                if f and len(f[0]) > 0:
                                    date_str = f[0][1]
                            event = Event.objects.create(
                                text = post['text'],
                                source = u'{} {}'.format(friend['first_name'], friend['last_name']),
                                link = u'https://vk.com/wall{}_{}'.format(post['to_id'], post['id']),
                                post_date = datetime.datetime.fromtimestamp(int(post['date'])).strftime('%d-%m-%Y %H:%M:%S'),
                                event_date = self.get_date_from_string(date_str)
                            )
                            posts.append({
                                u'source': event.source,
                                u'text': event.text,
                                u'date': event.post_date,
                                u'link': event.link
                            })
                except KeyError:
                    pass

            for group in self.get_groups():
                try:
                    newposts = self.call_api('wall.get', [('owner_id', u'-{}'.format(group['gid'])), ('count', 10)])
                    for post in newposts[1:]:
                        if post['text'] and regexp.match(post['text']):
                            posts.append({
                                u'matched': True if regexp.match(post['text']) else False,
                                u'source': group['name'],
                                u'text': post['text'],
                                u'date': datetime.datetime.fromtimestamp(int(post['date'])).strftime('%d-%m-%Y %H:%M:%S'),
                                u'link': u'https://vk.com/wall{}_{}'.format(post['to_id'], post['id'])
                            })
                except KeyError:
                    pass
        return posts

    def get_context_data(self, **kwargs):
        ctx = super(HomeView, self).get_context_data(**kwargs)
        ctx['posts'] = self.get_posts()
        return ctx