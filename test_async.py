import MySQLdb
import unirest

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
db.close()

def cb(resp):
    try:
        for p in resp.body['response'][1:]:
            print p['to_id']

    except KeyError:
        pass

for url in urls[:100]:
    unirest.get(url, callback=cb)

print 'End'