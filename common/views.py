# coding: utf-8
# Create your views here.
import re, datetime
from django.views.generic import TemplateView
from social_auth.db.django_models import UserSocialAuth
from common.utils import call_api
from common.forms import FeedbackForm

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

    def get_posts(self):
        posts = []
        if self.request.user.is_authenticated():
            regexp = re.compile(u'.*(\d{1,2}\s(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря))',
            re.I)
            pattern_day = re.compile(u'.*(сегодня|завтра)')
            for friend in self.get_friends():
                try:
                    newposts = self.call_api('wall.get', [('owner_id', friend['uid']), ('count', 10)])
                    for post in newposts[1:]:
                        if post['text'] and (regexp.match(post['text']) or pattern_day.match(post['text'])):
                            posts.append({
                                u'matched': True if regexp.match(post['text']) else False,
                                u'source': u'{} {}'.format(friend['first_name'], friend['last_name']),
                                u'text': post['text'],
                                u'date': datetime.datetime.fromtimestamp(int(post['date'])).strftime('%d-%m-%Y %H:%M:%S'),
                                u'link': u'https://vk.com/wall{}_{}'.format(post['to_id'], post['id'])
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