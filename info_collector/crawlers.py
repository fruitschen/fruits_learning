# coding: utf-8

import logging
import requests
from BeautifulSoup import BeautifulSoup as BS

from django.utils import timezone

from info_collector.models import InfoSource, Info


class AbstractBaseCrawler(object):
    def __init__(self, slug):
        self.headers = { 'user-agent': 'info_collect/0.1' }
        self.info_source = InfoSource.objects.get(slug=slug)
        self.slug = slug

    def run(self):
        try:
            self.info_source.status = InfoSource.CRAWLING
            self.info_source.last_fetched = timezone.now()
            self.info_source.save()
            self.update_info()
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


class TechQQCrawler(AbstractBaseCrawler):
    """
    from info_collector.crawlers import TechQQCrawler
    crawler = TechQQCrawler()
    crawler.update_info()
    """

    def __init__(self):
        super(TechQQCrawler, self).__init__('tech_qq')

    def update_info(self):
        response = None
        retry = 0
        while not response and retry < 3:
            try:
                response = requests.get(self.info_source.url, timeout=3, headers=self.headers)
            except requests.exceptions.ConnectTimeout:
                retry += 1
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

