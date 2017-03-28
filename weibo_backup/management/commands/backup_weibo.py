# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand
import time
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

from weibo_backup.models import Tweet

class Command(BaseCommand):
    help = u'备份微博账号内容'


    def handle(self, *args, **options):
        binary = FirefoxBinary('/usr/bin/firefox')
        driver = webdriver.Firefox(firefox_binary=binary)
        input = raw_input('login and go to the account page. Then enter anything to continue: ')

        import pdb; pdb.set_trace()
        print len(driver.page_source)
        items = driver.find_elements_by_class_name('card9')
        items.reverse()
        for item in items:
            content = item.find_element_by_class_name('weibo-main')
            links = content.find_elements_by_tag_name('a')
            status_time = item.find_element_by_class_name('time').text
            if links:
                for link in links:
                    if 'status' in link.get_attribute('href'):
                        break
                url = link.get_attribute('href')
                status_id = url.split('/status/')[-1]
                print 'record the id and save date, id, content, later'
                if Tweet.objects.filter(t_id=status_id).exists():
                    continue
                tweet = Tweet.objects.create(
                    t_id=status_id,
                    t_time=status_time,
                    finished=False
                )
            else:
                print 'Save the content and time'
                if Tweet.objects.filter(t_time=status_time).exists():
                    continue
                tweet = Tweet.objects.create(
                    t_id=status_id,
                    t_time=status_time,
                    finished=True,
                    content=content.text,
                )
                content.screenshot(tweet.screenshot_full)
                try:
                    picture_content = content.find_element_by_class_name('weibo-media')
                    picture_content.screenshot(tweet.screenshot_pictures)
                except selenium.common.exceptions.NoSuchElementException:
                    pass


        for tweet in Tweet.objects.filter(finished=False):
            retry = 0
            while retry < 3 and not tweet.finished:
                try:
                    driver.get(tweet.status_url())
                    time.sleep(3)
                    js = '''document.querySelectorAll('.tips')[0].style.display='None'; '''
                    try:
                        driver.execute_script(js)
                    except:
                        pass
                    main_content = driver.find_element_by_class_name('weibo-main')
                    main_content.screenshot(tweet.screenshot_full)
                    try:
                        picture_content = main_content.find_element_by_class_name('weibo-media')
                    except selenium.common.exceptions.NoSuchElementException:
                        pass
                    picture_content.screenshot(tweet.screenshot_pictures)
                    tweet.content = main_content.text
                    tweet.finished = True
                    tweet.save()
                except:
                    import pdb; pdb.set_trace()
                    retry += 1

        print 1
        print 2
        print 3
        driver.quit()



'''
[
 'add_cookie',
 'application_cache',
 'back',
 'binary',
 'capabilities',
 'close',
 'command_executor',
 'context',
 'create_web_element',
 'current_url',
 'current_window_handle',
 'delete_all_cookies',
 'delete_cookie',
 'desired_capabilities',
 'error_handler',
 'execute',
 'execute_async_script',
 'execute_script',
 'file_detector',
 'file_detector_context',
 'find_element',
 'find_element_by_class_name',
 'find_element_by_css_selector',
 'find_element_by_id',
 'find_element_by_link_text',
 'find_element_by_name',
 'find_element_by_partial_link_text',
 'find_element_by_tag_name',
 'find_element_by_xpath',
 'find_elements',
 'find_elements_by_class_name',
 'find_elements_by_css_selector',
 'find_elements_by_id',
 'find_elements_by_link_text',
 'find_elements_by_name',
 'find_elements_by_partial_link_text',
 'find_elements_by_tag_name',
 'find_elements_by_xpath',
 'firefox_profile',
 'forward',
 'get',
 'get_cookie',
 'get_cookies',
 'get_log',
 'get_screenshot_as_base64',
 'get_screenshot_as_file',
 'get_screenshot_as_png',
 'get_window_position',
 'get_window_size',
 'implicitly_wait',
 'log_types',
 'maximize_window',
 'mobile',
 'name',
 'orientation',
 'page_source',
 'profile',
 'quit',
 'refresh',
 'save_screenshot',
 'service',
 'session_id',
 'set_context',
 'set_page_load_timeout',
 'set_script_timeout',
 'set_window_position',
 'set_window_size',
 'start_client',
 'start_session',
 'stop_client',
 'switch_to',
 'switch_to_active_element',
 'switch_to_alert',
 'switch_to_default_content',
 'switch_to_frame',
 'switch_to_window',
 'title',
 'w3c',
 'window_handles']

'''