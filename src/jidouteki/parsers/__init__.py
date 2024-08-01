from abc import ABC, abstractmethod
from jidouteki.spec import DictSpec
from jidouteki.spec.meta import Meta
from typing import Literal

class Parser(DictSpec, ABC):
    type: str = Meta.REQUIRED
    output: Literal["multiple", "single"] = "multiple"
    
    @abstractmethod
    def parse(self, *args, **kwargs):
        pass
    
from .enumerate import EnumerateParser
from .network import NetworkParser
from .live import LiveParser
from .request import RequestParser
from .list import ParserList