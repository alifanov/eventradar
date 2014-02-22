# coding: utf-8
__author__ = 'vampire'
import json, datetime, re, time, gevent
import requests, grequests
import urllib2, unirest
from urllib import urlencode
from common.models import Event, Source
from social_auth.db.django_models import UserSocialAuth

regexp = re.compile(u'.*(^|\s)([1-9]\d?\s(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря))',
    re.I)
pattern_day = re.compile(u'.*(сегодня|завтра)')
pattern_today = re.compile(u'.*(сегодня)')
pattern_tomorrow = re.compile(u'.*(завтра)')

friends_url = 'https://api.vk.com/method/friends.get?uid={}&fields=first_name,last_name,uid'
posts_url = 'https://api.vk.com/method/wall.get?owner_id={}&count=10'
groups_url = 'https://api.vk.com/method/groups.get?uid={}&extended=1&access_token={}'

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
            if day == 29 and months[month.lower()] == 2 and now.year%12 != 0: return date
            date = datetime.date(day = day, month=months[month.lower()], year=now.year)
    return date

def process_for_user(user):
    # groups
    u = UserSocialAuth.objects.get(user=user, provider='vk-oauth')
    resp = requests.get(groups_url\
    .format(u.uid, u.tokens['access_token']))
    ids = resp.json()['response']
    for i in ids[1:]:
        s,created = Source.objects.get_or_create(
            name=i['name'],
            uid='-{}'.format(i['gid'])
        )
        s.users.add(u.user)
    print 'Getting groups [DONE]'

    # friends
    resp = requests.get(friends_url.format(u.uid))
    rj = resp.json()
    ids = rj.get('response', [])
    i_ids = []
    for i in ids[1:]:
        s,created = Source.objects.get_or_create(
            name=u'{} {}'.format(i['first_name'], i['last_name']),
            uid=i['uid']
        )
        s.users.add(u.user)

    print 'Getting friends [DONE]'

    ss = u.user.sources.all()
    dict_ss = {s.uid:s for s in ss}
    ids = ss.values_list('uid', flat=True)
    urls = map(lambda x: posts_url.format(x), ids)
    n = 100
    grouped_urls = [urls[i:i+n] for i in xrange(0, len(urls), n)]
    for i, grp in enumerate(grouped_urls):
        print 'Running {}'.format(i)
        r = (grequests.get(u, verify=False) for u in grp)
        rsp = grequests.map(r)

        for p in rsp:
            process_wall(p.json().get('response', []), dict_ss)

def get_all_uids():
    start = time.time()
    for u in UserSocialAuth.objects.filter(provider='vk-oauth'):
        process_for_user(u.user)
    print 'End in {}'.format(time.time()-start)

def process_wall(posts, uids_dict):
    for post in posts[1:]:
        if post['text'] and (regexp.match(post['text']) or pattern_day.match(post['text'])):
            date_str = None
            if regexp.match(post['text']):
                f = regexp.findall(post['text'])
                if f and len(f[0]) > 0:
                    date_str = f[0][1]
            if pattern_day.match(post['text']):
                f = pattern_day.findall(post['text'])
                if f and len(f[0]) > 0:
                    date_str = f[0]
            link = u'https://vk.com/wall{}_{}'.format(post['to_id'], post['id'])
            event_date = get_date_from_string(date_str)
            if not Event.objects.filter(link = link).exists() and event_date:
                event_date = event_date.strftime(u'%Y-%m-%d')
                post_date = datetime.datetime.fromtimestamp(int(post['date']))#.strftime('%Y-%m-%d %H:%M:%S')
                text = re.sub(u"[^a-zA-Zа-яА-Я0-9.,\/\-\s\<\>]", "" ,post['text'])
                if pattern_today.match(text) and not event_date == post_date.today(): continue
                if pattern_tomorrow.match(text) and not event_date == post_date.today() + datetime.timedelta(days=1): continue
                if datetime.datetime.strptime(event_date, u'%Y-%m-%d').date() > datetime.date.today() + datetime.timedelta(days=-1):
                    event = Event.objects.create(
                        text = text,
                        owner_id = post['to_id'],
                        link = link,
                        source = uids_dict[post['to_id']],
                        post_date = post_date,
                        event_date = event_date
                    )
                    event.save()

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