# coding: utf-8
__author__ = 'vampire'
import json, datetime, re
import urllib2
from urllib import urlencode
from common.models import Event
from social_auth.db.django_models import UserSocialAuth

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

class PostProcess(object):
    """
    Производит сканирование по друзям и группам пользователя и выдает результат, когда все готово
    """
    user = None
    regexp = re.compile(u'.*(^|\s)([1-9]\d?\s(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря))',
        re.I)
    pattern_day = re.compile(u'.*(сегодня|завтра)')
    pattern_today = re.compile(u'.*(сегодня)')
    pattern_tomorrow = re.compile(u'.*(завтра)')

    def __init__(self, user):
        self.user=user

    def get_token(self):
        if UserSocialAuth.objects.filter(user=self.user, provider='vk-oauth').exists():
            token_dict = UserSocialAuth.objects.get(user=self.user, provider='vk-oauth').tokens
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
                        post_date = datetime.datetime.fromtimestamp(int(post['date'])).strftime('%Y-%m-%d %H:%M:%S')
                        text = re.sub('[^0-9A-Za-zА-Яа-я_-]', "" ,post['text'])
                        if self.pattern_today.match(text) and not event_date == post_date.today(): continue
                        if self.pattern_tomorrow.match(text) and not event_date == post_date.today() + datetime.timedelta(days=1): continue
                        if datetime.datetime.strptime(event_date, u'%Y-%m-%d').date() > datetime.date.today() + datetime.timedelta(days=-1):
                            event = Event.objects.create(
                                text = text,
                                source = source,
                                link = link,
                                post_date = post_date,
                                event_date = event_date
                            )
                            event.users.add(self.user)
                            event.save()
                    else:
                        if not self.user.events.filter(link=link).exists():
                            e = Event.objects.get(link=link)
                            e.users.add(self.user)
                            e.save()

    def get_posts(self):
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


def del_old_evens():
    today = datetime.date.today()
    Event.objects.filter(event_date__lt=today).delete()


def call_api(method, params, token):
    params.append(("access_token", token))
    url = "https://api.vk.com/method/%s?%s" % (method, urlencode(params))
    try:
        response = json.loads(urllib2.urlopen(url).read())
        resp = response['response']
    except KeyError:
        return None
    return resp