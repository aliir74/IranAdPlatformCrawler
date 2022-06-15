import os.path
import time
from datetime import datetime
from typing import List, Tuple
import requests as rq
from bs4 import BeautifulSoup
import logging

from ad.divar_ad import DivarAd
from crawlers.base_crawler import BaseCrawler
from constance import SCROLL_PAUSE_TIME, IFTTT_URL, IFTTT_KEY, IFTTT_EVENT

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
            ads = self._extract_ads(data)
            new_ads, changed_ads = self._save_ads(ads)
            notif_new_ads.extend(new_ads)
            notif_changed_ads.extend(changed_ads)
            reach_old_ads = self._reach_last_week_ads(ads)
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                # we reached to end of the page
                logger.info('Reached to end of the page')
                retry_reach_to_end_of_page += 1
            last_height = new_height
        else:
            if retry_reach_to_end_of_page == 3:
                logger.info('Reached to end of the page 3 times')
            elif reach_old_ads:
                logger.info('Reached to old ads')
        return notif_new_ads, notif_changed_ads

    @staticmethod
    def _reach_last_week_ads(ads: List[DivarAd]) -> bool:
        for ad in ads:
            if 'هفته' in ad.neighborhood:
                return True
        return False

    def _extract_ads(self, data: str) -> List[DivarAd]:
        soup = BeautifulSoup(data, 'html.parser')
        body = soup.find('body')
        cards = body.find_all(class_='post-card-item')
        cards = list(filter(lambda x: x.find(class_='kt-post-card__title') is not None, cards))
        cards_data = []
        for c in cards:
            title = self._get_element_from_dom(c.find(class_='kt-post-card__title').get_text)
            price_description = self._get_element_from_dom(c.find(class_='kt-post-card__description').get_text)
            neighborhood = self._get_element_from_dom(
                c.find('span', class_='kt-post-card__bottom-description').get_text)
            try:
                link = 'https://divar.ir' + c.find('a', href=True).get('href')
            except Exception:
                logger.exception(f"cannot get link for {title}")
                continue
            token = 'divar:' + link.split('/')[-1]
            ad = DivarAd(title=title, price_description=price_description, link=link, neighborhood=neighborhood,
                         token=token)
            cards_data.append(ad)
        return cards_data

    @staticmethod
    def _get_element_from_dom(getter_function: callable) -> str:
        try:
            return getter_function()
        except Exception:
            logger.warning('Cannot get element from dom', exc_info=True)
            return ''

    def _save_ads(self, ads: List[DivarAd]) -> (List[DivarAd], List[DivarAd]):
        new_ads_cnt = 0
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
        return new_ads, changed_ads

    def _send_notif(self, ads: List[DivarAd], changed_ad=False):
        changed_str = '  آگهی تغییر یافته  ' if changed_ad else '   '
        for ad in ads:
            url = os.path.join(IFTTT_URL, 'trigger', IFTTT_EVENT, 'with', 'key', IFTTT_KEY)
            query_params = {'value1': ad.link, 'value2': changed_str + ad.neighborhood + " " + ad.title,
                            'value3': ad.price_description}
            try:
                rq.post(url, params=query_params)
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
            self._send_notif(new_ads)
            self._send_notif(changed_ads, changed_ad=True)
            logger.info(f'Wait for next crawl {self.refresh_sleep} seconds')
            time.sleep(self.refresh_sleep)
