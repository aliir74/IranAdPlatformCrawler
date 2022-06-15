from abc import abstractmethod, ABC

from ad.base_ad import BaseAd


class BaseDB(ABC):

    @abstractmethod
    def __init__(self): ...

    @abstractmethod
    def is_new_ad(self, token: str) -> bool: ...

    @abstractmethod
    def save_ad(self, ad: BaseAd): ...

    @abstractmethod
    def delete_ad(self, token): ...

    @abstractmethod
    def compare_same_token_ad_details(self, new_ad: BaseAd) -> bool: ...
