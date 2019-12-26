import atexit
import requestium
from typing import Union
from collections import namedtuple

from selenium.common.exceptions import NoSuchElementException

from spiderutil.connector import Database, MongoDB
from spiderutil.path import PathGenerator, StoreByUserName
from spiderutil.log import Log
from spiderutil.typing import MediaType

from .util import generate_url

Item = namedtuple('Item', ['item_id', 'username', 'links'])


class DoulistSpider:

    def __init__(self, driver_path,
                 cookies: dict,
                 db: Database = None,
                 path: Union[PathGenerator, str] = None,
                 proxies: dict = None,
                 timeout: int = 15,
                 no_window: bool = False,
                 logger=None):

        options = {
            'arguments': [
                "--headless",
                "--window-size=1920,1080"
            ]
        } if no_window else {}

        # https://chromedriver.chromium.org/downloads
        self.session = requestium.Session(webdriver_path=driver_path,
                                          browser='chrome',
                                          default_timeout=timeout,
                                          webdriver_options=options)

        for key, value in cookies.items():
            self.session.driver.ensure_add_cookie({
                'name': key,
                'value': value,
                'domain': '.douban.com'
            })
        self.session.transfer_driver_cookies_to_session()
        self.session.proxies = proxies
        self.session.headers = {
            'user-agent': self.session.driver.execute_script("return navigator.userAgent;")
        }
        self.session.default_timeout = timeout

        self.db = MongoDB('doulist', primary_key='id') if db is None else db

        if path is None:
            self.path = StoreByUserName('./download')
        elif path is str:
            self.path = StoreByUserName(path)
        else:
            self.path = path

        self.logger = Log.create_logger('DoulistSpider', './doulist.log') if logger is None else logger

        atexit.register(self.quit)

    @property
    def driver(self):
        return self.session.driver

    def list(self, number):
        url = 'https://douban.com/doulist/{}/'.format(number)
        params = {
            'sort': 'time',
            'sub_type': ''
        }
        result = []
        end = False
        self.driver.get(generate_url(url, params))
        paginator = self.driver.find_element_by_class_name('paginator')
        page_count = len(paginator.find_elements_by_tag_name('a'))

        def extract_link():
            for item in self.driver.find_elements_by_class_name('doulist-item'):
                item_id = item.get_attribute('id')
                try:
                    content = item.find_element_by_class_name('status-content')
                    a = content.find_element_by_tag_name('a')
                    username = a.text[:-4]
                    links = []
                    images = item.find_element_by_class_name('status-images')
                    for a in images.find_elements_by_tag_name('a'):
                        style = a.get_attribute('style')
                        links.append(style[style.find('https'): -3].replace('/m/', '/raw/').replace('.webp', '.jpg'))
                    yield Item(item_id, username, links)
                except NoSuchElementException:
                    self.logger.info('Content not available.')
                    continue

        page = 1
        params['start'] = 0
        while not end:
            for item in extract_link():
                if item.item_id in self.db:
                    end = True
                    break
                result.append(item)
            params['start'] += 25
            if page >= page_count:
                break
            self.driver.get(generate_url(url, params))
            page += 1

        result.reverse()
        return result

    def download(self, item: Item):
        for link in item.links:
            while True:
                try:
                    r = self.session.get(link)
                    break
                except Exception as e:
                    self.logger.error(e)
            with open(self.path.generate(user_name=item.username, media_type=MediaType.image), 'wb') as f:
                f.write(r.content)
        self.db.insert({'id': item.item_id})

    def quit(self):
        self.driver.quit()
