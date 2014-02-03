__author__ = 'vampire'
import json, datetime
import urllib2
from urllib import urlencode
from common.models import Event

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