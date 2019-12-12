from doulistspider import CookieReader, DoulistSpider

from spiderutil.connector import MongoDB
from spiderutil.path import StoreByUserName
from spiderutil.log import Log

if __name__ == '__main__':
    # 1. Save the cookies to cookie.txt and load the cookie
    cookies = CookieReader.from_local_file('./cookie.txt')

    # 2.Use MongoDB to save the checkpoint
    db = MongoDB('doulist', primary_key='id')

    # 3. Declare the spider, you need to specify:
    # the location of chromedriver.exe, the cookies,
    # the database, and the path generator
    path = StoreByUserName('./download')
    spider = DoulistSpider(driver_path='./chromedriver.exe',
                           cookies=cookies,
                           db=db,
                           path=path)

    # Create a logger to log
    logger = Log.create_logger(name='DoulistSpider', path='./doulist.log')

    # 4. Download the links, will stop if met duplicate link in the database
    for item in spider.list('<Doulist ID>'):
        logger.info('{} {}'.format(item.username, len(item.links)))
        spider.download(item)
