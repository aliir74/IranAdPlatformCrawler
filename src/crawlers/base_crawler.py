from abc import abstractmethod
from typing import List
from selenium.webdriver import Chrome

from ad.base_ad import BaseAd
from db.base_db import BaseDB


class BaseCrawler:
    def __init__(self, url: str, driver: Chrome, db: BaseDB, refresh_sleep: int = 15*60):
        self.url = url
        self.driver = driver
        self.db = db
        self.refresh_sleep = refresh_sleep

    @abstractmethod
    def run(self): ...

    @abstractmethod
    def _get_new_ads(self) -> (List[BaseAd], List[BaseAd]): ...

    @abstractmethod
    def _save_ads(self, ads: List[BaseAd]) -> (int, bool): ...

    @staticmethod
    @abstractmethod
    def _extract_ads(data: str) -> List[BaseAd]: ...

    def _send_notif(self, ads: List[BaseAd], changed_ad: bool):
        """
        It's optional to implement for getting notif on another service on each new or changed ad
        :param ads: list of new ads
        :param changed_ad: list of changed ads
        :return:
        """
