f = open('urls.txt')
urls = f.readlines()

import unirest

def cb(resp):
    try:
        for p in resp.body['response'][1:]:
            print p['to_id']

    except KeyError:
        pass
#        print resp.raw_body

for url in urls[:10]:
    unirest.get(url, callback=cb)

print 'End'