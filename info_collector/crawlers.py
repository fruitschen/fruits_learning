# coding: utf-8
import os
import json
import logging
import random
import requests
import time
import xlrd
from BeautifulSoup import BeautifulSoup as BS
from datetime import datetime, timedelta


from django.conf import settings
from django.utils import timezone
from django.utils.html import strip_tags

from info_collector.models import InfoSource, Info, Content, Author
from stocks.models import Stock

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


def get_response(req, url, timeout, headers, post_data=None):
    response = None
    retry = 0
    while not response and retry < 3:
        try:
            if post_data:
                response = req.post(url, data=post_data, timeout=timeout, headers=headers)
            else:
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
            url = '{}{}/{}'.format(self.info_source.url, data['user']['id'], identifier)
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
        self.get_starred_info_content(session)

    def get_starred_info_content(self, session):
        info_items = Info.objects.filter(info_source=self.info_source, starred=True, status=Info.NEW)
        for info in info_items:
            response = get_response(session, info.url, timeout=3, headers=self.headers)
            if not response:
                continue
            soup = BS(response.text)
            status_content = soup.find('div', {'class': 'status-content'})
            status_content = unicode(status_content)
            content = Content.objects.create(content=status_content)
            info.content = content
            info.status = Info.OK
            info.save()


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
                target = post['target']
                if target[0] == '/':
                    target = target[1:]
                url = '{}{}'.format(self.info_source.url, target)
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
                        status=Info.OK,
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


class StocksCrawler(AbstractBaseCrawler):
    """
    from info_collector.crawlers import StocksCrawler
    crawler = StocksCrawler()
    crawler.update_info()
    """

    def __init__(self):
        super(StocksCrawler, self).__init__('stocks')

    def update_info(self):
        sh_url = 'http://yunhq.sse.com.cn:32041/v1/sh1/list/exchange/equity'
        session = requests.Session()
        json_response = get_response(session, sh_url, timeout=3, headers=self.headers)
        json_result = json_response.json()
        for item in json_result['list']:
            code, name, price = item
            if not Stock.objects.filter(code=code, market='sh').exists():
                stock = Stock.objects.create(
                    code=code,
                    name=name,
                    market='sh',
                    is_stock=True,
                    price=price,
                    price_updated=timezone.now()
                )
            else:
                stock = Stock.objects.get(code=code)
                if stock.name != name:
                    print stock.name
                    stock.name = name
                    stock.save()

        if not os.path.exists(settings.DATA_DIR):
            os.makedirs(settings.DATA_DIR)
        sz_list_file = os.path.join(settings.DATA_DIR, 'sz_list.xlsx')
        sz_url = 'http://www.szse.cn/szseWeb/ShowReport.szse?SHOWTYPE=xlsx&CATALOGID=1110&&ENCODE=1&TABKEY=tab2'
        response = get_response(session, sz_url, timeout=3, headers=self.headers)
        open(sz_list_file, 'w').write(response.content)
        data = xlrd.open_workbook(sz_list_file)
        table = data.sheets()[0]
        table = data.sheet_by_index(0)
        nrows = table.nrows
        for i in range(nrows):
            row = table.row_values(i)
            code, name = row[0], row[1]
            name = name.replace(' ', '')
            if not Stock.objects.filter(code=code, market='sz').exists():
                stock = Stock.objects.create(
                    code=code,
                    name=name,
                    market='sz',
                    is_stock=True,
                )
            else:
                stock = Stock.objects.get(code=code)
                if stock.name != name:
                    print stock.name
                    stock.name = name
                    stock.save()


