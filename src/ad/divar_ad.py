from dataclasses import dataclass

from ad.base_ad import BaseAd


@dataclass
class DivarAd(BaseAd):
    title: str
    price_description: str
    neighborhood: str
