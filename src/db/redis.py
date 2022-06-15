import redis
from ad.base_ad import BaseAd
from constance import REDIS_HOST, REDIS_PORT
from db.base_db import BaseDB

import logging
logger = logging.getLogger(__name__)

class RedisDB(BaseDB):
    def __init__(self, db_name: int):
        self.service = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=db_name, decode_responses=True)

    def is_new_ad(self, token: str) -> bool:
        return self.service.exists(token) == 0

    def save_ad(self, ad: BaseAd):
        self.service.set(ad.token, ad.to_json())

    def delete_ad(self, token: str):
        self.service.delete(token)

    def compare_same_token_ad_details(self, new_ad: BaseAd) -> bool:
        old_ad = self.service.get(new_ad.token)
        return old_ad == new_ad.to_json()
