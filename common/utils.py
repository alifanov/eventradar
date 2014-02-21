# coding: utf-8
__author__ = 'vampire'
import json, datetime, re, time, gevent
import requests, grequests
import urllib2, unirest
from urllib import urlencode
from common.models import Event, Source
from social_auth.db.django_models import UserSocialAuth
from gevent import monkey

regexp = re.compile(u'.*(^|\s)([1-9]\d?\s(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря))',
    re.I)
pattern_day = re.compile(u'.*(сегодня|завтра)')
pattern_today = re.compile(u'.*(сегодня)')
pattern_tomorrow = re.compile(u'.*(завтра)')


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

def get_date_from_string(date_str):
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


def get_all_uids():
    for u in UserSocialAuth.objects.filter(provider='vk-oauth'):
        # groups
        resp = requests.get('https://api.vk.com/method/groups.get?uid={}&extended=1&access_token={}'
        .format(u.uid, u.tokens['access_token']))
        ids = resp.json()['response']
        for i in ids[1:]:
            s,created = Source.objects.get_or_create(
                name=i['name'],
                uid='-{}'.format(i['gid'])
            )
            s.users.add(u.user)

        # friends
        resp = requests.get('https://api.vk.com/method/friends.get?uid={}&fields=first_name,last_name,uid'.format(u.uid))
        rj = resp.json()
        ids = rj.get('response', [])
        i_ids = []
        r = []
        for i in ids:
            s,created = Source.objects.get_or_create(
                name=u'{} {}'.format(i['first_name'], i['last_name']),
                uid=i['uid']
            )
            s.users.add(u.user)
            r.append('https://api.vk.com/method/friends.get?uid={}&fields=first_name,last_name,uid'.format(i['uid']))
        rr = (grequests.get(rr, verify=False) for rr in r)
        rsp = grequests.map(rr)
        for i in rsp:
            s,created = Source.objects.get_or_create(
                name=u'{} {}'.format(i['first_name'], i['last_name']),
                uid=i['uid']
            )
            s.users.add(u.user)



#    uids = UserSocialAuth.objects.filter(provider='vk-oauth').values_list('uid', flat=True)
#
#    # get all friends
#    r = (grequests.get(u) for u in map(lambda x: 'https://api.vk.com/method/friends.get?uid={}&fields=first_name,last_name,uid'.format(x), uids))
#    rs = grequests.map(r)
#    uus = map(lambda x: json.loads(x), rs)
#    uus = [y for x in uus for y in x]
#    for p in uus:
#        Source.objects.create(name=u'{} {}'.format(p['first_name'], p['last_name']), uid=p['uid'])
#    uus = [p['uid'] for p in uus]
#    uus = list(set(uus))
#
#    # get all friends of uniq list of friends
#    r = (grequests.get(u) for u in map(lambda x: 'https://api.vk.com/method/friends.get?uid={}&fields=first_name,last_name,uid'.format(x), uids))
#    rs = grequests.map(r)
#    uus = map(lambda x: json.loads(x), rs)
#    uus = [y for x in uus for y in x]
#    for p in uus:
#        Source.objects.create(name=u'{} {}'.format(p['first_name'], p['last_name']), uid=p['uid'])
#        uus = [p['uid'] for p in uus]
#    # rest only uniq friends
#    uus = list(set(uus))
#
#    def process_wall(resp):
#        posts = []
#        try:
#            posts = resp.body.response
#        except KeyError:
#            pass
#        for post in posts:
#            if post['text'] and (regexp.match(post['text']) or pattern_day.match(post['text'])):
#                date_str = None
#                if regexp.match(post['text']):
#                    f = regexp.findall(post['text'])
#                    if f and len(f[0]) > 0:
#                        date_str = f[0][1]
#                if pattern_day.match(post['text']):
#                    f = pattern_day.findall(post['text'])
#                    if f and len(f[0]) > 0:
#                        date_str = f[0]
#                link = u'https://vk.com/wall{}_{}'.format(post['to_id'], post['id'])
#                if not Event.objects.filter(link = link).exists():
#                    event_date = get_date_from_string(date_str).strftime(u'%Y-%m-%d')
#                    post_date = datetime.datetime.fromtimestamp(int(post['date']))#.strftime('%Y-%m-%d %H:%M:%S')
#                    text = re.sub(u"[^a-zA-Zа-яА-Я0-9.,\-\s\<\>]", "" ,post['text'])
#                    if pattern_today.match(text) and not event_date == post_date.today(): continue
#                    if pattern_tomorrow.match(text) and not event_date == post_date.today() + datetime.timedelta(days=1): continue
#                    if datetime.datetime.strptime(event_date, u'%Y-%m-%d').date() > datetime.date.today() + datetime.timedelta(days=-1):
#                        event = Event.objects.create(
#                            text = text,
#                            source = Source.objects.get(uid=post['to_id']),
#                            link = link,
#                            post_date = post_date,
#                            event_date = event_date
#                        )
#                        event.users.add(user)
#                        event.save()
#                else:
#                    if not self.user.events.filter(link=link).exists():
#                        e = Event.objects.get(link=link)
#                        e.users.add(self.user)
#                        e.save()
#
#    urls = map(lambda x: 'https://api.vk.com/method/wall.get?owner_id={}&count=10'.format(x))
#    for url in urls:
#        unirest.get(url, callback=process_wall)


