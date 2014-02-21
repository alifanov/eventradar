# coding: utf-8
import MySQLdb
import unirest
import re
import datetime

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


db = MySQLdb.connect(host='localhost', user='eventuser', passwd='eventpass',db='eventdb', charset='utf8')

cursor = db.cursor()

sql = 'SELECT uid from common_source;'

cursor.execute(sql)

data = cursor.fetchall()

urls = []
for u in data:
    urls.append(
        'https://api.vk.com/method/wall.get?owner_id={}&count=10'.format(u[0])
    )
print len(urls)
#db.close()

def cb(resp):
    try:
        for post in resp.body['response'][1:]:
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
                link = 'https://vk.com/wall{}_{}'.format(post['to_id'], post['id'])
                event_date = get_date_from_string(date_str).strftime(u'%Y-%m-%d')
                post_date = datetime.datetime.fromtimestamp(int(post['date']))#.strftime('%Y-%m-%d %H:%M:%S')
                text = re.sub(u"[^a-zA-Zа-яА-Я0-9.,\-\s\<\>]", "" ,post['text'])
                if pattern_today.match(text) and not event_date == post_date.today(): continue
                if pattern_tomorrow.match(text) and not event_date == post_date.today() + datetime.timedelta(days=1): continue
                if datetime.datetime.strptime(event_date, u'%Y-%m-%d').date() > datetime.date.today() + datetime.timedelta(days=-1):
                    query = u'insert ignore into common_event (owner_id, post_date, event_date,text,source,link) values ({}, {}, {}, {}, {}, {})'\
                        .format(post['to_id'],
                        post_date.isoformat(),
                        event_date,
                        text,
                        post['to_id'],
                        link
                    )
                    print query.encode('utf-8')
#                    cursor.execute(query.encode('utf-8'))
#                    event = Event.objects.create(
#                        text = text,
#                        source = Source.objects.get(uid=post['to_id']),
#                        link = link,
#                        post_date = post_date,
#                        event_date = event_date
#                    )
#                    event.users.add(u.user)
#                    event.save()

    except KeyError:
        pass

for url in urls[:100]:
    unirest.get(url, callback=cb)

print 'End'