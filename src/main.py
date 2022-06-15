import logging
import time

from constance import DIVAR_URL
from db.redis import RedisDB
from crawlers.divar_crawler import DivarCrawler
from selenium.webdriver import Chrome, ChromeOptions
import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

if __name__ == '__main__':
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_driver = Chrome(options=chrome_options)
    db = RedisDB(db_name=0)
    crawler = DivarCrawler(url=DIVAR_URL, driver=chrome_driver, db=db)
    crawler.run()