class PostProcess(object):
    """
    Производит сканирование по друзям и группам пользователя и выдает результат, когда все готово
    """
    added_posts = []
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
        return req_call_api(method, params, self.get_token())

    def get_friends(self):
        friends = self.call_api('friends.get', {'fields': 'uid, first_name, last_name'})
        return friends

    def get_groups(self):
        groups = self.call_api('groups.get',{'extended': '1'})
        if not groups or len(groups) <= 1: return []
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
                        post_date = datetime.datetime.fromtimestamp(int(post['date']))#.strftime('%Y-%m-%d %H:%M:%S')
                        text = re.sub(u"[^a-zA-Zа-яА-Я0-9.,\-\s\<\>]", "" ,post['text'])
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

    def wall_get_spawn(self, source, sid):
        posts = self.call_api('wall.get', {'owner_id': sid, 'count': 10})
        self.added_posts.append({
            'source': source,
            'posts': posts
        })

    def get_posts(self):
        friends = self.get_friends()
        groups = self.get_groups()
        if friends is None: return None

#        monkey.patch_socket()
#        monkey.patch_ssl()

        start = time.time()

        threads = []
        for friend in friends:
#            threads.append(gevent.spawn(self.wall_get_spawn, ))
            self.wall_get_spawn(u'{} {}'.format(friend['first_name'], friend['last_name']), friend['uid'])

        for group in groups:
#            threads.append(gevent.spawn(self.wall_get_spawn, ))
            self.wall_get_spawn(group['name'], u'-{}'.format(group['gid']))

#        gevent.joinall(threads)

        print len(self.added_posts)
        for ap in self.added_posts:
            self.process_posts(ap['posts'], ap['source'])

        print u'Proccessed in {}'.format(time.time() - start)

        return len(friends)+len(groups)


def del_old_evens():
    today = datetime.date.today()
    Event.objects.filter(event_date__lt=today).delete()

def req_call_api(method, params, token):
    params['access_token'] = token
    url = "https://api.vk.com/method/%s" % (method)
    resp = requests.get(url, params=params)
    if resp.status_code != 200: return None
    resp = resp.json()
    return resp['response']

def call_api(method, params, token):
    params.append(("access_token", token))
    url = "https://api.vk.com/method/%s?%s" % (method, urlencode(params))
    r = urllib2.urlopen(url)
    response = json.loads(r.read())
    if not 'response' in response: return None
    return response['response']