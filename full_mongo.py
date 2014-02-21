# coding: utf-8
import pymongo
import grequests, requests
import time
import re
import datetime

start = time.time()
# reg exps
regexp = re.compile(u'.*(^|\s)([1-9]\d?\s(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря))',
    re.I)
pattern_day = re.compile(u'.*(сегодня|завтра)')
pattern_today = re.compile(u'.*(сегодня)')
pattern_tomorrow = re.compile(u'.*(завтра)')

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
            if day > 31:
                day %= 100
            date = datetime.date(day = day, month=months[month.lower()], year=now.year)
    return date

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

vkid = '194484'

client = pymongo.MongoClient()

db = client['test']

sources = db.sources
posts = db.posts

friends_url = 'https://api.vk.com/method/friends.get?uid={}&fields=first_name,last_name,uid'
posts_url = 'https://api.vk.com/method/wall.get?uid={}&count=10'
groups_url = 'https://api.vk.com/method/groups.get?uid={}&extended=1&access_token={}'

r = requests.get(friends_url.format(vkid))
friends = r.json().get('response')
sources_list = []
friends_of_friends_urls = []
for friend in friends:
    if sources.find({'_id': friend['uid']}).limit(1).count() == 0:
        sources.insert({
            '_id': friend['uid'],
            'name': u'{} {}'.format(friend['first_name'], friend['last_name'])
        })
    friends_of_friends_urls.append(
        friends_url.format(friend['uid'])
    )


r = (grequests.get(u, verify=False) for u in friends_of_friends_urls)
rs = grequests.map(r)
rs = map(lambda x: x.json(), rs)
sources_list = []
for r in rs:
    gfriends = r.get('response', [])
    if gfriends:
        for gf in gfriends:
            if sources.find({'_id': gf['uid']}).limit(1).count() == 0:
                sources.insert({
                    '_id': gf['uid'],
                    'name': u'{} {}'.format(gf['first_name'], gf['last_name'])
                })

print 'Done in  {}'.format(time.time() - start)