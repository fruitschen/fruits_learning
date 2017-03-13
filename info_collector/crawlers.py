# coding: utf-8
import json
import logging
import random
import requests
import time
from BeautifulSoup import BeautifulSoup as BS
from datetime import datetime, timedelta


from django.utils import timezone
from django.utils.html import strip_tags

from info_collector.models import InfoSource, Info, Content, Author

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


class XueqiuBaseCrawler(AbstractBaseCrawler):
    def __init__(self, slug):
        super(XueqiuBaseCrawler, self).__init__(slug)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Upgrade - Insecure - Requests': '1',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en,zh-CN;q=0.8,zh;q=0.6,zh-TW;q=0.4',
        }

    def save_author(self, user_info, info):
        user_id = user_info['id']
        author_query = Author.objects.filter(user_id=user_id)
        if not author_query.exists():
            img = user_info.get('profile_image_url', '')
            if img:
                img = user_info.get('photo_domain', '') + img.split(',')[-1]
            author = Author.objects.create(
                user_id=user_id,
                name=user_info.get('screen_name', ''),
                avatar_url=img,
                raw=json.dumps(user_info),
            )
        else:
            author = author_query[0]
        info.author = author
        info.save()
        return author

class XueqiuHomeCrawler(XueqiuBaseCrawler):
    """
    from info_collector.crawlers import XueqiuHomeCrawler
    crawler = XueqiuHomeCrawler()
    crawler.update_info()
    """

    def __init__(self):
        super(XueqiuHomeCrawler, self).__init__('xueqiu_home')

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
            url = '{}{}/{}'.format(self.info_source.url, data['user']['id'], identifier).replace('//', '/')
            created_at = int(data['created_at']) / 1000
            created = datetime.utcfromtimestamp(created_at) + timedelta(minutes=60*8)
            info_query = Info.objects.filter(info_source=self.info_source, identifier=identifier)
            if not info_query.exists():
                info = Info.objects.create(
                    url=url,
                    status=Info.NEW,
                    info_source=self.info_source,
                    title=title,
                    identifier=identifier,
                    original_timestamp = created,
                )
                self.save_author(data['user'], info)
            else:
                info = info_query[0]
                if not info.author:
                    author = self.save_author(data['user'], info)


class XueqiuPeopleCrawler(XueqiuBaseCrawler):
    """
    from info_collector.crawlers import XueqiuPeopleCrawler
    crawler = XueqiuPeopleCrawler()
    crawler.update_info()
    """

    def __init__(self):
        super(XueqiuPeopleCrawler, self).__init__('xueqiu_people')

    def update_info(self):
        session = requests.Session()
        # load home page and get cookies
        response = get_response(session, self.info_source.url, timeout=3, headers=self.headers)
        if not response:
            return

        users = [
            {'name': u'孙旭东', 'uid': '2536207007'},
            {'name': u'驽马-估值温度计', 'uid': '2548992415'},
            {'name': u'b_ing', 'uid': '4939534471'},
            {'name': u'云蒙', 'uid': '3037882447'},
            {'name': u'唐朝', 'uid': '8290096439'},
            {'name': u'东博老股民', 'uid': '9528220473'},
            {'name': u'滚一个雪球', 'uid': '6677862831'},
            {'name': u'正合奇胜天舒', 'uid': '7315353232'},
            {'name': u'陈绍霞', 'uid': '1876614331'},
            {'name': u'DAVID自由之路', 'uid': '5819606767'},
            {'name': u'天南财务健康谈', 'uid': '1175857472'},
            {'name': u'闲来一坐s话投资', 'uid': '3491303582'},
            {'name': u'处镜如初', 'uid': '9226205191'},
        ]
        for user in users:
            # print user['name']
            page = 1
            json_url = 'https://xueqiu.com/v4/statuses/user_timeline.json?user_id={}&page={}&type=&_=1488637{}'.\
                format(user['uid'], page, random.randint(1, 1000000))
            json_response = get_response(session, json_url, timeout=3, headers=self.headers)
            json_result = json_response.json()
            total = json_result['total']
            max_page = json_result['maxPage']
            posts = json_result['statuses']
            posts.reverse()
            for post in posts:
                identifier = post['target']
                title = post['title'] or post['topic_title']
                url = '{}{}'.format(self.info_source.url, post['target']).replace('//', '/')
                text = post['text']
                if not title:
                    title = u'[无标题]{}...'.format(strip_tags(text)[:64])
                created_at = int(post['created_at']) / 1000
                created = datetime.utcfromtimestamp(created_at) + timedelta(minutes=60*8)
                info_query = Info.objects.filter(info_source=self.info_source, identifier=identifier)
                if not info_query.exists():
                    content = Content.objects.create(content=text)
                    info = Info.objects.create(
                        url=url,
                        status=Info.NEW,
                        info_source=self.info_source,
                        title=title,
                        identifier=identifier,
                        original_timestamp = created,
                        content = content,
                    )
                    info.save()
                    author = self.save_author(post['user'], info)
                else:
                    info = info_query[0]
                    if not info.author:
                        author = self.save_author(post['user'], info)

            time.sleep(3)

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

        queries = [
            # 'q=python',
            u'tag=英文绘本',
        ]
        for query in queries:
            start = 0
            total = 0
            while (not start) or (start < total - count):  # haven't got all the books yet
                api_url = u'https://api.douban.com/v2/book/search?{}&count={}&start={}'.format(query, count, start)
                json_response = get_response(requests, api_url , timeout=3, headers=self.headers)
                json_result = json_response.json()
                if not total:
                    total = json_result['total']
                    # print 'Total {}'.format(total)
                start += count
                books = json_result['books']

                for book in books:
                    identifier = book['id']
                    title = book['title']
                    url = '{}subject/{}'.format(self.info_source.url, identifier)
                    try:
                        created = timezone.datetime.strptime(book['pubdate'], '%Y-%m-%d')
                        if created < timezone.datetime(1900,1,1):
                            created = None
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
                        pass
                        # print u'Book exists {}'.format(book['title'])
