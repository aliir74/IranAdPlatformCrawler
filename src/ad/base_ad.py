import json
from dataclasses import dataclass


@dataclass
class BaseAd:
    link: str
    token: str

    def to_json(self) -> str:
        return json.dumps(self.__dict__)
