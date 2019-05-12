import urllib2
import re
import geoip2.database
from django.conf import settings


def get_current_ip():
    url = urllib2.urlopen("http://txt.go.sohu.com/ip/soip")
    text = url.read()
    res = re.findall(r'\d+.\d+.\d+.\d+',text)
    ip = res[0]
    return ip


def get_current_country():
    ip = get_current_ip()
    reader = geoip2.database.Reader(settings.GEOIP_DB_PATH)
    response = reader.country(ip)
    return response.country.name

