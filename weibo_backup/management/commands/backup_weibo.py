# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand
from django.utils import timezone
import os
import time
import selenium
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

from weibo_backup.models import Tweet


class Command(BaseCommand):
    help = u'备份微博账号内容'

    def handle(self, *args, **options):
        binary = FirefoxBinary('/usr/bin/firefox')
        driver = webdriver.Firefox(firefox_binary=binary)
        input = raw_input('login and go to the account page. Then enter anything to continue: ')

        items = driver.find_elements_by_class_name('card9')
        #  items.reverse()
        tweets_to_process = []
        for item in items:
            content = item.find_element_by_class_name('weibo-main')
            links = content.find_elements_by_tag_name('a')
            status_time = item.find_element_by_class_name('time').text
            link = None
            for a_link in links:
                if 'status' in a_link.get_attribute('href'):
                    link = a_link
                    break
            tweets_to_process.append({
                'item': item,
                'content': content,
                'status_time': status_time,
                'link': link,
            })

        js = '''
        document.querySelectorAll('footer').forEach(function(obj){obj.remove()});
        document.querySelectorAll('header').forEach(function(obj){obj.remove()});
        document.querySelectorAll('.profile-cover').forEach(function(obj){obj.remove()});
        document.querySelectorAll('.m-top-nav-wrapper').forEach(function(obj){obj.remove()});
        document.querySelectorAll('.m-top-nav').forEach(function(obj){obj.remove()});
        document.querySelectorAll('.card-list').forEach(function(obj){obj.remove()});
        document.querySelectorAll('.m-tab-bar').forEach(function(obj){obj.remove()});
        document.querySelectorAll('.card11').forEach(function(obj){obj.remove()});

        var i = 0;
        document.querySelectorAll('.card9').forEach(function(obj){
            obj.id = 'tweet_processing' + i;
            i += 1;
        })

        '''
        driver.execute_script(js)

        for index, t in enumerate(tweets_to_process):
            content = t['content']
            link = t['link']
            status_time = t['status_time']
            if not status_time[:4].isdigit():
                now = timezone.now()
                status_time = '{}-{}'.format(now.year, status_time)
            if link:
                url = link.get_attribute('href')
                status_id = url.split('/status/')[-1]
                if Tweet.objects.filter(t_id=status_id).exists():
                    # Tweet.objects.filter(t_id=status_id).update(t_time=status_time)
                    pass
                else:
                    print 'record the id and save date, id, content, later'
                    tweet = Tweet.objects.create(
                        t_id=status_id,
                        t_time=status_time,
                        finished=False
                    )
            else:
                if Tweet.objects.filter(t_time=status_time).exists():
                    tweet = Tweet.objects.filter(t_time=status_time)[0]
                else:
                    print 'Save the content and time'
                    tweet = Tweet.objects.create(
                        t_id='',
                        t_time=status_time,
                        finished=True,
                        content=content.text,
                    )
                if os.path.exists(tweet.screenshot_full):
                    pass
                else:
                    time.sleep(0.5)
                    content.location_once_scrolled_into_view
                    time.sleep(0.5)
                    content.screenshot(tweet.screenshot_full)
                    #  open(tweet.screenshot_full, 'wb').write(content.screenshot_as_png)
                    try:
                        picture_content = content.find_element_by_class_name('weibo-media')
                        picture_content.screenshot(tweet.screenshot_pictures)
                    except selenium.common.exceptions.NoSuchElementException:
                        pass

            #  we need to hide the tweet or the screenshot will be wrong.
            js = '''document.querySelectorAll('#tweet_processing%s').forEach(function(obj){
                obj.style.display='none';
            })''' % (index)
            driver.execute_script(js)

        for tweet in Tweet.objects.filter(finished=False):
            retry = 0
            while retry < 3 and not tweet.finished:
                try:
                    driver.get(tweet.status_url())
                    time.sleep(1)
                    js = '''document.querySelectorAll('.tips')[0].style.display='None'; '''
                    try:
                        driver.execute_script(js)
                    except:
                        pass
                    main_content = driver.find_element_by_class_name('weibo-main')
                    time.sleep(0.2)
                    if os.path.exists(tweet.screenshot_full):
                        pass
                    else:
                        main_content.screenshot(tweet.screenshot_full)
                        try:
                            picture_content = main_content.find_element_by_class_name('weibo-media')
                            picture_content.screenshot(tweet.screenshot_pictures)
                        except selenium.common.exceptions.NoSuchElementException:
                            pass
                    tweet.content = main_content.text
                    tweet.finished = True
                    tweet.save()
                except:
                    retry += 1

        print 1
        print 2
        print 3
        driver.quit()

