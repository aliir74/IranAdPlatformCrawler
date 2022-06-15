import time
from datetime import datetime
from typing import List, Tuple
import requests as rq
from bs4 import BeautifulSoup
import logging

from ad.divar_ad import DivarAd
from crawlers.base_crawler import BaseCrawler
from constance import SCROLL_PAUSE_TIME, IFTTT_URL, IFTTT_KEY

logger = logging.getLogger(__name__)


class DivarCrawler(BaseCrawler):

    def _get_new_ads(self) -> Tuple[List[DivarAd], List[DivarAd]]:
        driver = self.driver
        driver.get(self.url)
        driver.execute_script("window.scrollTo(0, 0);")
        last_height = driver.execute_script("return document.body.scrollHeight")
        notif_new_ads = []
        notif_changed_ads = []
        retry_reach_to_end_of_page = 0
        reach_old_ads = False
        while (retry_reach_to_end_of_page < 3) and (not reach_old_ads):
            data = driver.page_source
            logger.info(f'data:\n {data}')
            ads = self._extract_ads(data)
            new_ads, changed_ads, reach_old_ads = self._save_ads(ads)
            notif_new_ads.extend(new_ads)
            notif_changed_ads.extend(changed_ads)
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                # we reached to end of the page
                retry_reach_to_end_of_page += 1
            last_height = new_height
        return notif_new_ads, notif_changed_ads

    @staticmethod
    def _extract_ads(data: str) -> List[DivarAd]:
        soup = BeautifulSoup(data, 'html.parser')
        body = soup.find('body')
        cards = body.find_all(class_='post-card-item')
        cards = list(filter(lambda x: x.find('div', class_='kt-post-card__title') is not None, cards))
        cards_data = []
        for c in cards:
            logger.info(f'card: {c}')
            title = c.find(class_='kt-post-card__title').get_text()
            price_description = c.find(class_='kt-post-card__description').get_text()
            link = c.find('a', href=True)['href']
            neighborhood = c.find('span', class_='kt-post-card__bottom-description').get_text()
            token = 'divar:'+link.split('/')[-1]
            cards_data.append(DivarAd(title, price_description, link, neighborhood, token))
        return cards_data

    def _save_ads(self, ads: List[DivarAd]) -> (List[DivarAd], List[DivarAd], bool):
        new_ads_cnt = 0
        reach_old_ads = False
        new_ads = []
        changed_ads = []
        for ad in ads:
            if self.db.is_new_ad(ad.token):
                self.db.save_ad(ad)
                new_ads_cnt += 1
                new_ads.append(ad)
            else:
                if not self.db.compare_same_token_ad_details(ad):
                    self.db.save_ad(ad)
                    new_ads_cnt += 1
                    changed_ads.append(ad)
                else:
                    reach_old_ads = True
        return new_ads, changed_ads, reach_old_ads

    def _send_notif(self, ads: List[DivarAd], changed_ad=False):
        changed_str = '  آگهی تغییر یافته  ' if changed_ad else '   '
        for ad in ads:
            # To prevent loss any ads if any error occurred
            print(f'new ad notif: {ad.link}')
            try:
                rq.post(
                    "%s/trigger/notify/with/key/%s?value1=%s&value2=%s&value3=%s" % (IFTTT_URL, IFTTT_KEY, ad.link,
                                                                                     changed_str + ad.neighborhood + ' '
                                                                                     + ad.title,
                                                                                     ad.price_description))
            except Exception:
                logger.exception(f"cannot send notif for {ad}")
                self.db.delete_ad(ad.token)
            time.sleep(1)

    def run(self):
        while True:
            logger.info(f'Starting crawl at {datetime.now()}...')
            new_ads, changed_ads = self._get_new_ads()
            logger.info(f'Got {len(new_ads)} new ads and {len(changed_ads)} changed ads!')
            logger.info('Starting sending notification to telegram group')
            # self._send_notif(new_ads)
            # self._send_notif(changed_ads, changed_ad=True)
            time.sleep(self.refresh_sleep)