class StocksAnnouncementCrawler(AbstractBaseCrawler):
    """
    from info_collector.crawlers import StocksAnnouncementCrawler
    crawler = StocksAnnouncementCrawler()
    crawler.update_info()
    """

    def __init__(self):
        super(StocksAnnouncementCrawler, self).__init__('cninfo')

    def update_info(self):
        session = requests.Session()
        watching = Stock.objects.filter(watching=True).values_list('code', flat=True)
        sh_url = 'http://www.cninfo.com.cn/cninfo-new/disclosure/sse'
        response = get_response(session, sh_url, timeout=3, headers=self.headers)  # just for cookie
        sh_announcements_url = 'http://www.cninfo.com.cn/cninfo-new/disclosure/sse_latest'
        we_shall_stop = False
        page = 1
        save_point = None
        while page < 5 and not we_shall_stop:
            json_response = get_response(session, sh_announcements_url, timeout=3, headers=self.headers, post_data={
                'column': 'sse',
                'columnTitle': u'沪市公告',
                'pageNum': unicode(page),
                'pageSize': u'30',
                'tabName': u'latest',
                'seDate': u'请选择日期',
            })
            json_result = json_response.json()
            for item_list in json_result['classifiedAnnouncements']:
                if we_shall_stop:
                    break
                for item in item_list:
                    code = item['secCode']
                    name = item['secName']
                    title = item['announcementTitle']
                    identifier = item['adjunctUrl']
                    announcement_id = item['announcementId']
                    storage_time = item['storageTime']
                    correct_time = datetime.utcfromtimestamp(storage_time/1000)
                    time_str = correct_time.strftime('%Y-%m-%d')
                    info_url = 'http://www.cninfo.com.cn/cninfo-new/disclosure/sse/bulletin_detail/true/{}?announceTime={}'
                    info_url = info_url.format(announcement_id, time_str)
                    if code in watching or not save_point:
                        save_point = True
                        created = correct_time
                        if not Info.objects.filter(info_source=self.info_source, identifier=identifier).exists():
                            info = Info.objects.create(
                                url=info_url,
                                status=Info.NEW,
                                info_source=self.info_source,
                                title=name + ' ' + title,
                                identifier=identifier,
                                original_timestamp=created,
                                important=True,
                            )
                        else:
                            we_shall_stop = True
            page += 1
            time.sleep(2)

        sz_url = 'http://www.cninfo.com.cn/cninfo-new/disclosure/szse'
        response = get_response(session, sz_url, timeout=3, headers=self.headers)  # just for cookie
        sz_announcements_url = 'http://www.cninfo.com.cn/cninfo-new/disclosure/szse_latest'
        page = 1
        we_shall_stop = False
        save_point = None
        while page < 5 and not we_shall_stop:
            json_response = get_response(session, sz_announcements_url, timeout=3, headers=self.headers, post_data={
                'column': 'szse',
                'columnTitle': u'深市公告',
                'pageNum': unicode(page),
                'pageSize': u'30',
                'tabName': u'latest',
                'seDate': u'请选择日期',
            })
            json_result = json_response.json()
            for item_list in json_result['classifiedAnnouncements']:
                if we_shall_stop:
                    break
                for item in item_list:
                    code = item['secCode']
                    name = item['secName']
                    title = item['announcementTitle']
                    identifier = item['adjunctUrl']
                    announcement_id = item['announcementId']
                    storage_time = item['storageTime']
                    correct_time = datetime.utcfromtimestamp(storage_time / 1000)
                    time_str = correct_time.strftime('%Y-%m-%d')
                    info_url = 'http://www.cninfo.com.cn/cninfo-new/disclosure/sse/bulletin_detail/true/{}?announceTime={}'
                    info_url = info_url.format(announcement_id, time_str)
                    if code in watching or not save_point:
                        save_point = True
                        created = correct_time
                        if not Info.objects.filter(info_source=self.info_source, identifier=identifier).exists():
                            info = Info.objects.create(
                                url=info_url,
                                status=Info.NEW,
                                info_source=self.info_source,
                                title=name + ' ' + title,
                                identifier=identifier,
                                original_timestamp=created,
                                important=True,
                            )
                        else:
                            we_shall_stop = True
            page += 1
            time.sleep(2)
