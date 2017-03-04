# coding: utf-8

import logging
import json
import requests
from datetime import datetime, timedelta
from BeautifulSoup import BeautifulSoup as BS


from django.utils import timezone

from info_collector.models import InfoSource, Info

import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()


class AbstractBaseCrawler(object):
    def __init__(self, slug):
        self.headers = { 'user-agent': 'info_collect/0.1' }
        self.info_source = InfoSource.objects.get(slug=slug)
        self.slug = slug

    def run(self):
        try:
            self.info_source.status = InfoSource.CRAWLING
            self.info_source.save()
            self.update_info()
            self.info_source.last_fetched = timezone.now()
            self.info_source.status = InfoSource.GOOD
            self.info_source.save()
        except Exception, e:
            logging.error(e)
            try:
                info_source = InfoSource.objects.get(slug=self.slug)
                info_source.status = InfoSource.ERROR
                info_source.last_error = timezone.now()
                info_source.save()
            except:
                pass


def get_response(req, url, timeout, headers):
    response = None
    retry = 0
    while not response and retry < 3:
        try:
            response = req.get(url, timeout=timeout, headers=headers)
        except requests.exceptions.ConnectTimeout:
            pass
        retry += 1
    return response

class TechQQCrawler(AbstractBaseCrawler):
    """
    from info_collector.crawlers import TechQQCrawler
    crawler = TechQQCrawler()
    crawler.update_info()
    """

    def __init__(self):
        super(TechQQCrawler, self).__init__('tech_qq')

    def update_info(self):
        response = get_response(requests, self.info_source.url, timeout=3, headers=self.headers)
        if not response:
            return
        soup = BS(response.text)
        list_zone = soup.find('div', {'id': 'listZone'})
        headings = list_zone.findAll('h3')
        links = [heading.find('a') for heading in headings]
        links.reverse()
        for link in links:
            url = link.get('href')
            title = link.text
            identifier = '/'.join(url.split('/')[-2:])
            if not Info.objects.filter(info_source=self.info_source, identifier=identifier).exists():
                info = Info.objects.create(
                    url=url,
                    status=Info.NEW,
                    info_source=self.info_source,
                    title=title,
                    identifier=identifier,
                )


class XueqiuHomeCrawler(AbstractBaseCrawler):
    """
    from info_collector.crawlers import XueqiuHomeCrawler
    crawler = XueqiuHomeCrawler()
    crawler.update_info()
    """

    def __init__(self):
        super(XueqiuHomeCrawler, self).__init__('xueqiu_home')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Upgrade - Insecure - Requests': '1',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en,zh-CN;q=0.8,zh;q=0.6,zh-TW;q=0.4',
        }

    def update_info(self):
        session = requests.Session()
        # load home page and get cookies
        response = get_response(session, self.info_source.url, timeout=3, headers=self.headers)
        if not response:
            return

        json_url = 'https://xueqiu.com/v4/statuses/public_timeline_by_category.json?since_id=-1&max_id=-1&count=20&category=-1'
        json_response = get_response(session, json_url, timeout=3, headers=self.headers)
        res = json_response.json()
        posts = res['list']
        posts.reverse()
        for post in posts:
            data = json.loads(post['data'])
            identifier = data['id']
            title = data['title'] or data['topic_title']
            url = '{}{}/{}'.format(self.info_source.url, data['user']['id'], identifier)
            created_at = int(data['created_at']) / 1000
            created = datetime.utcfromtimestamp(created_at) + timedelta(minutes=60*8)

            if not Info.objects.filter(info_source=self.info_source, identifier=identifier).exists():
                info = Info.objects.create(
                    url=url,
                    status=Info.NEW,
                    info_source=self.info_source,
                    title=title,
                    identifier=identifier,
                    original_timestamp = created,
                )


class DoubanBookCrawler(AbstractBaseCrawler):
    """
    from info_collector.crawlers import DoubanBookCrawler
    crawler = DoubanBookCrawler()
    crawler.update_info()
    """

    def __init__(self):
        super(DoubanBookCrawler, self).__init__('douban_book')

    def update_info(self):
        count = 50
        start = 0
        total = 0
        while (not start) or (start < total - count):  # haven't got all the books yet
            api_url = 'https://api.douban.com/v2/book/search?q=python&count={}&start={}'.format(count, start)
            json_response = get_response(requests, api_url , timeout=3, headers=self.headers)
            json_result = json_response.json()
            if not total:
                total = json_result['total']
            start += count
            books = json_result['books']

            for book in books:
                identifier = book['id']
                title = book['title']
                url = '{}subject/{}'.format(self.info_source.url, identifier)
                try:
                    created = timezone.datetime.strptime(book['pubdate'], '%Y-%m-%d')
                except:
                    created = None
                if not Info.objects.filter(info_source=self.info_source, identifier=identifier).exists():
                    info = Info.objects.create(
                        url=url,
                        status=Info.NEW,
                        info_source=self.info_source,
                        title=title,
                        identifier=identifier,
                        original_timestamp = created,
                    )
                else:
                    print u'Book exists {}'.format(book['title'])
